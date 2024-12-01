from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import Mesa, Producto, Pedido, DetallePedido
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import check_password


def login_user(request):
    """Inicia sesión para una mesa."""
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
    """Cierra la sesión de la mesa."""
    logout(request)
    return redirect('login')


def productos(request):
    """Muestra los productos para el administrador."""
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


def agregar_producto(request, producto_id):
    """Agrega un producto al pedido de la mesa."""
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
    if request.method == "POST":
        nombre = request.POST['nombre']
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST['precio']
        categoria = request.POST['categoria']
        stock = request.POST['stock']
        imagen = request.FILES.get('imagen')  # Captura el archivo de imagen

        # Crear el producto directamente
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria,
            stock=stock,
            imagen=imagen  # Guarda la imagen en el campo `ImageField`
        )
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

        # Verifica si hay una nueva imagen cargada
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']  # Actualiza la imagen si se cargó una nueva

        producto.save()  # Guarda los cambios del producto, incluyendo la imagen actualizada
        return redirect('admin_home')
    return render(request, 'editar_producto.html', {'producto': producto})

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('admin_home')

# Mesas
def crear_mesa(request):
    if request.method == "POST":
        numero = request.POST.get("numero")
        if Mesa.objects.filter(numero=numero).exists():
            messages.error(request, "Ya existe una mesa con este número.")
        else:
            Mesa.objects.create(numero=numero)
            messages.success(request, "Mesa creada correctamente.")
            return redirect("admin_home")  # O la URL de redirección que prefieras
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
    """Vista para que una mesa inicie sesión."""
    if request.method == "POST":
        numero_mesa = request.POST.get("numero_mesa")
        contraseña = request.POST.get("contraseña")

        try:
            mesa = Mesa.objects.get(numero=numero_mesa)
            if check_password(contraseña, mesa.contraseña):  # Verifica la contraseña
                request.session['mesa_id'] = mesa.id  # Guarda la mesa en la sesión
                return redirect('index')  # Redirige a la vista principal
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Mesa.DoesNotExist:
            messages.error(request, "La mesa ingresada no existe.")
    
    return render(request, 'login_mesa.html')

def index(request):
    # Verificamos si la mesa está en la sesión
    if 'mesa_id' not in request.session:
        return redirect('login_mesa')  # Redirige al inicio de sesión de mesa si no está autenticado

    productos = Producto.objects.all()
    return render(request, 'index.html', {'productos': productos})

def pedido_resumen(request):
    pedido = Pedido.objects.last()  # El último pedido realizado
    return render(request, 'pedido_resumen.html', {'pedido': pedido})


def finalizar_pedido(request):
    if request.method == 'POST':
        carrito = request.session.get('cart', {})
        if not carrito:
            return JsonResponse({"error": "El carrito está vacío"}, status=400)

        total = sum(item['cantidad'] * item['precio'] for item in carrito.values())

        # Crear el pedido
        pedido = Pedido.objects.create(total=total)

        # Crear detalles del pedido
        for product_id, item in carrito.items():
            producto = Producto.objects.get(id=product_id)
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio=producto.precio
            )

        # Limpiar el carrito de la sesión
        request.session['cart'] = {}

        return render(request, 'pedido_resumen.html', {'pedido': pedido})

    return redirect('index')


def ver_pedidos(request):
    """Vista que muestra todos los pedidos para el administrador."""
    pedidos = Pedido.objects.all()

    # Calcula el subtotal de cada detalle de pedido
    for pedido in pedidos:
        for detalle in pedido.detalles.all():
            detalle.subtotal = detalle.cantidad * detalle.precio

    return render(request, 'ver_pedidos.html', {'pedidos': pedidos})


@csrf_exempt
def guardar_pedido(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Obtiene los datos del carrito en JSON
        mesa_id = request.session.get("mesa_id")  # Obtén la mesa de la sesión o ajusta según tus necesidades
        print(f"Mesa en sesión: {mesa_id}")

        if mesa_id is None:
            return JsonResponse({"error": "No se ha seleccionado una mesa"}, status=400)

        pedido = Pedido.objects.create(mesa_id=mesa_id, estado="no tomado", total=0)  # Crea el pedido inicialmente con total 0

        total = 0
        for producto_id, item in data.items():
            producto = Producto.objects.get(id=producto_id)
            cantidad = item["quantity"]
            subtotal = producto.precio * cantidad

            # Crea un detalle del pedido
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio=producto.precio
            )

            # Reducir el stock del producto
            if producto.stock >= cantidad:
                producto.stock -= cantidad
                producto.save()
                print(f"Mesa en sesión: {mesa_id}")

            else:
                return JsonResponse({"error": f"No hay suficiente stock para {producto.nombre}"}, status=400)

            total += subtotal

        # Actualiza el total del pedido
        pedido.total = total
        pedido.save()

        return JsonResponse({"mensaje": "Pedido realizado con éxito"})


def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        pedido.estado = nuevo_estado
        pedido.save()

        # Redirige a la lista general de pedidos
        return redirect('ver_pedidos')  # Aquí no se pasa pedido_id

def ver_detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()

    # Calculate the total amount
    total = sum(detalle.cantidad * detalle.producto.precio for detalle in detalles)

    return render(request, 'detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles,
        'total': total
    })


def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.delete()
    return redirect(reverse('ver_pedidos'))


def obtener_pedidos_actualizados(request):
    pedidos = Pedido.objects.values('id', 'mesa__numero', 'total', 'estado', 'fecha')
    return JsonResponse(list(pedidos), safe=False)

