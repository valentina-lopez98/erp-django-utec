from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

APPS_ERP = [
    'clientes', 'proveedores', 'productos',
    'ventas', 'reportes', 'configuracion',
]

# Gerente recibe todos los permisos; el resto, una lista de codenames.
# 'Almac\u00e9n' = Almacén (con tilde, como lo espera el test).
GRUPOS = {
    'Gerente': 'TODOS',
    'Vendedor': [
        'view_cliente', 'add_cliente',
        'view_producto',
        'view_venta', 'add_venta', 'add_detalleventa',
    ],
    'Almac\u00e9n': [
        'view_producto', 'add_producto', 'change_producto',
        'view_categoria', 'add_categoria', 'change_categoria',
        'view_proveedor',
    ],
}

# Grupos de una version anterior de este command
GRUPOS_OBSOLETOS = ['Administrador', 'Almacen', 'Consulta']


class Command(BaseCommand):
    help = 'Crea los grupos de acceso del ERP (Gerente, Vendedor, Almacen)'

    def handle(self, *args, **options):
        self.stdout.write('Configurando grupos de acceso del ERP...\n')

        Group.objects.filter(name__in=GRUPOS_OBSOLETOS).delete()

        for nombre, config in GRUPOS.items():
            grupo, creado = Group.objects.get_or_create(name=nombre)

            if config == 'TODOS':
                permisos = Permission.objects.filter(
                    content_type__app_label__in=APPS_ERP
                )
            else:
                permisos = Permission.objects.filter(
                    content_type__app_label__in=APPS_ERP,
                    codename__in=config,
                )

            grupo.permissions.set(permisos)
            estado = 'creado' if creado else 'actualizado'
            self.stdout.write(self.style.SUCCESS(
                f'   OK {nombre} - {permisos.count()} permisos asignados ({estado})'
            ))

        self.stdout.write(self.style.SUCCESS('\nGrupos configurados exitosamente.'))
        self.stdout.write('Asigna usuarios desde /admin/ -> Usuarios -> Grupos.')
