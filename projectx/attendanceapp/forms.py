from django import forms 
from .models import Indlist
  
class UserForm(forms.ModelForm): 
  
    class Meta: 
        model = Indlist
        fields = ['username', 'orgname', 'imagee']