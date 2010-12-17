from models import Users, Servers, Layers, LayerSet, SLD, LayerTree
from django.shortcuts import render_to_response
from django.template import loader, Context, Template, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
#from django.newforms import widgets
from django import forms, template
from settings import MEDIA_URL, LAYER_SET_URL
from django.db.models import Q
from django.db import connection, transaction
#from faqs.models import Category
#from mptt.exceptions import InvalidMove
from mptt.forms import MoveNodeForm, TreeNodeChoiceField
from django.forms import ModelChoiceField, ChoiceField
from django import template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import auth

def login(request):
  username = request.GET['username']
  password = request.GET['password']
  user = auth.authenticate(username=username, password=password)
  if user is not None and user.is_active:
   # Correct password, and the user is marked "active"
    auth.login(request, user)
    # Redirect to a success page.
    return HttpResponseRedirect("/accounts/register/")
  else:
    # Show an error page
    return HttpResponseRedirect("/accounts/login/")

#  return render_to_response("login.html",
#                              context_instance=RequestContext(request)
#                            )

def register(request):
  if request.method == 'GET':
    username = request.GET.get('username', 0)
    passwd1 = request.GET.get('password1', 0)
    passwd2 = request.GET.get('password2', 0)
    if (passwd1 != passwd2) or (not username):
      return render_to_response("registration/register.html",
                              context_instance=RequestContext(request)
                            )
    else:
      user = auth.authenticate(username = username, password = passwd1)
      if user is not None:
        return render_to_response("registration/register.html",
                              context_instance=RequestContext(request)
                            )
      else:
        user = User.objects.create(username = username, password = passwd1, is_active = True)
        #user.save()
        
        return HttpResponseRedirect("/accounts/login/")
  else:
    return render_to_response("registration/register.html",
                              context_instance=RequestContext(request)
                            )

def show_category_tree(request):
  slt_server = request.GET.get('list_servers', 0)
  slt_set = request.GET.get('list_sets', 0)
  ####
  oprt = request.GET.get('oprt', 0)
  list_all = 0
  if oprt == 'add':
    LayerTree.objects.add_inset(request)
  if oprt == 'del':
    LayerTree.objects.del_fromset(request)
  if oprt == 'hidd_off':
    layer = request.GET.get('set_layer', 0)
    layers = []
    ll = (int(layer), )
    layers.append(ll)
    cursor = connection.cursor()
    LayerTree.objects.hidden(1, layers, cursor)
  if oprt == 'hidd_on':
    layer = request.GET.get('set_layer', 0)
    layers = []
    ll = (int(layer), )
    layers.append(ll)
    cursor = connection.cursor()
    LayerTree.objects.hidden(0, layers, cursor)
  #if oprt == 'pub_off':
  #  layer = request.GET.get('set_layer', 0)
  #  layers = []
  #  ll = (int(layer), )
  #  layers.append(ll)
  #  cursor = connection.cursor()
  #  LayerTree.objects.hidden(0, layers, cursor)
  title_group = request.GET.get('title_group', 0)
  if title_group:
    LayerTree.objects.add_newgroup(request)
  addset = request.GET.get('add_set', 0)
  if addset:
    LayerSet.objects.add_newset(request)
  editset = request.GET.get('edit_set', 0)
  if editset:
    LayerSet.objects.edit_set(request)
  delset = request.GET.get('delete_set', 0)
  if delset:
    LayerSet.objects.del_set(request)
    slt_set = 0
  servers = request.GET.get('add_server', 0)
  if servers:
    if servers.find('edit_') == 0:
      Servers.objects.editURL(request, servers)
    if servers == 'update':
      Servers.objects.add(request)
  ###
  
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
  
  
  cursor = connection.cursor()
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
  
  if id_server:
    cursor.execute('''
                      WITH RECURSIVE tree 
                      AS 
                      (
                        SELECT 
                              name, title, id, parent_id, server_id, NULL::varchar AS parent_name, id::text AS path 
                        FROM 
                              tree_layers
                        WHERE parent_id IS NULL 
                        UNION 
                        SELECT 
                              f1.name, f1.title, f1.id, f1.parent_id, f1.server_id, tree.name 
                        AS parent_name, tree.path || '-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layers f1 ON f1.parent_id = tree.id)
                        SELECT name, title, id, parent_id, name, path FROM tree WHERE server_id = %d ORDER BY path;
                    '''%id_server)
    layers = cursor.fetchall()
  else:
    layers = None
  
  if id_set:
    cursor.execute('''
                      WITH RECURSIVE tree 
                      AS 
                      (
                        SELECT 
                              name, id, parent_id, lset_id, layer_id, hidden, NULL::varchar AS parent_name, id::text AS path 
                        FROM 
                              tree_layertree
                        WHERE parent_id IS NULL 
                        UNION 
                        SELECT 
                              f1.name, f1.id, f1.parent_id, f1.lset_id, f1.layer_id, f1.hidden, tree.name 
                        AS parent_name, tree.path || '-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layertree f1 ON f1.parent_id = tree.id)
                        SELECT name, id, parent_id, lset_id, layer_id, hidden, name, path FROM tree WHERE lset_id = %d  ORDER BY path;
                  '''%id_set)
    layertree = cursor.fetchall()
  else:
    layertree = None

  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'LAYER_SET_URL': LAYER_SET_URL,
                                'nodes_layers':Layers.tree.all(), 
                                'layers' : layers,
                                'nodes_layertree':LayerTree.tree.all(), 
                                'layertree' : layertree,
                                'list_servers': list_servers.widget.render("list_servers", id_server),
                                'list_sets': list_sets.widget.render("list_sets", id_set),
                                'selected_server':selected_server,
                                'selected_set':selected_set,
                              },
                              context_instance=RequestContext(request)
                            )



