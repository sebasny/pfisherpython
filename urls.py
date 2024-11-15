from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sistema_pedidos.urls')),  # Incluye las URLs de la app
]
