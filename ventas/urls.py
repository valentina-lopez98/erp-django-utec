# ventas/urls.py
"""URLs de la app ventas — W07."""

from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Inicio y listado de ventas
    path(
        '',
        views.VentaListView.as_view(),
        name='inicio',
    ),
    path(
        '',
        views.VentaListView.as_view(),
        name='lista',
    ),

    # Detalle de venta
    path(
        '<int:venta_id>/',
        views.VentaDetailView.as_view(),
        name='detalle',
    ),

    # Escritura — pendientes de implementar
    # path('nueva/', views.crear_venta, name='crear'),
    # path('<int:venta_id>/eliminar/', views.VentaDeleteView.as_view(), name='eliminar'),
]
