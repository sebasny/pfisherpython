# Generated by Django 5.1.2 on 2024-11-12 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_pedidos', '0012_mesa_disponible_mesa_usuario_alter_mesa_numero'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mesa',
            name='disponible',
        ),
        migrations.RemoveField(
            model_name='mesa',
            name='usuario',
        ),
        migrations.AlterField(
            model_name='mesa',
            name='numero',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
