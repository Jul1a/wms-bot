from django import template
from WMSMash.tree.models import Layers
from django.db.models import Q

register = template.Library()

# 0 -its group, 1 - other
@register.filter(name='rect')
def rect(value):
  if value.layer_id:
    mt = Layers.objects.filter(parent=value.layer_id)
    ct = mt.count()
    if ct:
      return 0
    else:
      return 1
  else:
    return 0