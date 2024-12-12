from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from .models import Mesa, Producto, Pedido, DetallePedido
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.formats import number_format
from django.db.models import Sum
from datetime import datetime, timedelta

def ver_pedidos(request):
    """
    Muestra los pedidos ordenados por fecha y actualiza dinámicamente si es una solicitud AJAX.
    """
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        pedidos = Pedido.objects.all().order_by('-fecha').values(
            'id', 'mesa__numero', 'producto__nombre', 'cantidad', 'total', 'fecha'
        )
        # Formatear el total en cada pedido antes de enviarlo como JSON
        for pedido in pedidos:
            pedido['total_formateado'] = number_format(
                pedido['total'], decimal_pos=0, use_l10n=True, force_grouping=True
            )
        return JsonResponse(list(pedidos), safe=False)

    # Para solicitudes normales, renderizar la página HTML
    pedidos = Pedido.objects.all().order_by('-fecha')
    for pedido in pedidos:
        # Formatear el total para mostrar en la plantilla
        pedido.total_formateado = number_format(
            pedido.total, decimal_pos=0, use_l10n=True, force_grouping=True
        )
    return render(request, 'ver_pedidos.html', {'pedidos': pedidos})

def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'mesa'):
            login(request, user)
            return redirect('index')
        else:
            return HttpResponse("Usuario o contraseña inválidos o el usuario no es una mesa.")

    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})

def agregar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if not hasattr(request.user, 'mesa'):
        return HttpResponse("Este usuario no tiene una mesa asignada.", status=400)

    mesa = request.user.mesa
    pedido, created = Pedido.objects.get_or_create(mesa=mesa, finalizado=False)
    detalle, created = DetallePedido.objects.get_or_create(pedido=pedido, producto=producto)
    detalle.cantidad += cantidad
    detalle.save()

    return redirect('index')

def admin_home(request):
    productos = Producto.objects.all()
    mesas = Mesa.objects.all()
    pedidos = Pedido.objects.all()
    return render(request, 'admin_home.html', {'productos': productos, 'mesas': mesas, 'pedidos': pedidos})

def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        categoria = request.POST.get('categoria')
        imagen = request.FILES.get('imagen')

        # Validar el campo precio
        try:
            precio = float(precio)
        except ValueError:
            messages.error(request, "Por favor, ingresa un número válido en el campo precio.")
            return render(request, 'crear_producto.html', {'form': request.POST})
        
        # Crear el producto si no hay errores
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria,
            imagen=imagen,
        )
        messages.success(request, "Producto creado exitosamente.")
        return redirect('admin_home')

    return render(request, 'crear_producto.html')

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        producto.nombre = request.POST['nombre']
        producto.descripcion = request.POST.get('descripcion', '')
        producto.precio = request.POST['precio']
        producto.categoria = request.POST['categoria']
        producto.stock = request.POST['stock']

        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']

        producto.save()
        return redirect('admin_home')
    return render(request, 'editar_producto.html', {'producto': producto})

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('admin_home')

def crear_mesa(request):
    if request.method == "POST":
        numero = request.POST.get("numero")
        if Mesa.objects.filter(numero=numero).exists():
            messages.error(request, "Ya existe una mesa con este número.")
        else:
            Mesa.objects.create(numero=numero)
            messages.success(request, "Mesa creada correctamente.")
            return redirect("admin_home")
    return render(request, "crear_mesa.html")

def editar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.method == "POST":
        mesa.numero = request.POST['numero']
        mesa.disponible = 'disponible' in request.POST
        mesa.save()
        return redirect('admin_home')
    return render(request, 'editar_mesa.html', {'mesa': mesa})

def eliminar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if request.method == "POST":
        mesa.delete()
        return redirect('admin_home')
    return render(request, 'eliminar_mesa.html', {'mesa': mesa})

def login_mesa(request):
    if request.method == "POST":
        numero_mesa = request.POST.get("numero_mesa")

        try:
            mesa = Mesa.objects.get(numero=numero_mesa)
            request.session['mesa_id'] = mesa.id
            return redirect('index')
        except Mesa.DoesNotExist:
            messages.error(request, "La mesa ingresada no existe.")
            return redirect('login_mesa')

    return render(request, 'login_mesa.html')

def index(request):
    if 'mesa_id' not in request.session:
        return redirect('login_mesa')

    productos = Producto.objects.all()
    return render(request, 'index.html', {'productos': productos})

def pedido_resumen(request):
    pedido = Pedido.objects.last()
    return render(request, 'pedido_resumen.html', {'pedido': pedido})

def finalizar_pedido(request):
    if request.method == 'POST':
        carrito = request.session.get('cart', {})
        if not carrito:
            return JsonResponse({"error": "El carrito está vacío"}, status=400)

        total = sum(item['cantidad'] * item['precio'] for item in carrito.values())
        pedido = Pedido.objects.create(total=total)

        for product_id, item in carrito.items():
            producto = Producto.objects.get(id=product_id)
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio=producto.precio
            )

        request.session['cart'] = {}
        return render(request, 'pedido_resumen.html', {'pedido': pedido})

    return redirect('index')

def ver_pedidos(request):
    pedidos = Pedido.objects.all().order_by('-fecha')
    context = {
        'pedidos': pedidos,
    }
    
    for pedido in pedidos:
        for detalle in pedido.detalles.all():
            detalle.subtotal = detalle.cantidad * detalle.precio

    pedido.total_formateado = number_format(pedido.total, decimal_pos=0, use_l10n=True, force_grouping=True)
    return render(request, 'ver_pedidos.html', {'pedidos': pedidos})

@csrf_exempt
def guardar_pedido(request):
    if request.method == "POST":
        data = json.loads(request.body)
        mesa_id = request.session.get("mesa_id")

        if mesa_id is None:
            return JsonResponse({"error": "No se ha seleccionado una mesa"}, status=400)

        pedido = Pedido.objects.create(mesa_id=mesa_id, estado="no tomado", total=0)
        total = 0
        for producto_id, item in data.items():
            producto = Producto.objects.get(id=producto_id)
            cantidad = item["quantity"]
            subtotal = producto.precio * cantidad

            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio=producto.precio
            )

            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()
            else:
                return JsonResponse({"error": f"No hay suficiente stock para {producto.nombre}"}, status=400)

            total += subtotal

        pedido.total = total
        pedido.save()

        return JsonResponse({"mensaje": "Pedido realizado con éxito"})

def actualizar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id)
        nuevo_estado = request.POST.get('estado')

        # Actualizar el estado del pedido
        if nuevo_estado in dict(Pedido.ESTADO_OPCIONES).keys():
            pedido.estado = nuevo_estado
            pedido.save()

            # Si el estado es "servido" y aún no se actualizó el stock
            if nuevo_estado == "servido" and not pedido.stock_actualizado:
                for detalle in pedido.detalles.all():
                    if detalle.producto.stock < detalle.cantidad:
                        messages.error(request, f"No hay suficiente stock para {detalle.producto.nombre}.")
                        return redirect('ver_pedidos')  # Evita actualizar el pedido si no hay suficiente stock

                    # Reducir el stock
                    detalle.producto.stock -= detalle.cantidad
                    detalle.producto.save()

                # Marcar como actualizado el stock
                pedido.stock_actualizado = True
                pedido.save()

        return redirect('ver_pedidos')


def ver_detalle_pedido(request, pedido_id):
    # Recuperar el pedido y los detalles asociados
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()

    # Calcular el total directamente sumando los subtotales de los detalles
    total = sum(detalle.total for detalle in detalles)

    return render(request, 'detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'total': total,  # Pasar el total calculado al template
    })
def eliminar_pedido(request, pedido_id):
    """
    Elimina un pedido después de confirmarlo.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        # Eliminar el pedido
        pedido.delete()
        # Redirigir a la lista de pedidos o la página deseada
        return redirect('ver_pedidos')  # Cambia 'ver_pedidos' por la URL correcta

    return render(request, 'eliminar_pedido.html', {'pedido': pedido})

def obtener_pedidos_actualizados(request):
    pedidos = Pedido.objects.values('id', 'mesa__numero', 'total', 'estado', 'fecha')
    return JsonResponse(list(pedidos), safe=False)

def actualizar_total(self):
        """Recalcula el total del pedido sumando los subtotales de los detalles."""
        self.total = sum(detalle.cantidad * detalle.precio for detalle in self.detalles.all())
        self.save()




def historial_pedidos(request):
    pedidos = Pedido.objects.filter(en_historial=True).order_by('-fecha')
    return render(request, 'historial_pedidos.html', {'pedidos': pedidos})


def ver_detalle_pedido_eliminado(request, pedido_id):


    pedido = get_object_or_404(Pedido, id=pedido_id, eliminado=True)  # Asegúrate de que sea un pedido eliminado
    detalles = pedido.detalles.all()

    total = sum(detalle.total for detalle in detalles)  # Calcula el total usando los detalles

    return render(request, 'detalle_pedido_eliminado.html', {
        'pedido': pedido,
        'detalles': detalles,
        'total': total,
    })

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import ExtractHour
from datetime import datetime, timedelta
from .models import DetallePedido, Pedido

def estadisticas(request):
    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    # Producto más vendido esta semana
    producto_mas_vendido_semana = (
        DetallePedido.objects.filter(pedido__fecha__gte=inicio_semana)
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')
        .first()
    )

    # Producto más vendido este mes
    producto_mas_vendido_mes = (
        DetallePedido.objects.filter(pedido__fecha__gte=inicio_mes)
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')
        .first()
    )

    # Producto menos vendido esta semana
    producto_menos_vendido_semana = (
        DetallePedido.objects.filter(pedido__fecha__gte=inicio_semana)
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('total_vendido')
        .first()
    )

    # Ingresos totales
    ingresos_semana = DetallePedido.objects.filter(
        pedido__fecha__gte=inicio_semana
    ).aggregate(total=Sum('precio'))['total'] or 0

    ingresos_mes = DetallePedido.objects.filter(
        pedido__fecha__gte=inicio_mes
    ).aggregate(total=Sum('precio'))['total'] or 0

    # Horas pico
    horas_pico = (
        Pedido.objects.filter(fecha__gte=inicio_semana)
        .annotate(hora=ExtractHour('fecha'))
        .values('hora')
        .annotate(total_pedidos=Count('id'))
        .order_by('-total_pedidos')
    )
    hora_pico = horas_pico.first()

    # Categoría más vendida este mes
    categoria_mas_vendida = (
        DetallePedido.objects.filter(pedido__fecha__gte=inicio_mes)
        .values('producto__categoria')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')
        .first()
    )

    # Número total de pedidos
    total_pedidos_hoy = Pedido.objects.filter(fecha__date=hoy.date()).count()
    total_pedidos_semana = Pedido.objects.filter(fecha__gte=inicio_semana).count()
    total_pedidos_mes = Pedido.objects.filter(fecha__gte=inicio_mes).count()

    return render(request, 'estadisticas.html', {
        'producto_mas_vendido_semana': producto_mas_vendido_semana,
        'producto_mas_vendido_mes': producto_mas_vendido_mes,
        'producto_menos_vendido_semana': producto_menos_vendido_semana,
        'ingresos_semana': ingresos_semana,
        'ingresos_mes': ingresos_mes,
        'hora_pico': hora_pico,
        'categoria_mas_vendida': categoria_mas_vendida,
        'total_pedidos_hoy': total_pedidos_hoy,
        'total_pedidos_semana': total_pedidos_semana,
        'total_pedidos_mes': total_pedidos_mes,
    })

