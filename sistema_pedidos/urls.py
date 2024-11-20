# # urls.py
# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path, include
# from django.contrib import admin
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('admin_home/', views.admin_home, name='admin_home'),
#      path('index', views.index, name='index'),
#      path('', views.login_mesa, name='login_mesa'),

#     # Manejo de productos
#     path('crear_producto/', views.crear_producto, name='crear_producto'),
#     path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
#     path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
#     path('finalizar_pedido/', views.finalizar_pedido, name='finalizar_pedido'),
#     path('pedido_resumen/', views.pedido_resumen, name='pedido_resumen'),
#     path('guardar_pedido/', views.guardar_pedido, name='guardar_pedido'),
#     path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),
#       path('ver_pedidos/eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
#     path('actualizar_estado_pedido/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
#     path('ver_pedido/<int:pedido_id>/', views.ver_detalle_pedido, name='ver_detalle_pedido'),

#     # Manejo de mesas
#     path('crear_mesa/', views.crear_mesa, name='crear_mesa'),
#     path('editar_mesa/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),
#     path('eliminar_mesa/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),

#     # M
#     path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),  # URL para "Ve
#     path('obtener_pedidos_actualizados/', views.obtener_pedidos_actualizados, name='obtener_pedidos_actualizados'),
# ]# Agregar rutas de archivos multimedia en modo de desarrollo
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin_home/', views.admin_home, name='admin_home'),
     path('index', views.index, name='index'),
     path('', views.login_mesa, name='login_mesa'),
     path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),


    # Manejo de productos
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('editar_producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar_producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('finalizar_pedido/', views.finalizar_pedido, name='finalizar_pedido'),
    path('pedido_resumen/', views.pedido_resumen, name='pedido_resumen'),
    path('guardar_pedido/', views.guardar_pedido, name='guardar_pedido'),
    path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),
      path('ver_pedidos/eliminar/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('actualizar_estado_pedido/<int:pedido_id>/', views.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('ver_pedido/<int:pedido_id>/', views.ver_detalle_pedido, name='ver_detalle_pedido'),

    # Manejo de mesas
    path('crear_mesa/', views.crear_mesa, name='crear_mesa'),
    path('editar_mesa/<int:mesa_id>/', views.editar_mesa, name='editar_mesa'),
    path('eliminar_mesa/<int:mesa_id>/', views.eliminar_mesa, name='eliminar_mesa'),

    # M
    path('ver_pedidos/', views.ver_pedidos, name='ver_pedidos'),  # URL para "Ve
    path('obtener_pedidos_actualizados/', views.obtener_pedidos_actualizados, name='obtener_pedidos_actualizados'),
]# Agregar rutas de archivos multimedia en modo de desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

