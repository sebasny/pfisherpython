from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'imagen']

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')

        # Validar que el precio sea un número
        try:
            float(precio)  # Intenta convertirlo a número
        except ValueError:
            raise forms.ValidationError("Por favor, ingresa un número válido sin comas ni puntos.")
        
        # Retorna el precio convertido
        return precio