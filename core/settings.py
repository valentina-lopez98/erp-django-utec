# core/settings.py
from datetime import timedelta
from celery.schedules import crontab
import dj_database_url
from datetime import timedelta   # ← necesario para CELERY_BEAT_SCHEDULE
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Variables de entorno ──────────────────────────────────────────────────
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY    = env('SECRET_KEY', default='dev-key-insegura-solo-para-desarrollo')
DEBUG         = env('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Render define RENDER_EXTERNAL_HOSTNAME automaticamente (tu-app.onrender.com)
RENDER_HOST = env('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_HOST:
    ALLOWED_HOSTS.append(RENDER_HOST)

# core/settings.py — actualizar INSTALLED_APPS (terceros):
# core/settings.py — actualizar INSTALLED_APPS:
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Terceros
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',              # ← nuevo (nombre de app es django_filters)
    'whitenoise.runserver_nostatic',
    # Apps del ERP
    'clientes',
    'proveedores',
    'productos',
    'ventas',
    'reportes',
    'configuracion',
    'catalogo',                    # ← nuevo
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # al final
]

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# ── Templates ─────────────────────────────────────────────────────────────
# core/settings.py — actualizar TEMPLATES[0]['OPTIONS']['context_processors']:
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Context processor del carrito — W13
                'catalogo.context_processors.carrito_info',
            ],
        },
    },
]


# ── Base de datos ─────────────────────────────────────────────────────────
DATABASE_URL = env('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Validadores de contraseña ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internacionalización ──────────────────────────────────────────────────
LANGUAGE_CODE = 'es-mx'
TIME_ZONE     = 'America/Mexico_City'
USE_I18N      = True
USE_TZ        = True

# ── Archivos estáticos ────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']   # crea esta carpeta: static/

# STATICFILES_STORAGE fue eliminado en Django 5.1; ahora se usa STORAGES
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

# ── Archivos media ────────────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Autenticación ─────────────────────────────────────────────────────────
LOGIN_URL           = '/accounts/login/'
LOGIN_REDIRECT_URL  = '/productos/'
LOGOUT_REDIRECT_URL = '/'

# core/settings.py — reemplazar la configuración REST_FRAMEWORK de W01:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',   # para el navegador
        'rest_framework.authentication.TokenAuthentication',     # para clientes externos
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'anymail',    # ← agregar

# ── JAZZMIN ───────────────────────────────────────────────────────────────
JAZZMIN_SETTINGS = {
    'site_title':   'ERP Django',
    'site_header':  'ERP UTEC Celaya',
    'site_brand':   '📦 ERP Django',
    'welcome_sign': 'Bienvenido al Sistema ERP · UTEC Celaya',
    'copyright':    'MC. Román Fernando López González · UTEC Celaya',

    'site_icon': None,
    'site_logo': None,

    'search_model': ['clientes.Cliente', 'productos.Producto'],

    'topmenu_links': [
        {'name': 'Inicio ERP', 'url': '/', 'new_window': False},
        {'name': 'Productos',  'url': '/productos/'},
        {'name': 'Clientes',   'url': '/clientes/'},
        {'name': 'Ventas',     'url': '/ventas/'},
    ],

    'usermenu_links': [
        {'name': 'Ver ERP', 'url': '/', 'new_window': False},
    ],

    'order_with_respect_to': [
        'clientes', 'proveedores', 'productos',
        'ventas', 'configuracion', 'auth',
    ],

    'icons': {
        'auth':                           'fas fa-users-cog',
        'auth.user':                      'fas fa-user',
        'auth.Group':                     'fas fa-users',
        'clientes.Cliente':               'fas fa-user-tie',
        'proveedores.Proveedor':          'fas fa-truck',
        'productos.Categoria':            'fas fa-tags',
        'productos.Producto':             'fas fa-box',
        'ventas.Venta':                   'fas fa-file-invoice-dollar',
        'ventas.DetalleVenta':            'fas fa-list',
        'ventas.Pedido':                  'fas fa-shopping-cart',
        'configuracion.ConfiguracionERP': 'fas fa-cogs',
    },
    'default_icon_parents':  'fas fa-folder',
    'default_icon_children': 'fas fa-circle',

    'related_modal_active': True,
    'custom_css':           'erp_custom.css',   # static/erp_custom.css (crear aunque esté vacío)
    'show_sidebar':         True,
    'navigation_expanded':  True,
    'hide_apps':            [],
    'hide_models':          [],

    'changeform_format': 'horizontal_tabs',
    'language_chooser':  False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text':         False,
    'footer_small_text':         False,
    'body_small_text':           False,
    'brand_small_text':          False,
    'brand_colour':              'navbar-navy',
    'accent':                    'accent-navy',
    'navbar':                    'navbar-navy navbar-dark',
    'no_navbar_border':          False,
    'navbar_fixed':              True,
    'layout_boxed':              False,
    'footer_fixed':              False,
    'sidebar_fixed':             True,
    'sidebar':                   'sidebar-dark-navy',
    'sidebar_nav_small_text':    False,
    'sidebar_disable_expand':    False,
    'sidebar_nav_child_indent':  True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style':  False,
    'sidebar_nav_flat_style':    False,
    'theme':                     'default',
    'default_theme_mode':        'auto',

    'button_classes': {
        'primary':   'btn-primary',
        'secondary': 'btn-secondary',
        'info':      'btn-info',
        'warning':   'btn-warning',
        'danger':    'btn-danger',
        'success':   'btn-success',
    },
}

# core/settings.py — agregar al final (antes de JAZZMIN_SETTINGS):

# ── STRIPE (Pasarela de pago) ──────────────────────────────────────────────
STRIPE_SECRET_KEY     = env('STRIPE_SECRET_KEY',     default='sk_test_placeholder')
STRIPE_PUBLISHABLE_KEY = env('STRIPE_PUBLISHABLE_KEY', default='pk_test_placeholder')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='whsec_placeholder')

# ── DJANGO SITES (requerido por allauth) ──────────────────────────────────
SITE_ID = 1

# ── AUTHENTICATION BACKENDS ───────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# ── ALLAUTH (compatible con django-allauth 0.63.x) ────────────────────────
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED     = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_LOGOUT_ON_GET      = True
ACCOUNT_SESSION_REMEMBER   = True

# ── Produccion (Render): proxy HTTPS y CSRF ───────────────────────────────
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS    = ['https://*.onrender.com']

# ── CELERY — Cola de tareas asíncronas (W16) ──────────────────────────────
# REDIS_URL definida (Render → Key Value):
#     las tareas se encolan en Redis y las procesa el worker.
# REDIS_URL vacía (laboratorio sin Docker / tests):
#     modo EAGER → .delay() ejecuta la tarea en el mismo proceso,
#     sin broker ni worker. El código de las vistas no cambia.
REDIS_URL = env('REDIS_URL', default='')

if REDIS_URL:
    # Broker: Redis almacena los mensajes de las tareas pendientes
    CELERY_BROKER_URL     = REDIS_URL
    # Backend: Redis almacena los resultados de las tareas
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER = False
else:
    CELERY_BROKER_URL        = 'memory://'
    CELERY_RESULT_BACKEND    = 'cache+memory://'
    CELERY_TASK_ALWAYS_EAGER = True

# Los resultados caducan en 1 hora (el Key Value gratuito tiene 25 MB)
CELERY_RESULT_EXPIRES = 3600

# Formato de serialización (JSON es seguro y portable)
CELERY_ACCEPT_CONTENT    = ['json']
CELERY_TASK_SERIALIZER   = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Zona horaria (heredar de Django)
CELERY_TIMEZONE = TIME_ZONE   # 'America/Mexico_City'

# Reintentos automáticos ante fallos de conexión al broker
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Tiempo máximo que puede correr una tarea antes de ser terminada (segundos)
# NOTA: con --pool=solo (worker embebido en Render) estos límites NO se aplican;
# solo funcionan con el pool prefork (Background Worker / docker-compose).
CELERY_TASK_SOFT_TIME_LIMIT = 300   # 5 minutos
CELERY_TASK_TIME_LIMIT       = 360  # 6 minutos (hard limit)

# Cola por defecto de las tareas (el worker la consume con --queues=erp_django)
CELERY_TASK_DEFAULT_QUEUE = 'erp_django'

# En modo EAGER, las excepciones de la tarea se propagan (útil en tests)
CELERY_TASK_EAGER_PROPAGATES = True

# core/settings.py — configuración de correo electrónico

# ── CORREO ELECTRÓNICO ────────────────────────────────────────────────────
# En desarrollo: usar el backend de consola (imprime en terminal)
# En producción: anymail con SendGrid
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# Dirección del remitente visible en los correos
# (en producción debe ser el remitente verificado en SendGrid)
DEFAULT_FROM_EMAIL = env(
    'DEFAULT_FROM_EMAIL',
    default='ERP Django <noreply@erp-django.com>'
)

# Destinatario de las alertas de stock bajo.
# Variable propia: NO se usa ADMINS porque Django enviaría por correo
# los errores 500 de producción a esa dirección.
ALERTAS_ADMIN_EMAIL = env('ADMIN_EMAIL', default='admin@erp-django.com')

# URL pública del sitio (para los enlaces de los correos)
# En Render: https://erp-django-utec.onrender.com
SITE_URL = env('SITE_URL', default='http://127.0.0.1:8000')

# Configuración de django-anymail (SendGrid)
SENDGRID_API_KEY = env('SENDGRID_API_KEY', default='')
ANYMAIL = {
    'SENDGRID_API_KEY': SENDGRID_API_KEY,
}

# Hora del reporte diario (hora de México), configurable sin tocar código:
#   Render → Environment → REPORTE_DIARIO_HORA=10:00
# Default 21:00: el reporte resume el día en curso, así que va al cierre.
REPORTE_DIARIO_HORA = env('REPORTE_DIARIO_HORA', default='21:00')
try:
    _rep_h, _rep_m = (int(x) for x in REPORTE_DIARIO_HORA.split(':'))
    if not (0 <= _rep_h <= 23 and 0 <= _rep_m <= 59):
        raise ValueError('hora fuera de rango')
except ValueError:
    _rep_h, _rep_m = 21, 0
    REPORTE_DIARIO_HORA = '21:00'   # el pie del correo muestra la hora real

CELERY_BEAT_SCHEDULE = {

    # Verificar stock bajo cada hora
    'verificar-stock-bajo-cada-hora': {
        'task':     'ventas.verificar_stock_bajo',
        'schedule': timedelta(hours=1),
        'args':     (5,),   # umbral = 5 unidades
        'options':  {'queue': 'erp_django'},
    },

    # Reporte de ventas diario (default 21:00, cierre del día, hora México)
    'reporte-ventas-diario': {
        'task':     'ventas.reporte_ventas_diario',
        'schedule': crontab(hour=_rep_h, minute=_rep_m),
        'options':  {'queue': 'erp_django'},
    },

}

# Beat usa la zona horaria de Celery (no UTC). Normalmente ya existe en el
# bloque CELERY_* de W16; si no está, agregarla:
CELERY_TIMEZONE = TIME_ZONE   # 'America/Mexico_City'