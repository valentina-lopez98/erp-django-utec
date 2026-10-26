
# core/views.py
"""Vistas principales del proyecto ERP — W02."""

from django.shortcuts import render
from django.urls import reverse, NoReverseMatch


def bienvenida(request):
    """Página de inicio del ERP con tarjetas de módulos."""

    modulos_config = [
        {
            'nombre': 'Productos',
            'icono': '📦',
            'ruta': 'productos:inicio',
            'descripcion': 'Inventario, precios y stock',
        },
        {
            'nombre': 'Clientes',
            'icono': '👥',
            'ruta': 'clientes:inicio',
            'descripcion': 'Cartera y gestión de clientes',
        },
        {
            'nombre': 'Proveedores',
            'icono': '🏭',
            'ruta': 'proveedores:inicio',
            'descripcion': 'Red de proveedores',
        },
        {
            'nombre': 'Ventas',
            'icono': '💰',
            'ruta': 'ventas:inicio',
            'descripcion': 'Pedidos, facturas y cobros',
        },
        {
            'nombre': 'Reportes',
            'icono': '📊',
            'ruta': 'reportes:inicio',
            'descripcion': 'Dashboard y analítica',
        },
        {
            'nombre': 'Admin',
            'icono': '⚙️',
            'url': '/admin/',
            'descripcion': 'Panel de administración Django',
        },
    ]

    modulos = []

    for modulo in modulos_config:
        modulo = modulo.copy()

        if 'ruta' in modulo:
            try:
                modulo['url'] = reverse(modulo['ruta'])
            except NoReverseMatch:
                # Evita que una ruta inexistente provoque un error 500.
                modulo['url'] = '#'
            del modulo['ruta']

        modulos.append(modulo)

    return render(request, 'bienvenida.html', {'modulos': modulos})
