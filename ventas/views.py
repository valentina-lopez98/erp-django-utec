"""Vistas de la app ventas — W07/W08 + PDF W12.

Lectura: VentaListView y VentaDetailView.
Escritura: crear_venta (función) y VentaDeleteView.
PDF: venta_pdf (xhtml2pdf, sin Docker).
"""
import io
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
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