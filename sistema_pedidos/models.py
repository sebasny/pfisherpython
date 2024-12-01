from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import render
class Mesa(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.PositiveIntegerField(unique=True)  # Número único para cada mesa
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mesa"
    )  
    contraseña = models.CharField(max_length=128, default="default_password")

#Modelo Pedido
class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    estado = models.CharField(
        max_length=20,
        choices=[('no tomado', 'No tomado'),
                 ('en preparacion', 'En preparación'),
                 ('servido', 'Servido')],
        default='no tomado'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    ESTADO_OPCIONES = [
        ('no tomado', 'No tomado'),
        ('en preparacion', 'En preparación'),
        ('servido', 'Servido'),
    ]

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.id}"
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


