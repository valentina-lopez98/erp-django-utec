# productos/urls.py
"""URLs de la app productos — W07 (Lista + Detalle)."""

from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # Inicio y listado de productos
    path(
        '',
        views.ProductoListView.as_view(),
        name='inicio',
    ),
    path(
        '',
        views.ProductoListView.as_view(),
        name='lista',
    ),

    # Detalle de producto
    path(
        '<int:producto_id>/',
        views.ProductoDetailView.as_view(),
        name='detalle',
    ),

    # Escritura (W08) — pendientes de implementar
    # path('nuevo/', views.ProductoCreateView.as_view(), name='crear'),
    # path('<int:producto_id>/editar/', views.ProductoUpdateView.as_view(), name='editar'),
    # path('<int:producto_id>/eliminar/', views.ProductoDeleteView.as_view(), name='eliminar'),
]
