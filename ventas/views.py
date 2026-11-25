"""Vistas de la app ventas — W07/W08 + PDF W12.

Lectura: VentaListView y VentaDetailView.
Escritura: crear_venta (función) y VentaDeleteView.
PDF: venta_pdf (xhtml2pdf, sin Docker).
Reporte: enviar_reporte_ventas (HTML + CSV por correo).
"""
import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, DetailView, ListView
from xhtml2pdf import pisa

from configuracion.models import ConfiguracionERP
from .forms import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta, Pedido


class VentaListView(ListView):
    """Lista paginada de ventas en orden cronológico inverso."""

    model               = Venta
    template_name       = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by         = 20

    def get_queryset(self):
        """Pre-carga cliente para evitar N+1 en la tabla de ventas."""
        return (
            Venta.objects
            .select_related('cliente')
            .order_by('-fecha')
        )


class VentaDetailView(DetailView):
    """Detalle de una venta."""

    model               = Venta
    template_name       = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg        = 'venta_id'   # la URL usa <int:venta_id>

    def get_queryset(self):
        return Venta.objects.select_related('cliente')


@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea un encabezado de venta con una línea de detalle.

    GET  → muestra los dos formularios vacíos.
    POST → valida ambos, guarda si correctos, muestra errores si no.
    """
    venta_form   = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta         = venta_form.save()
            detalle       = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(
                request,
                f'Venta #{venta.pk} registrada. '
                f'Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form':   venta_form,
        'detalle_form': detalle_form,
    })


class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirmación y borrado de una venta (requiere permiso)."""

    model               = Venta
    template_name       = 'ventas/eliminar.html'
    pk_url_kwarg        = 'venta_id'
    success_url         = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'

    def form_valid(self, form):
        pk       = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response


@login_required
def venta_pdf(request, venta_id: int):
    """Genera y descarga la factura en PDF usando xhtml2pdf sin Docker."""
    venta = get_object_or_404(
        Venta.objects
        .select_related('cliente')
        .prefetch_related('detalles__producto'),
        pk=venta_id
    )
    config = ConfiguracionERP.get_instance()
    context = {
        'venta': venta,
        'config': config,
        'hoy': date.today(),
    }

    # Renderizar el HTML
    html_string = render_to_string('ventas/factura_pdf.html', context, request=request)

    # Preparar la respuesta HTTP tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{venta.pk:05d}.pdf"'

    # Convertir HTML a PDF en memoria
    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_string, dest=buffer)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    response.write(buffer.getvalue())
    return response


@login_required
@require_POST
def enviar_reporte_ventas(request):
    """Reporte de los últimos 30 días: ventas internas + pedidos pagados de la tienda."""
    destinatario = request.user.email or getattr(settings, 'ADMIN_EMAIL', '')
    if not destinatario:
        messages.error(request, 'Tu usuario no tiene correo configurado.')
        return redirect('ventas:lista')

    hoy = timezone.localdate()
    desde = hoy - timedelta(days=30)

    # Fuente 1: ventas internas del ERP
    ventas = list(
        Venta.objects
        .select_related('cliente')
        .prefetch_related('detalles')
        .filter(fecha__date__gte=desde)
    )
    # Fuente 2: compras pagadas en la tienda en línea
    pedidos = list(
        Pedido.objects
        .select_related('cliente')
        .filter(estado='pagado', fecha_pedido__date__gte=desde)
    )

    movimientos = []
    for v in ventas:
        fecha_v = timezone.localtime(v.fecha) if timezone.is_aware(v.fecha) else v.fecha
        movimientos.append({
            'fecha': fecha_v,
            'pk': f'#{v.pk}',
            'cliente': str(v.cliente) if v.cliente else '',
            'total': v.total,
        })
    for p in pedidos:
        fecha_p = timezone.localtime(p.fecha_pedido) if timezone.is_aware(p.fecha_pedido) else p.fecha_pedido
        movimientos.append({
            'fecha': fecha_p,
            'pk': p.numero_pedido,
            'cliente': str(p.cliente) if p.cliente else '',
            'total': p.total_pagado,
        })

    movimientos.sort(key=lambda m: m['fecha'])

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Referencia', 'Fecha', 'Cliente', 'Total'])

    filas = []
    total_general = Decimal('0')
    for m in movimientos:
        total_general += m['total']
        fecha_txt = m['fecha'].strftime('%Y-%m-%d')
        writer.writerow([m['pk'], fecha_txt, m['cliente'], f"{m['total']:.2f}"])
        filas.append({
            'pk': m['pk'],
            'fecha': fecha_txt,
            'cliente': m['cliente'],
            'total': m['total'],
        })

    writer.writerow([])
    writer.writerow(['', '', 'TOTAL', f'{total_general:.2f}'])
    contenido = buffer.getvalue().encode('utf-8-sig')

    contexto = {
        'filas': filas,
        'cantidad': len(movimientos),
        'total_general': total_general,
        'desde': desde,
        'hoy': hoy,
    }
    html_body = render_to_string('emails/reporte_ventas_manual.html', contexto)
    texto_plano = render_to_string('emails/reporte_ventas_manual.txt', contexto)

    correo = EmailMultiAlternatives(
        subject=f'Reporte de ventas - {hoy:%Y-%m-%d}',
        body=texto_plano,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinatario],
    )
    correo.attach_alternative(html_body, 'text/html')
    correo.attach(f'reporte_ventas_{hoy:%Y%m%d}.csv', contenido, 'application/octet-stream')

    try:
        correo.send()
        messages.success(request, f'Reporte enviado a {destinatario}.')
    except Exception as exc:
        messages.error(request, f'No se pudo enviar el reporte: {exc}')

    return redirect('ventas:lista')