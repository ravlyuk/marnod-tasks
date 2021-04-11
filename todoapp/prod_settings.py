import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get("SECRET_KEY", "4%w^0ig86f1l^rп2rn3-e8gk9bjn0j9ag(v!6x-*wde7m!")

DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '35.178.235.111']

STATIC_DIR = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [STATIC_DIR]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# https://youtu.be/mp4rwP7Ny_A?t=5557
