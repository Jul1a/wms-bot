from models import Users, Servers, Layers, LayerSet, SLD, LayerTree
from django.shortcuts import render_to_response
from django.template import loader, Context, Template, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
#from django.newforms import widgets
from django import forms, template
from settings import MEDIA_URL
from django.db.models import Q

#from faqs.models import Category
#from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm, TreeNodeChoiceField
from django.forms import ModelChoiceField, ChoiceField

#register=template.Library()

#@register.filter
#def restr(items):
#  sl_layer = Layers.objects.get(id=items.id)
  
#  return 0
#restr = register.tag(restr)

def show_category_tree(request):

  BIG_CHOICES = [(c.id, "(%s(%s"%(c.title, c.name)) for c in Servers.objects.all()]
  list_servers = forms.ChoiceField(choices = BIG_CHOICES,
                                     required = False,
                                     label = '',
                                     widget=forms.Select({'class':'select_style', 
                                                          'id': 'list_servers'
                                                         }),
                                    ) 
  BIG_CHOICES = [(c.id, "(%s(%s"%(c.title, c.name)) for c in LayerSet.objects.all()]
  list_sets = forms.ChoiceField(choices = BIG_CHOICES,
                                  required = False,
                                  label = '',
                                  widget=forms.Select({'class':'select_style', 
                                                        'id': 'list_sets'
                                                      }),
                                  #empty_label = None
                                 )
#  query = request.get_full_path()

  slt_server = request.GET.get('list_servers', 0)
  slt_set = request.GET.get('list_sets', 0)
  if not slt_server:
    for c in Servers.objects.all():
      selected_server = c
      break;
    if not selected_server:
      id_server = None
    else:
      id_server = selected_server.id
  else:
    selected_server = Servers.objects.get(id=slt_server)
    id_server = selected_server.id
  if not slt_set:
    for c in LayerSet.objects.all():
      selected_set = c
      break;
    if not selected_set:
      id_set = None
    else:
      id_set = selected_set.id
  else:
    selected_set = LayerSet.objects.get(id=slt_set)
    id_set = selected_set.id
  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'nodes_layers':Layers.tree.all(), 
                                'nodes_layertree':LayerTree.tree.all(), 
                                'list_servers': list_servers.widget.render("list_servers", id_server),
                                'list_sets': list_sets.widget.render("list_sets", id_set),
                                'selected_server':selected_server,
                                'selected_set':selected_set,
                              },
                              context_instance=RequestContext(request)
                            )

