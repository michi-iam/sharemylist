from django.db.models.fields import files
from django.forms import fields
from django import forms
from django.contrib.auth.models import User


from .models import Category



class CustomUserProfileForm(forms.ModelForm):
    class Meta:
        model=User
        fields= ["email", "first_name", "last_name"]
    def __init__(self, *args, **kwargs):
        super(CustomUserProfileForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
        })

        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ["author", "is_private", "is_favorite"]

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
        })

