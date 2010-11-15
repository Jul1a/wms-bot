from models import Users, Servers, Layers, LayerSet, SLD, LayerTree
from django.shortcuts import render_to_response
from django.template import loader, Context, Template, RequestContext
from django.http import HttpResponseRedirect, Http404
#from django.newforms import widgets
from django import forms
from settings import MEDIA_URL

#from faqs.models import Category
#from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm, TreeNodeChoiceField
from django.forms import ModelChoiceField

#@filter
#def width_tables(obj, wd):
#  return 10*wd


def show_category_tree(request):
  #TreeNodeChoiceField
  list_servers = ModelChoiceField(queryset = Servers.objects.all(), 
                                     required = False,
                                     label = 'server',
                                     widget=forms.Select({'class':'select_style'}),
                                     empty_label = None
                                    )
  #TreeNodeChoiceField                
  list_sets = ModelChoiceField(queryset = LayerSet.objects.all(),
                                  required = False,
                                  label = 'set',
                                  widget=forms.Select({'class':'select_style'}),
                                  empty_label = None
                                 )
#  query = request.GET.get('server', '')
#  if query:
#    qset = (Q(name__icontains=query))
#    results = Servers.objects.filter(qset).distinct()
#  else:
#    results = []
  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'nodes_layers':Layers.tree.all(), 
                                'nodes_layertree':LayerTree.tree.all(), 
                                'list_servers': list_servers.widget.render("test", None),
                                'list_sets': list_sets.widget.render("test", None),
                              },
                              context_instance=RequestContext(request)
                            )
