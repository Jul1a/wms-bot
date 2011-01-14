from models import Users, Servers, Layers, LayerSet, SLD, LayerTree
from django.shortcuts import render_to_response
from django.template import loader, Context, Template, RequestContext
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django import forms, template
from settings import MEDIA_URL, LAYER_SET_BASE_URL
from django.db.models import Q
from django.db import connection, transaction
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
  cursor = connection.cursor()

  # Definition of the seected server and set of layers
  slt_server = request.GET.get('list_servers', 0)
  slt_set = request.GET.get('list_sets', 0)

  # Stores list of sets that have layers from removed the server
  name_sets = 0
  
  # Stores the name of the group that failed to create
  namegroup = 0
  
  # Saved a list of layers which couldn't be inserted into a set of layers
  errlayer = "" 
  
  # Operations with layers of virtual set of layers
  oprt = request.GET.get('oprt', 0)
  # Layer in set that is processed
  set_layer = request.GET.get('set_layer', -1)
  
  if oprt and (set_layer != -1):
    # Operation of adding a layers in a virtual set of layers
    if oprt == 'add':
      layer = request.GET.get('layer', -1)
      namelayer = request.GET.get('namelayer', 0)
      list_layers = request.GET.get('layers', -1)
      err_layer = LayerTree.objects.add_inset(slt_server, slt_set, layer, set_layer, namelayer, list_layers, cursor)
      if not err_layer: 
        errlayer = ""
      else:
        for i in err_layer:
          errlayer += "%s ?end %d %d;"%(i[0], i[1], i[2])
    
    # Operation of deleting a layers in a virtual set of layers
    if oprt == 'del':
      LayerTree.objects.del_fromset(set_layer, cursor)
    
    # Operation of off hidden layers
    if (oprt == 'hidd_off') and set_layer:
      layers = []
      if set_layer == -1:
        ll = (0, )
      else:
        ll = (int(set_layer), )
      layers.append(ll)
      LayerTree.objects.hidden(1, layers, cursor)
    
    # Operation of on hidden layers 
    if (oprt == 'hidd_on') and set_layer:
      layers = []
      if set_layer == -1:
        ll = (0, )
      else:
        ll = (int(set_layer), )
      layers.append(ll)
      LayerTree.objects.hidden(0, layers, cursor)
    
    # Operation of adding style to a layer of a set
    if oprt == 'add_style':
      name = request.GET.get('namelayer', 0)
      url = request.GET.get('sld', 0)
      LayerTree.objects.addstyle(set_layer, name, url)
    
    # Operation of deleting style to a layer of a set
    if oprt == 'del_style':
      LayerTree.objects.delstyle(set_layer)
    
    # Operation off the layer of publicity
    #if oprt == 'pub_off':
    #  layers = []
    #  if set_layer == -1:
    #     ll = (0, )
    #  else:
    #     ll = (int(set_layer), )
    #  layers.append(ll)
    #  LayerTree.objects.hidden(0, layers, cursor)

  else:
    # Operation of adding a new group in set of layers 
    title_group = request.GET.get('title_group', 0)
    if title_group:
      lparent = request.GET.get('where_layer', -1)
      list_set = request.GET.get('list_sets', 0)
      namegroup = LayerTree.objects.add_newgroup(title_group, lparent, list_set)

    # Operations managment sets
  
    susers = 1 #hz
    # Operation to create a new set of layers
    addset = request.GET.get('add_set', 0)
    if addset:
      sname = request.GET.get('name_set', 0)
      stitle = request.GET.get('title_set', 0)
      sabstr = request.GET.get('abstract_set', 0)
      skeywords = request.GET.get('keywords_set', 0)

      slt_set = (LayerSet.objects.add_newset(sname, stitle, sabstr, skeywords, susers)).id

    # Operation of editing a describe set of layers
    editset = request.GET.get('edit_set', 0)
    if editset:
      sname = request.GET.get('name_set', 0)
      stitle = request.GET.get('title_set', 0)
      sabstr = request.GET.get('abstract_set', 0)
      skeywords = request.GET.get('keywords_set', 0)

      LayerSet.objects.edit_set(slt_set, sname, stitle, sabstr, skeywords, susers)
  
    # Operation of remove a set of layers
    delset = request.GET.get('delete_set', 0)
    if delset:
      LayerSet.objects.del_set(slt_set, cursor)
      slt_set = 0
  
    # Operations managment servers
  
    # Operation to add, edit the URL and update server
    servers = request.GET.get('add_server', 0)
    if servers:
      if servers.find('add_') == 0:
        Servers.objects.add(servers)
      if servers.find('edit_') == 0:
        Servers.objects.editURL(slt_server, servers)
      if servers == 'update':
        Servers.objects.update(slt_server)
      
    # Operation of remove server
    delserv = request.GET.get('delete_server', 0)
    if delserv:
      name_sets = Servers.objects.delete(slt_server, cursor)
      if not name_sets:
        slt_server = 0

  # Formed a list of servers with class = "select_style", value = Servers.id, id = "list_servers"
  BIG_CHOICES = [(c.id, "(%s(%s"%(c.title, c.name)) for c in Servers.objects.all()]
  list_servers = forms.ChoiceField(choices = BIG_CHOICES,
                                     required = False,
                                     label = '',
                                     widget=forms.Select({'class':'select_style', 
                                                          'id': 'list_servers'
                                                         }),
                                    ) 
  
  # Formed a list of sets with class = "select_style", value = LayerSet.id, id = "list_sets"
  BIG_CHOICES = [(c.id, "(%s(%s"%(c.title, c.name)) for c in LayerSet.objects.all()]
  list_sets = forms.ChoiceField(choices = BIG_CHOICES,
                                  required = False,
                                  label = '',
                                  widget=forms.Select({'class':'select_style', 
                                                        'id': 'list_sets'
                                                      }),
                                 )
  
  # Formed a list of SLD with class = "select_small", value = SLD.id, id = "list_sld"
  BIG_CHOICES = [(c.id, "%s(%s)"%(c.name, c.url)) for c in SLD.objects.all()]
  list_sld = forms.ChoiceField(choices = BIG_CHOICES,
                                     required = False,
                                     label = '',
                                     widget=forms.Select({'class':'select_small', 
                                                          'id': 'list_sld'
                                                         }),
                                    ) 

  selected_set = 0
  selected_server = ""
  # Definition id for server

  # If server was not selected
  if not slt_server:
    # Take the first server from the list
    for c in Servers.objects.all():
      selected_server = c
      break;
    
    if not selected_server:
      # If list is empty then id is not defined
      id_server = None
    else:
      id_server = selected_server.id
  else:
    # If server was selected
    selected_server = Servers.objects.get(id=slt_server)
    id_server = selected_server.id
  
  # Definition id for set
  
  # If set was not selected
  if not slt_set:
    # Take the first set from the list
    for c in LayerSet.objects.all():
      selected_set = c
      break;
    
    if not selected_set:
      # If list is empty then id is not defined
      id_set = None
    else:
      id_set = selected_set.id
  else:
    # If set was selected
    selected_set = LayerSet.objects.get(id=slt_set)
    id_set = selected_set.id
  
  # If the server has been selected then formed a list of its layers
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
                        AS parent_name, tree.path || '-000-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layers f1 ON f1.parent_id = tree.id)
                        SELECT name, title, id, parent_id, name, path FROM tree WHERE server_id = %s ORDER BY path, title;
                   ''', (id_server, ))
    layers = cursor.fetchall()
  else:
    layers = None
  
  # If the set has been selected then formed a list of its layers
  if id_set:
    cursor.execute('''
                      WITH RECURSIVE tree 
                      AS 
                      (
                        SELECT 
                              name, id, parent_id, lset_id, layer_id, hidden, sld_id, NULL::varchar AS parent_name, id::text AS path 
                        FROM 
                              tree_layertree
                        WHERE parent_id IS NULL 
                        UNION 
                        SELECT 
                              f1.name, f1.id, f1.parent_id, f1.lset_id, f1.layer_id, f1.hidden, f1.sld_id, tree.name 
                        AS parent_name, tree.path || '-000-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layertree f1 ON f1.parent_id = tree.id)
                        SELECT name, id, parent_id, lset_id, layer_id, hidden, sld_id, name, path FROM tree WHERE lset_id = %s ORDER BY path, name;
                  ''', (id_set, ))
    layertree = cursor.fetchall()
  else:
    layertree = None

  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'LAYER_SET_BASE_URL': LAYER_SET_BASE_URL%"",
                                'nodes_layers':Layers.tree.all(), 
                                'layers' : layers,
                                'nodes_layertree':LayerTree.tree.all(), 
                                'layertree' : layertree,
                                'list_servers': list_servers.widget.render("list_servers", id_server),
                                'list_sets': list_sets.widget.render("list_sets", id_set),
                                'list_sld': list_sld.widget.render("list_sld", None),
                                'selected_server':selected_server,
                                'selected_set':selected_set,
                                'name_sets': name_sets,
                                'error_layers': errlayer,
                                'namegroup': namegroup
                              },
                              context_instance=RequestContext(request)
                            )



