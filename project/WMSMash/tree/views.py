# -*- coding: utf-8 -*-
#

from django import forms
from django.db import connection

from django.http import HttpResponseRedirect
from django.forms import ChoiceField

from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_protect

from settings import MEDIA_URL, LAYER_SET_BASE_URL

from models import Users, Servers, Layers, LayerSet, SLD, LayerTree


###########################
#        login            #
###########################
def login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
  
    user = auth.authenticate(username = username, password = password)
    if user is not None and user.is_active:
    # Correct password, and the user is marked "active"
      auth.login(request, user)
      # Redirect to a success page.
      return HttpResponseRedirect("/")
    else:
      # Show an error page
      return render_to_response("registration/login.html",
                                {
                                  'MEDIA_URL' : MEDIA_URL,
                                  'errors'    : 1
                                },
                                context_instance = RequestContext(request)
                               )
  else:
    return render_to_response("registration/login.html",
                              {
                                'MEDIA_URL' : MEDIA_URL
                              },
                              context_instance = RequestContext(request)
                             )


###########################
#        logout_view      #
###########################
def logout_view(request):
  logout(request)
  return HttpResponseRedirect("/accounts/login/")


###########################
#        register         #
###########################
@csrf_protect
def register(request):

  if request.method == 'POST':
    username = request.POST.get('username', 0)
    email    = request.POST.get('email', 0)
    passwd1  = request.POST.get('password1', 0)
    passwd2  = request.POST.get('password2', 0)
    role = request.POST.get('role', 0)
    profile = request.user
    
    if (passwd1 != passwd2) or (not username):
      return render_to_response("registration/register.html",
                                {
                                  'MEDIA_URL' : MEDIA_URL,
                                  'role' : role
                                },
                                context_instance = RequestContext(request)
                               )
    else:
      user = auth.authenticate(username = username, password = passwd1, email = email)

      if user is not None:
        return HttpResponseRedirect("/accounts/login/")
      else:
        try:
          user = User.objects.create_user(username = username, password = passwd1, email = email)
        except:
          return render_to_response("registration/register.html",
                                    {
                                      'MEDIA_URL' : MEDIA_URL,
                                      'errors'    : "A user with that name already exists"
                                    },
                                    context_instance = RequestContext(request)
                                    )
        if profile:
          if role and profile.is_superuser:
            user.is_superuser = True
        user.is_active = True
        user.save()
        if profile:
          if role and profile.is_superuser:
            Users.objects.create(id = user.id, username = user.username, pwdhash = user.password, email = user.email, role = 0)
            return HttpResponseRedirect("/")

        Users.objects.create(id = user.id, username = user.username, pwdhash = user.password, email = user.email, role = 1)
        return HttpResponseRedirect("/accounts/login/")
  else:
    profile = request.user
    role = 0
    if profile:
      if profile.is_superuser:
          role = 1
    return render_to_response("registration/register.html",
                              {
                               'MEDIA_URL' : MEDIA_URL,
                               'role'      : role
                              },
                              context_instance = RequestContext(request)
                              )



###########################
#        show_page        #
###########################
@csrf_protect
@login_required
def show_page ( request ) :
  cursor = connection.cursor()

  # User running the application
  profile = request.user #.get_profile()

  USER = profile.id

  # User rights
  if profile.is_superuser:
    user_role = 0
  else:
    user_role = 1
  
  # Definition of the selected server and set of layers
  select_server = request.POST.get( 'list_servers', 0 )
  select_set    = request.POST.get( 'list_sets', 0 )

  # Stores list of sets that have layers from removed the server
  name_sets = 0
  
  # Stores the name of the group that failed to create
  namegroup = 0
  
  # Saved a list of layers which couldn't be inserted into a set of layers
  errorLayers = "" 

  # Stores error messages
  error_message = ""
  
  # Set that is processed
  setObj = 0
  if select_set :
    try:
      setObj = LayerSet.objects.get( id = select_set )
      if ( (user_role == 1) and (setObj.author_id != USER) and (setObj.pub == 0) ) :
        setObj = 0
        select_set = 0
    except:
      setObj = 0
      select_set = 0
      error_message = "Such a set was not created"

  # Server that is processed
  serverObj = 0
  if select_server :
    try:
      serverObj = Servers.objects.get( id = select_server )
      if ( (user_role == 1) and (serverObj.owner_id != USER) and (serverObj.pub == 0) ) :
        serverObj = 0
        select_server = 0
    except:
      serverObj = 0
      select_server = 0
      error_message = "Such a server was not added"


  ###################################################
  # Operations with layers of virtual set of layers #
  ###################################################

  op = request.POST.get( 'oprt', 0 )

  # Layer in set that is processed
  currentLayer = request.POST.get( 'set_layer', -1 )
  
  if ( op and (currentLayer != -1) and setObj ) :
    # Operation of adding a layers in a virtual set of layers
    if ( (op == 'add') and (setObj.author_id == USER or setObj.pub == 1 or user_role == 0) ) :
      layer       = request.POST.get( 'layer', -1 )
      namelayer   = request.POST.get( 'namelayer', 0 )
      list_layers = request.POST.get( 'layers', -1 )
      try:
        listlayers = int(list_layers)
      except:
        listlayers = list_layers
      error = LayerTree.objects.add_inset(select_server, select_set, layer, currentLayer, namelayer, listlayers, cursor)
      if not error : 
        errorLayers = ""
      else :
        for i in error :
          errorLayers += "%s ?end %d %d;"%(i[0], i[1], i[2]) # (name, parent, layer_id)
    
    # Operation of deleting a layers in a virtual set of layers #or (setObj.pub == 1)
    if ( (op == 'del') and ( (setObj.author_id == USER) or (user_role == 0) ) ) :
      LayerTree.objects.del_fromset(currentLayer, cursor)
    elif (op == 'del') and (setObj.pub == 1):
      error_message = "This layers of set can remove only the owner"
    
    # Operation of off hidden layers
    if ( (op == 'hidd_off') and currentLayer and ( (setObj.author_id == USER) or (setObj.pub == 1) or (user_role == 0) ) ) :
      layers = []
      if (currentLayer == -1) :
        ll = (0, )
      else :
        ll = (int(currentLayer), )
      layers.append(ll)
      LayerTree.objects.hidden(1, layers, cursor)
    
    # Operation of on hidden layers 
    if ( (op == 'hidd_on') and currentLayer and (setObj.author_id == USER or setObj.pub == 1 or user_role == 0) ) :
      layers = []
      if ( currentLayer == -1 ) :
        ll = (0, )
      else :
        ll = (int(currentLayer), )
      layers.append(ll)
      LayerTree.objects.hidden(0, layers, cursor)
    
    # Operation of adding style to a layer of a set
    if ( (op == 'add_style') and ( (setObj.author_id == USER) or (setObj.pub == 1) or (user_role == 0) ) ) :
      name = request.POST.get( 'namelayer', 0 )
      url  = request.FILES
      file = 0
      if 'sld' in url:
        file = request.FILES['sld']
      else:
        file = request.POST.get( 'sld', 0 )
      
      if LayerTree.objects.addstyle(currentLayer, name, file, setObj.name, USER) == -1:
        error_message = "Error add style, please add other name style"
    
    # Operation of deleting style to a layer of a set
    if ( (op == 'del_style') and ( (setObj.author_id == USER) or (setObj.pub == 1) or (user_role == 0) ) ) :
      LayerTree.objects.delstyle(currentLayer)
    
    # Operation off the layer of publicity #or (setObj.pub == 1) 
    if ( (op == 'pub_off') and ( (setObj.author_id == USER) or (user_role == 0) ) ) :
      login     = request.POST.get( 'login', -1 )
      passwd    = request.POST.get( 'passwd', -1 )
      currentLayer = request.POST.get( 'set_layer', -1 )
      if ( (int(currentLayer) == 0) and login and passwd ) :
        setObj.pub = 0
        setObj.login = login
        setObj.passwd = passwd
        setObj.save()
      if ( int(currentLayer) and login and passwd ) :
        LayerTree.objects.pub(0, currentLayer, login, passwd)
    else:
      if (op == 'pub_off') and (setObj.pub == 1) :
        error_message = "This layer can be sealed to access only the owner"
    
    if ( (op == 'pub_on') and ( (setObj.author_id == USER) or (user_role == 0) ) ) :
      if ( (int(currentLayer) == 0) ) :
          setObj.pub = 1
          setObj.login = None
          setObj.passwd = None
          setObj.save()
      if int(currentLayer) :
        LayerTree.objects.pub(1, currentLayer, None, None)
    else:
      if (op == 'pub_on') and(setObj.pub == 1) :
        error_message = "This layer can be opened for access only by the owner"
  else:
    if setObj:
      # Operation of adding a new group in set of layers 
      title_group = request.POST.get( 'title_group', 0 )
      if ( title_group and (setObj.author_id == USER or setObj.pub == 1 or user_role == 0) ) :
        parentLayer  = request.POST.get( 'where_layer', -1 )
        list_sets = request.POST.get( 'list_sets', 0 )
        namegroup = LayerTree.objects.add_newgroup(title_group, parentLayer, list_sets, cursor)


    #############################
    # Operations managment sets #
    #############################
  
    # Operation to create a new set of layers
    addset = request.POST.get('add_set', 0)
    if addset:
      name = request.POST.get('name_set', 0)
      title = request.POST.get('title_set', 0)
      abstr = request.POST.get('abstract_set', 0)
      keywords = request.POST.get('keywords_set', 0)
      #spub = int(request.POST.get('pub_set', 0))
      newset = LayerSet.objects.add_newset(name, title, abstr, keywords, USER)
      if newset:
        select_set = newset.id
        setObj = newset
      else:
        error_message = "You have already created a set with the name \"%s\"" % name

    # Operation of editing a describe set of layers
    editset = request.POST.get( 'edit_set', 0 )
    if ( editset and setObj ) :
      sname  = request.POST.get( 'name_set', 0 )
      stitle = request.POST.get( 'title_set', 0 )
      sabstr = request.POST.get( 'abstract_set', 0 )
      skeywords = request.POST.get( 'keywords_set', 0 )
      #spub = request.POST.get( 'pub_set', 0 )
      if ( (setObj.author_id == USER) or (user_role == 0) ) :
        set = LayerSet.objects.edit_set(select_set, sname, stitle, sabstr, skeywords, USER)
        if ( set == 1 ) :
          error_message = "You have already created a set with the name \"%s\"" % sname
      else :
        error_message = "This set can edit only the owner"
  
    # Operation of remove a set of layers
    delset = request.POST.get( 'delete_set', 0 )
    if ( delset and setObj ) :
      if ( (setObj.author_id == USER) or (user_role == 0) ) :
        LayerSet.objects.del_set(select_set, cursor)
        select_set = 0
        setObj = 0
      else:
        error_message = "This set can be removed only by the owner"


    ################################
    # Operations managment servers #
    ################################
      
    # Operation to add, edit the URL and update server
    servers = request.POST.get( 'add_server', 0 )
    if servers :
      if ( servers.find('add_') == 0 ) :
        serverName = request.POST.get( 'serv_name', 0 )
        serverTitle = request.POST.get( 'serv_title', 0 )
        Servers.objects.add(servers, serverName, serverTitle)
      if ( (servers.find('edit_') == 0) and (serverObj) ) :
        if ( (serverObj.owner_id == USER) or (user_role == 0) ) :
          serverName = request.POST.get( 'serv_name', 0 )
          serverTitle = request.POST.get( 'serv_title', 0 )
          serverObj = Servers.objects.editURL(select_server, servers, serverName, serverTitle)
        else:
          error_message = "URL of this server can edit only the resource owner"
      if ( (servers == 'update') and (serverObj) ) :
        if ( (serverObj.owner_id == USER) or (user_role == 0) ) :
          Servers.objects.update(select_server)
        else:
          error_message = "URL of this server can update only the resource owner"
      
    # Operation of remove server
    delserv = request.POST.get( 'delete_server', 0 )
    if ( delserv and serverObj ) :
      if ( (serverObj.owner_id == USER) or (user_role == 0) ) :
        name_sets = Servers.objects.delete(select_server, cursor)
        if not name_sets :
          select_server = 0
          serverObj = 0
      else:
        error_message = "This server can only delete the resource owner"


  ###################################
  # Formation of the displayed page #
  ###################################

  # Formed a list of servers with class = "select_style", value = Servers.id, id = "list_servers"
  BIG_CHOICES = []
  for c in Servers.objects.all() :
    if ( (c.owner_id == USER) or (c.pub == 1) or (user_role == 0) ):
      BIG_CHOICES.append( ( c.id, "(%s(%s" % (c.title, c.name) ) )

  list_servers = forms.ChoiceField( choices = BIG_CHOICES,
                                    required = False,
                                    label = '',
                                    widget = forms.Select({'class':'select_style', 
                                                           'id': 'list_servers'
                                                          }),
                                    ) 
  
  # Formed a list of sets with class = "select_style", value = LayerSet.id, id = "list_sets"
  BIG_CHOICES = []
  for c in LayerSet.objects.all() :
    if ( (c.author_id == USER) or (c.pub == 1) or (user_role == 0) ) :
      BIG_CHOICES.append( ( c.id, "(%s(%s" % (c.title, c.name) ) )

  list_sets = forms.ChoiceField( choices = BIG_CHOICES,
                                 required = False,
                                 label = '',
                                 widget=forms.Select({'class':'select_style', 
                                                      'id': 'list_sets'
                                                      }),
                                 )
  
  # Formed a list of SLD with class = "select_small", value = SLD.id, id = "list_sld"
  list_sld = []
  for c in SLD.objects.all() :
    if ( (c.owner_id == USER) or (not c.owner_id) or (user_role == 0) ) :
      list_sld.append( "%s(%s)" % (c.name, c.url) )

  # If server was not selected
  if (not serverObj) :
    # Take the first server from the list
    select_server = None
    for c in Servers.objects.all() :
      if ( (c.pub == 1) or (c.owner_id == USER) or (user_role == 0) ) :
        serverObj = c
        select_server = serverObj.id
        break

  # If set was not selected
  if (not setObj) :
    # Take the first set from the list
    select_set = None
    for c in LayerSet.objects.all() :
      if ( (c.pub == 1) or (c.author_id == USER) or (user_role == 0) ) :
        setObj = c
        select_set = setObj.id
        break

  if ( user_role == 0 ) :
    root = "true"
  else :
    root = "false"

  # If the server has been selected then formed a list of its layers
  tree_layers = None
  if ( serverObj ) :
    if ( (user_role == 0) or (serverObj.pub == 1) or (serverObj.owner_id == USER) ) :
      cursor.execute( """
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
                      """, (select_server, USER, root) )
      tree_layers = cursor.fetchall()
  
  # If the set has been selected then formed a list of its layers
  tree_layertree = None
  if ( setObj ) :
    cursor.execute( """
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
                        FROM tree, tree_layers, tree_layerset
                        WHERE tree.lset_id = %s AND 
                              (
                                (tree.layer_id = tree_layers.id AND tree.lset_id = tree_layerset.id
                                and (tree_layerset.author_id = %s or (tree_layers.pub = true and tree.login IS NULL) or %s))
                              OR
                                tree.layer_id IS NULL
                              )
                        GROUP BY tree.name, tree.id, tree.parent_id, tree.lset_id, tree.layer_id, tree.hidden, tree.sld_id, tree.login, tree.path
                        ORDER BY tree.path, tree.name;
                      """, (select_set, USER, root) )
    tree_layertree = cursor.fetchall()

  return render_to_response( "index.html",
                            { 
                              'role': user_role,
                              'userName' : profile.username,
                              'userEmail': profile.email,
                              'LAYER_SET_BASE_URL': LAYER_SET_BASE_URL%"",
                              'MEDIA_URL'         : MEDIA_URL,
                              'list_servers': list_servers.widget.render("list_servers", select_server),
                              'list_sets'   : list_sets.widget.render("list_sets", select_set), 
                              'layers'    : tree_layers,
                              'layertree' : tree_layertree,
                              'list_sld'  : list_sld, 
                              'selected_server': serverObj,
                              'selected_set'   : setObj,
                              'name_sets'   : name_sets,
                              'error_layers': errorLayers,
                              'namegroup'   : namegroup,
                              'errors'      : error_message
                            },
                             context_instance = RequestContext(request)
                          )


