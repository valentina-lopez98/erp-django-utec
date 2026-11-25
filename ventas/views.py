"""Vistas de la app ventas — W07/W08 + PDF W12.

Lectura: VentaListView y VentaDetailView.
Escritura: crear_venta (función) y VentaDeleteView.
PDF: venta_pdf (xhtml2pdf, sin Docker).
Reporte: enviar_reporte_ventas (CSV por correo).
"""
import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMessage
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
from .models import DetalleVenta, Venta


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
    """Genera un CSV con las ventas de los últimos 30 días y lo envía por correo."""
    destinatario = request.user.email or getattr(settings, 'ADMIN_EMAIL', '')
    if not destinatario:
        messages.error(request, 'Tu usuario no tiene correo configurado.')
        return redirect('ventas:lista')

    hoy = timezone.localdate()
    desde = hoy - timedelta(days=30)

    # fecha__date evita el aviso de datetime ingenuo al comparar con una fecha
    ventas = list(
        Venta.objects
        .select_related('cliente')
        .prefetch_related('detalles')
        .filter(fecha__date__gte=desde)
        .order_by('fecha')
    )

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['Venta', 'Fecha', 'Cliente', 'Total'])

    total_general = Decimal('0')
    for v in ventas:
        total_venta = v.total  # propiedad calculada en el modelo
        total_general += total_venta

        fecha_v = v.fecha
        if timezone.is_aware(fecha_v):
            fecha_v = timezone.localtime(fecha_v)

        writer.writerow([
            v.pk,
            fecha_v.strftime('%Y-%m-%d'),
            str(v.cliente) if v.cliente else '',
            f'{total_venta:.2f}',
        ])

    writer.writerow([])
    writer.writerow(['', '', 'TOTAL', f'{total_general:.2f}'])

    # utf-8-sig para que Excel muestre bien acentos y la ñ
    contenido = buffer.getvalue().encode('utf-8-sig')

    correo = EmailMessage(
        subject=f'Reporte de ventas - {hoy:%Y-%m-%d}',
        body=(
            f'Adjunto el reporte de ventas de los últimos 30 días.\n'
            f'Ventas: {len(ventas)}\n'
            f'Total: ${total_general:.2f}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinatario],
    )
    correo.attach(f'reporte_ventas_{hoy:%Y%m%d}.csv', contenido, 'text/csv')

    try:
        correo.send()
        messages.success(request, f'Reporte enviado a {destinatario}.')
    except Exception as exc:
        messages.error(request, f'No se pudo enviar el reporte: {exc}')

    return redirect('ventas:lista')