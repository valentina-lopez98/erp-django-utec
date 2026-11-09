import io
from datetime import date
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa

from ventas.models import Venta
from configuracion.models import ConfiguracionERP


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