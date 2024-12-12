# from django.db import models
# from django.contrib.auth.models import User
# from django.shortcuts import render
# # models.py

# #Modelo Mesa
# class Mesa(models.Model):
#     numero = models.PositiveIntegerField(unique=True)  # Número de la mesa, debe ser único
#     usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Relación con usuario

#     def __str__(self):
#         return f"Mesa {self.numero}"

# #Modelo Pedido
# class Pedido(models.Model):
#     mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
#     estado = models.CharField(max_length=20, choices=[('no tomado', 'No tomado'), ('en preparacion', 'En preparación'), ('servido', 'Servido')], default='no tomado')
#     total = models.DecimalField(max_digits=10, decimal_places=2)  # Asegúrate de definir el campo total aquí
#     fecha = models.DateTimeField(auto_now_add=True)

# #Modelo Producto
# class Producto(models.Model):
#     nombre = models.CharField(max_length=100)
#     descripcion = models.TextField(blank=True, null=True)
#     precio = models.IntegerField()  # Cambiado a IntegerField
#     categoria = models.CharField(
#         max_length=50,
#         choices=[
#             ('bebidas', 'Bebidas'),
#             ('postres', 'Postres'),
#             ('platos', 'Platos')
#         ]
#     )
#     stock = models.PositiveIntegerField(default=0)
#     imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

#     def __str__(self):
#         return self.nombre


# #Modelo DetallePedido
# class DetallePedido(models.Model):
#     pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
#     producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
#     cantidad = models.PositiveIntegerField()
#     precio = models.IntegerField()

#     def __str__(self):
#         return f"{self.cantidad} x {self.producto.nombre} en Pedido {self.pedido.id}"

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
    estado = models.CharField(
        max_length=20,
        choices=[('no tomado', 'No tomado'),
                 ('en preparacion', 'En preparación'),
                 ('servido', 'Servido')],
        default='no tomado'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    eliminado = models.BooleanField(default=False)  # Nuevo campo para marcar como eliminado
    en_historial = models.BooleanField(default=False)
    stock_actualizado = models.BooleanField(default=False)
    


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
    pedido = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Nueva columna para almacenar el total

    def calcular_total(self):
        """Calcula el total de este detalle como cantidad * precio."""
        self.total = self.cantidad * self.precio

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para calcular el total automáticamente antes de guardar."""
        self.calcular_total()  # Calcula el total antes de guardar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad}) - Total: ${self.total}"

