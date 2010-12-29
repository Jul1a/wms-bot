from django import template
from WMSMash.tree.models import Layers, LayerSet, LayerTree, Servers
from django.db.models import Q

register = template.Library()

# 0 - its group, 1 - not groups, 2-users group
@register.filter(name='rect')
def rect(value):
  if value: 
  #.layer_id:
    mt = Layers.objects.filter(parent=value)#.layer_id)
    ct = mt.count()
    if ct:
      return 0
    else:
      return 1
  else:
    return 2
    
@register.filter(name='pub')
def pub(value):
  if value: 
  #.layer_id:
    layer = Layers.objects.get(id=value)#.layer_id
    pb = layer.pub
    if pb:
      return 1
    else:
      return 0
  else:
    return 0
    
@register.filter(name='pub_set')
def pub_set(value):
  if value: 
  #.set_id:
    set = LayerSet.objects.get(id=value)#.set_id
    pb = set.pub
    if pb:
      return 1
    else:
      return 0
  else:
    return 0

@register.filter(name='hidden_layer')
def hidden_layer(id_layer):
  if id_layer:
    layer_obj = LayerTree.objects.get(id = id_layer)
    if layer_obj.parent_id:
      lparent = LayerTree.objects.get(id = layer_obj.parent_id)
      if lparent.hidden == 1:
        return 1
      else:
        return 0
    else:
      return 0
  else: 
    return 0

@register.filter(name='servname')
def servname(value):
  if value: 
  #.layer_id:
    layer = Layers.objects.get(id=value)#.layer_id
    id_server = layer.server_id
    if id_server:
      server = Servers.objects.get(id=id_server)
      if server.name:
        return server.name#+ ' %d'%server.id
      else:
        return server.title#+ ' %d'%server.id
    else:
      return ""
  else:
    return ""
    
    
    


