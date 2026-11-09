import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'REPORT_SERVICE_SECRET_KEY',
    'report-service-insecure-key-soa-lab5-p1#9@w^9404!'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'reports.apps.ReportsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'report_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'report_project.wsgi.application'
ASGI_APPLICATION = 'report_project.asgi.application'


# Cơ sở dữ liệu riêng biệt cho Reporting Service (Tuân thủ nguyên tắc kiến trúc SOA)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'reports_db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Cấu hình Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Cấu hình drf-spectacular & Swagger UI
SPECTACULAR_SETTINGS = {
    'TITLE': 'Reporting Service (SOA - Bài Thực Hành Số 5)',
    'DESCRIPTION': (
        'Dịch vụ báo cáo hoạt động độc lập trên cổng 8003 và cơ sở dữ liệu riêng (reports_db.sqlite3).\n'
        '- Thống kê số lượng hàng tồn, hàng bán được, doanh thu, chi phí, lợi nhuận theo sản phẩm và đơn hàng.\n'
        '- Xác thực người dùng thông qua Auth Service đã xây dựng ở Bài thực hành số 2 (cổng 8000).\n'
        '- Tương tác liên dịch vụ (Inter-Service) lấy dữ liệu từ Product Service (cổng 8001) và Order Service (cổng 8002).'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    'APPEND_COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
                'description': 'Nhập token JWT lấy được từ Auth Service (POST http://localhost:8000/login).'
            }
        }
    }
}

# Cấu hình giao tiếp SOA tới Auth Service (Bài Thực Hành Số 2)
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://127.0.0.1:8000/auth')
AUTH_SERVICE_TIMEOUT = int(os.environ.get('AUTH_SERVICE_TIMEOUT', '5'))

# Cấu hình giao tiếp SOA tới Product Service (Bài Thực Hành Số 3)
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://127.0.0.1:8001/products')
PRODUCT_SERVICE_TIMEOUT = int(os.environ.get('PRODUCT_SERVICE_TIMEOUT', '5'))

# Cấu hình giao tiếp SOA tới Order Service (Bài Thực Hành Số 4)
ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://127.0.0.1:8002/orders')
ORDER_SERVICE_TIMEOUT = int(os.environ.get('ORDER_SERVICE_TIMEOUT', '5'))

# Khóa bí mật dùng để giải mã JWT trong chế độ fallback hoặc offline unit test
AUTH_SECRET_KEY = os.environ.get(
    'AUTH_SECRET_KEY',
    'django-insecure-e3x-!ks+i%e@c#82%4zcxv1vb#p)-0^i^1cjgxv)6*p65n0*1%'
)

