from django.forms import ModelForm
from django.forms.widgets import TextInput

from .models import Tag


class TagAdminForm(ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={"type": "color"})
        }
