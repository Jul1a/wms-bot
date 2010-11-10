from django.db import models
#from mptt.models import MPTTModel
#from apps.mptt.models import *
#from mptt.models import *
#from django import forms
from django.forms.models import ModelForm #, ModelChoiceField
#import mptt

class MyForms(ModelForm):
  class Meta:
    model = Layers
    fields = ('name', 'title') 
#    widget = {
#              'name': 
#             }

  




