from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render
# models.py

#Modelo Mesa    
class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)  # Número de la mesa, debe ser único
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Relación con usuario
    
    def __str__(self):
        return f"Mesa {self.numero}"
    
#Modelo Pedido    
class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=[('no tomado', 'No tomado'), ('en preparacion', 'En preparación'), ('servido', 'Servido')], default='no tomado')
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Asegúrate de definir el campo total aquí
    fecha = models.DateTimeField(auto_now_add=True)

#Modelo Producto
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField()  # Cambiado a IntegerField
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('bebidas', 'Bebidas'),
            ('postres', 'Postres'),
            ('platos', 'Platos')
        ]
    )
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return self.nombre


#Modelo DetallePedido
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.IntegerField() 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}"
    
    
