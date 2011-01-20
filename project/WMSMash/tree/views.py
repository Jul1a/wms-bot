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

  # User running the application
  USER = 1

  # User rights
  role = (Users.objects.get(id = USER)).role
#  role = 1
  
  # Definition of the seected server and set of layers
  slt_server = request.GET.get('list_servers', 0)
  slt_set = request.GET.get('list_sets', 0)

  # Stores list of sets that have layers from removed the server
  name_sets = 0
  
  # Stores the name of the group that failed to create
  namegroup = 0
  
  # Saved a list of layers which couldn't be inserted into a set of layers
  errlayer = "" 

  # Stores error messages
  errors = ""
  
  # Set that is processed
  set_obj = 0
  if slt_set:
    try:
      set_obj = LayerSet.objects.get(id = slt_set)
    except:
      set_obj = 0
      slt_set = 0
      errors = "Such a set was not created"

  # Server that is processed
  serv_obj = 0
  if slt_server:
    try:
      serv_obj = Servers.objects.get(id = slt_server)
    except:
      serv_obj = 0
      slt_server = 0
      errors = "Such a server was not added"
  
  # Operations with layers of virtual set of layers
  oprt = request.GET.get('oprt', 0)
  # Layer in set that is processed
  set_layer = request.GET.get('set_layer', -1)
  
  if oprt and (set_layer != -1) and set_obj:

    # Operation of adding a layers in a virtual set of layers
    if ((oprt == 'add') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      layer = request.GET.get('layer', -1)
      namelayer = request.GET.get('namelayer', 0)
      list_layers = request.GET.get('layers', -1)
      try:
        listlayers = int(list_layers)
      except:
        listlayers = list_layers
      err_layer = LayerTree.objects.add_inset(slt_server, slt_set, layer, set_layer, namelayer, listlayers, cursor)
      if not err_layer: 
        errlayer = ""
      else:
        for i in err_layer:
          errlayer += "%s ?end %d %d;"%(i[0], i[1], i[2])
    
    # Operation of deleting a layers in a virtual set of layers
    if ((oprt == 'del') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      LayerTree.objects.del_fromset(set_layer, cursor)
    
    # Operation of off hidden layers
    if ((oprt == 'hidd_off') and set_layer and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      layers = []
      if set_layer == -1:
        ll = (0, )
      else:
        ll = (int(set_layer), )
      layers.append(ll)
      LayerTree.objects.hidden(1, layers, cursor)
    
    # Operation of on hidden layers 
    if ((oprt == 'hidd_on') and set_layer and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      layers = []
      if set_layer == -1:
        ll = (0, )
      else:
        ll = (int(set_layer), )
      layers.append(ll)
      LayerTree.objects.hidden(0, layers, cursor)
    
    # Operation of adding style to a layer of a set
    if ((oprt == 'add_style') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      name = request.GET.get('namelayer', 0)
      url = request.GET.get('sld', 0)
      LayerTree.objects.addstyle(set_layer, name, url)
    
    # Operation of deleting style to a layer of a set
    if ((oprt == 'del_style') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      LayerTree.objects.delstyle(set_layer)
    
    # Operation off the layer of publicity
    if ((oprt == 'pub_off') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      login = request.GET.get('login', -1)
      passwd = request.GET.get('passwd', -1)
      set_layer = request.GET.get('set_layer', -1)
      if (int(set_layer) == 0 and login and passwd):
        set_obj.pub = 0
        set_obj.login = login
        set_obj.passwd = passwd
        set_obj.save()
      if (int(set_layer) and login and passwd):
        LayerTree.objects.pub(0, set_layer, login, passwd)
    if ((oprt == 'pub_on') and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
      login = request.GET.get('login', 0)
      passwd = request.GET.get('passwd', 0)
      if (int(set_layer) == 0 and login and passwd):
        if ((set_obj.login == login) and (set_obj.passwd == passwd)):
          set_obj.pub = 1
          set_obj.login = None
          set_obj.passwd = None
          set_obj.save()
        if (int(set_layer) and login and passwd):
          LayerTree.objects.pub(1, set_layer, login, passwd)
        #LayerTree.objects.pub(1,set_layer, cursor)

  else:
    if set_obj:
      # Operation of adding a new group in set of layers 
      title_group = request.GET.get('title_group', 0)
      if (title_group and (set_obj.author_id == USER or set_obj.pub == 1 or role == 0)):
        lparent = request.GET.get('where_layer', -1)
        list_set = request.GET.get('list_sets', 0)
        namegroup = LayerTree.objects.add_newgroup(title_group, lparent, list_set)

    # Operations managment sets
  
    # Operation to create a new set of layers
    addset = request.GET.get('add_set', 0)
    if addset:
      sname = request.GET.get('name_set', 0)
      stitle = request.GET.get('title_set', 0)
      sabstr = request.GET.get('abstract_set', 0)
      skeywords = request.GET.get('keywords_set', 0)
      #spub = int(request.GET.get('pub_set', 0))
      newset_obj = LayerSet.objects.add_newset(sname, stitle, sabstr, skeywords, USER)
      if newset_obj:
        slt_set = newset_obj.id
      else:
        errors = "You have already created a set with the name \"%s\""%sname

    # Operation of editing a describe set of layers
    editset = request.GET.get('edit_set', 0)
    if editset and set_obj:
      sname = request.GET.get('name_set', 0)
      stitle = request.GET.get('title_set', 0)
      sabstr = request.GET.get('abstract_set', 0)
      skeywords = request.GET.get('keywords_set', 0)
      #spub = request.GET.get('pub_set', 0)
      if set_obj.author_id == USER or role == 0:
        set = LayerSet.objects.edit_set(slt_set, sname, stitle, sabstr, skeywords, USER)
        if set == 1:
          errors = "You have already created a set with the name \"%s\""%sname
      else:
        errors = "This set can edit only the owner"
  
    # Operation of remove a set of layers
    delset = request.GET.get('delete_set', 0)
    if delset and set_obj:
      if set_obj.author_id == USER or role == 0:
        LayerSet.objects.del_set(slt_set, cursor)
        slt_set = 0
      else:
        errors = "This set can be removed only by the owner"

    # Operations managment servers
  
    # Operation to add, edit the URL and update server
    servers = request.GET.get('add_server', 0)
    if servers:
      if servers.find('add_') == 0:
        Servers.objects.add(servers)
      if ((servers.find('edit_') == 0) and (serv_obj)):
        if serv_obj.owner_id == USER or role == 0:
          Servers.objects.editURL(slt_server, servers)
        else:
          errors = "URL of this server can edit only the resource owner"
      if ((servers == 'update') and (serv_obj)):
        if serv_obj.owner_id == USER or role == 0:
          Servers.objects.update(slt_server)
        else:
          errors = "URL of this server can update only the resource owner"
      
    # Operation of remove server
    delserv = request.GET.get('delete_server', 0)
    if delserv and serv_obj:
      if serv_obj.owner_id == USER or role == 0:
        name_sets = Servers.objects.delete(slt_server, cursor)
        if not name_sets:
          slt_server = 0
          serv_obj = 0
      else:
        errors = "This server can only delete the resource owner"

  # Formed a list of servers with class = "select_style", value = Servers.id, id = "list_servers"
  #BIG_CHOICES = [(c.id, "(%s(%s"%(c.title, c.name)) for c in Servers.objects.all()]
  BIG_CHOICES = []
  for c in Servers.objects.all():
    if (c.owner_id == USER) or (c.pub == 1) or (role == 0):
      BIG_CHOICES.append((c.id, "(%s(%s" % (c.title, c.name)))

  list_servers = forms.ChoiceField(choices = BIG_CHOICES,
                                     required = False,
                                     label = '',
                                     widget=forms.Select({'class':'select_style', 
                                                          'id': 'list_servers'
                                                         }),
                                    ) 
  
  # Formed a list of sets with class = "select_style", value = LayerSet.id, id = "list_sets"
  BIG_CHOICES = []
  for c in LayerSet.objects.all():
    if (c.author_id == USER) or (c.pub == 1) or (role == 0):
      BIG_CHOICES.append((c.id, "(%s(%s"%(c.title, c.name)))
  list_sets = forms.ChoiceField(choices = BIG_CHOICES,
                                  required = False,
                                  label = '',
                                  widget=forms.Select({'class':'select_style', 
                                                        'id': 'list_sets'
                                                      }),
                                 )
  
  # Formed a list of SLD with class = "select_small", value = SLD.id, id = "list_sld"
  #BIG_CHOICES = [(c.id, "%s(%s)"%(c.name, c.url)) for c in SLD.objects.all()]
  #BIG_CHOICES = ""
  list_sld = []
  for c in SLD.objects.all():
    if (c.owner_id == USER or (not c.owner_id) or role == 0):
      list_sld.append("%s(%s)"%(c.name, c.url))

  selected_set = 0
  selected_server = ""
  # Definition id for server

  # If server was not selected
  # or (role == 1 and serv_obj.owner_id != USER and serv_obj.pub == 0)
  if (not slt_server):
    # Take the first server from the list
    for c in Servers.objects.all():
      if (c.pub == 1) or (c.owner_id == USER) or role == 0:
        selected_server = c
        break;
    
    if not selected_server:
      # If list is empty then id is not defined
      id_server = None
    else:
      id_server = selected_server.id
  else:
    # If server was selected
    if serv_obj:
      if (role == 1 and serv_obj.owner_id != USER and serv_obj.pub == 0):
        # Take the first server from the list
        for c in Servers.objects.all():
          if (c.pub == 1) or (c.owner_id == USER) or role == 0:
            selected_server = c
            break;
    
        if not selected_server:
        # If list is empty then id is not defined
          id_server = None
        else:
          id_server = selected_server.id
      else:
        selected_server = Servers.objects.get(id=slt_server)
        id_server = selected_server.id
    else:
      selected_server = Servers.objects.get(id=slt_server)
      id_server = selected_server.id
  
  # Definition id for set
  
  # If set was not selected
  # or (role == 1 and set_obj.author_id != USER and set_obj.pub == 0)
  if (not slt_set):
    # Take the first set from the list
    for c in LayerSet.objects.all():
      if (c.pub == 1) or (c.author_id == USER) or (role == 0):
        selected_set = c
        break;
    
    if not selected_set:
      # If list is empty then id is not defined
      id_set = None
    else:
      id_set = selected_set.id
  else:
    # If set was selected
    if set_obj:
      if (role == 1 and set_obj.author_id != USER and set_obj.pub == 0):
        # Take the first set from the list
        for c in LayerSet.objects.all():
          if (c.pub == 1) or (c.author_id == USER) or (role == 0):
            selected_set = c
            break;
    
        if not selected_set:
        # If list is empty then id is not defined
          id_set = None
        else:
          id_set = selected_set.id
      else:
        selected_set = LayerSet.objects.get(id=slt_set)
        id_set = selected_set.id
    else:
      selected_set = LayerSet.objects.get(id=slt_set)
      id_set = selected_set.id

  if role == 0:
    root = "true"
  else:
    root = "false"
  # Set that is processed
  set_obj = 0
  if id_set:
    try:
      set_obj = LayerSet.objects.get(id = id_set)
    except:
      set_obj = 0
      slt_set = 0
      errors = "Such a set was not created"

  # Server that is processed
  serv_obj = 0
  if id_server:
    try:
      serv_obj = Servers.objects.get(id = id_server)
    except:
      serv_obj = 0
      slt_server = 0
      errors = "Such a server was not added"
  # If the server has been selected then formed a list of its layers
  if id_server and serv_obj:
    if ((role == 0) or (serv_obj.pub == 1) or (serv_obj.owner_id == USER)):
      cursor.execute("""
                      WITH RECURSIVE tree 
                      AS 
                      (
                        SELECT 
                              name, title, id, parent_id, server_id, pub, NULL::varchar AS parent_name, id::text AS path 
                        FROM 
                              tree_layers
                        WHERE parent_id IS NULL
                        UNION 
                        SELECT 
                              f1.name, f1.title, f1.id, f1.parent_id, f1.server_id, f1.pub, tree.name 
                        AS parent_name, tree.path || '-000-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layers f1 ON f1.parent_id = tree.id)
                        SELECT tree.name, tree.title, tree.id, tree.parent_id, tree.pub, tree.name, tree.path 
                        FROM tree, tree_servers 
                        WHERE tree.server_id = %s and (tree_servers.owner_id = %s or tree.pub = true or %s) and tree_servers.id = tree.server_id
                        ORDER BY tree.path, tree.title;
                   """, (id_server, USER, root))
      layers = cursor.fetchall()
    else:
      layers = None
  else:
    layers = None
  
  # If the set has been selected then formed a list of its layers
  if id_set and set_obj:
    #if (set_obj.pub == 1 or role == 0 or set_obj.author_id == USER):
      cursor.execute("""
                      WITH RECURSIVE tree 
                      AS 
                      (
                        SELECT 
                              name, id, parent_id, lset_id, layer_id, hidden, sld_id, login, NULL::varchar AS parent_name, id::text AS path 
                        FROM 
                              tree_layertree
                        WHERE parent_id IS NULL 
                        UNION 
                        SELECT 
                              f1.name, f1.id, f1.parent_id, f1.lset_id, f1.layer_id, f1.hidden, f1.sld_id, f1.login, tree.name 
                        AS parent_name, tree.path || '-000-'||f1.id::text AS path 
                        FROM 
                              tree 
                        JOIN tree_layertree f1 ON f1.parent_id = tree.id)
                        SELECT tree.name, tree.id, tree.parent_id, tree.lset_id, tree.layer_id, tree.hidden, tree.sld_id, tree.login, tree.name, tree.path 
                        FROM tree, tree_layers, tree_servers
                        WHERE tree.lset_id = %s AND 
                              (
                                (tree.layer_id = tree_layers.id AND tree_layers.server_id = tree_servers.id
                                and (tree_servers.owner_id = %s or (tree_layers.pub = true and tree.login IS NULL) or %s))
                              OR
                                tree.layer_id IS NULL
                              )
                        GROUP BY tree.name, tree.id, tree.parent_id, tree.lset_id, tree.layer_id, tree.hidden, tree.sld_id, tree.login, tree.path
                        ORDER BY tree.path, tree.name;
                  """, (id_set, USER, root))
      layertree = cursor.fetchall()
    #else:
    #  layertree = None
  else:
    layertree = None

  return render_to_response("index.html",
                              { 'MEDIA_URL': MEDIA_URL,
                                'LAYER_SET_BASE_URL': LAYER_SET_BASE_URL%"",
                                'nodes_layers':Layers.tree.all(), 
                                'layers' : layers,
                                'nodes_layertree':LayerTree.tree.all(), 
                                'layertree' : layertree,
                                'sld_objects': SLD.objects.all(),
                                'list_servers': list_servers.widget.render("list_servers", id_server),
                                'list_sets': list_sets.widget.render("list_sets", id_set),
                                'list_sld': list_sld, #.widget.render("list_sld", None),
                                'selected_server':selected_server,
                                'selected_set':selected_set,
                                'name_sets': name_sets,
                                'error_layers': errlayer,
                                'namegroup': namegroup,
                                'errors': errors
                              },
                              context_instance=RequestContext(request)
                            )



