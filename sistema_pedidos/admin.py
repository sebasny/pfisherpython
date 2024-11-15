from django.contrib import admin
from .models import Producto, Mesa, Pedido, DetallePedido
from django.db import models
from django.contrib.auth.models import User

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0  # Número de formularios vacíos para agregar

class PedidoAdmin(admin.ModelAdmin):
    inlines = [DetallePedidoInline]
    list_display = ('id', 'get_mesa_numero', 'get_detalle_pedido', 'fecha')  # Asegúrate de incluir los campos que desees mostrar

    def get_mesa_numero(self, obj):
        return obj.mesa.numero  # Devuelve el número de la mesa

    get_mesa_numero.short_description = 'Mesa'  # Nombre que se mostrará en la columna

    def get_detalle_pedido(self, obj):
        # Devuelve un string con los nombres de los productos y sus cantidades
        return ', '.join([f"{detalle.producto.nombre} (Cantidad: {detalle.cantidad})" for detalle in obj.detalles.all()])
    
    get_detalle_pedido.short_description = 'Detalles del Pedido'  # Nombre que se mostrará en la columna

# Registrar los modelos
admin.site.register(Producto)
admin.site.register(Mesa)  # Esto ahora se referirá al modelo definido en models.py
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido)
