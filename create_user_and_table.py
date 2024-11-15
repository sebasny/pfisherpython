import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'patagonia_fisher.settings')
django.setup()

from django.contrib.auth.models import User
from sistema_pedidos.models import Mesa

# Crear usuario
user = User.objects.create_user(username='mesa3', password='adminfisher')
print("Usuario creado con ID:", user.id)

# Crear mesa
mesa = Mesa.objects.create(numero=3, usuario=user)
print("Mesa creada con ID:", mesa.id)
