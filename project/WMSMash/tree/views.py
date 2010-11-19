from models import Users, Servers, Layers, LayerSet, SLD, LayerTree
from django.shortcuts import render_to_response
from django.template import loader, Context, Template, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
#from django.newforms import widgets
from django import forms
from settings import MEDIA_URL
from django.db.models import Q

#from faqs.models import Category
#from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm, TreeNodeChoiceField
from django.forms import ModelChoiceField, ChoiceField


def show_category_tree(request):
  #TreeNodeChoiceField
#  form_server = InForm()
  #TreeNodeChoiceField
  selected_server = request.GET.get('list_servers', 0)
  selected_set = request.GET.get('list_sets', 0)
  list_servers = ModelChoiceField(queryset = Servers.objects.all(), 
                                     required = False,
                                     label = '',
                                     widget=forms.Select({'class':'select_style', 
                                                          'onChange':'this.form.submit();'
                                                         }),
                                     empty_label = None
                                    ) 
  #BIG_CHOICES = [(c.id, '%s(%s)'%(c.name, c.title)) for c in LayerSet.objects.all()]
  list_sets = ModelChoiceField(queryset = LayerSet.objects.all(),
                                  required = False,
                                  label = '',
                                  widget=forms.Select({'class':'select_style', 
                                                       'onChange':'this.form.submit();'
                                                      }),
                                  empty_label = None
                                 )
#  query = request.get_full_path()
  if not selected_server:
    for c in Servers.objects.all():
      selected_server = c.id
      break;
  if not selected_set:
    for c in LayerSet.objects.all():
      selected_set = c.id
      break;
  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'nodes_layers':Layers.tree.all(), 
                                'nodes_layertree':LayerTree.tree.all(), 
                                'list_servers': list_servers.widget.render("list_servers", selected_server),
                                'list_sets': list_sets.widget.render("list_sets", selected_set),
                                'selected_server':int(selected_server),
                                'selected_set':int(selected_set),
                              },
                              context_instance=RequestContext(request)
                            )

