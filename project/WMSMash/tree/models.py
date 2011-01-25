# -*- coding: utf-8 -*-
#

#import mptt
from django.db import models
from django.db import connection, transaction


#######################################
#             SLDManager              #
#######################################
class SLDManager ( models.Manager ) :
  #
  # add: Create new style with name and url.
  def add ( self, name, url ) :
    idsld = 0
    try:
      idsld = self.create(name = name, url = url)
    except:
      transaction.rollback_unless_managed()        
      idsld = self.get(name = name, url = url)
    return idsld
  
  #
  # dell: Delete style with id "idsld".
  def dell ( self, idsld ) :
    cursor = connection.cursor()
    try:
      cursor.execute( '''DELETE FROM tree_sld where id= %s;''', (idsld, ) )
      transaction.commit_unless_managed()
    except:
      transaction.rollback_unless_managed()
  

############################################
#             LayerTreeManager             #
############################################
class LayerTreeManager ( models.Manager ) :
  #
  # add: Create new records in the table tree_layertree. If unless specified 
  #      namelayer then changes the name of the added layer.
  def add ( self, errorLayers, layers, parentLayers, set, cursor, namelayer ) :
    # Determined the max node number within group
    if parentLayers :
      cursor.execute( '''SELECT MAX(ordr) FROM tree_layertree 
                         WHERE parent_id = %s;
                      ''', (parentLayers, ) )
      ordr_max = cursor.fetchone()
      ordr = 0
      if not ordr_max :
        ordr = 0
      elif ordr_max[0] :
        ordr = int(ordr_max[0])
      try:
        parent_obj = self.get( id = parentLayers )
      except:
        transaction.rollback_unless_managed()
        return errorLayers

    counts = 1
    for i in layers :
      error_flag = 0

      layer = 0
      try:
        layer = Layers.objects.get( id = i[0] )
      except:
        transaction.rollback_unless_managed()

      if layer :
        if ( namelayer and (counts == 1) ):
          lname = namelayer
        else:
          lname = layer.name
        
        if parentLayers :
          try:
            newlayer = ( self.create( name = lname, layer_id = int(i[0]),\
                                      parent_id = int(parentLayers),\
                                      hidden = parent_obj.hidden,\
                                      ordr = int(ordr + counts),\
                                      lset_id = int(set) ) ).id
          except:
            transaction.rollback_unless_managed()
            error_flag = 1
            errorLayers.append( (lname, int(parentLayers), int(i[0])) )
        else :
          try:
            newlayer = ( self.create( name = lname, layer_id = int(i[0]),\
                                      hidden = 0,\
                                      ordr = counts, lset_id = int(set) ) ).id
          except:
            transaction.rollback_unless_managed()
            error_flag = 1
            errorLayers.append((lname, 0, int(i[0])))

        counts += 1

        if not error_flag :
          cursor.execute( 'SELECT id from tree_layers where parent_id = %s;', (i[0], ) )
          sublayers = cursor.fetchall()
          if sublayers :
            errorLayers = self.add(errorLayers, sublayers, newlayer, set, cursor, 0)
    
    return errorLayers

  #
  # add_inset: Add several layers of the server or only one layer.
  def add_inset ( self, server, set, layer, parentLayer, namelayer, list_layers, cursor ) :
    if ( server and set ) :
      # Saved a list of included layers
      layers = []
      errorLayers = []

      # If add all the layers of the server
      if (not layer or list_layers == 0) :
        cursor.execute('SELECT id from tree_layers where parent_id IS NULL and server_id = %s;', (server, ))
        layers = cursor.fetchall()

      # If add several layers of the server
      if (layer == -1 and list_layers != 0) :
        if (list_layers == -1) :
          return
        list_layers = list_layers.split(',')
        for i in list_layers :
          ll = (int(i), )
          layers.append(ll)

      # If add only one layer of the servers
      if (layer and layer != -1 and parentLayer) :
        ll = (int(layer), )
        layers.append(ll)

      # If the list includes layers composed
      if layers :
        return self.add(errorLayers, layers, int(parentLayer), set, cursor, namelayer)

  #
  # dellayer: Remove layers from set.
  def dellayer ( self, layers, cursor ) :
    for i in layers :
      cursor.execute( 'SELECT id from tree_layertree where parent_id = %s;', (i[0], ) )
      sublayers = cursor.fetchall()
      self.dellayer(sublayers, cursor)

      layer = self.get( id = i[0] )
      if layer :
        sld = layer.sld_id
      cursor.execute( '''DELETE FROM tree_layertree where id = %s;''', (i[0], ) );
      transaction.commit_unless_managed()

      if sld :
        SLD.objects.dell(sld)

  #
  # del_fromset: Removes the specified layer from the set.
  def del_fromset ( self, currentLayer, cursor ) :
    if currentLayer :
      layers = []
      ll = (int(currentLayer), )
      layers.append(ll)
      self.dellayer(layers, cursor)

  #
  # add_newgroup: Adds a new group in the set of layers.
  def add_newgroup ( self, title_group, parentLayer, set ) :
    if ( set and title_group and (parentLayer != -1) ) :
      if int(parentLayer) :
        cursor = connection.cursor()
        cursor.execute( '''SELECT MAX(ordr) FROM tree_layertree 
                           WHERE parent_id = %s;
                        ''', (parentLayer, ) );
        ordr_max = cursor.fetchone()
        ordr = 0
        if not ordr_max :
          ordr = 0
        elif ordr_max[0] :
          ordr = int(ordr_max[0])
        parentObj = self.get( id = parentLayer )

      if not int(parentLayer) :
        try:
          self.create( name = title_group, hidden = 0, \
                       ordr = 0, lset_id = int(set) \
                      )
        except:
          transaction.rollback_unless_managed()
          return title_group
      elif parentObj :
        try:
          self.create( name = title_group, parent_id = int(parentLayer),\
                       hidden = parentObj.hidden,\
                       ordr = int(ordr + 1), lset_id = int(set) \
                      )
        except:
            transaction.rollback_unless_managed()
            return title_group

    return None

  #
  # hidden: Enables/disables the layers in the set. 
  def hidden ( self, on_off, layers, cursor ) :
    for i in layers :
      layer = self.get( id = int(i[0]) )
      layer.hidden = on_off
      layer.save()
      cursor.execute( 'SELECT id from tree_layertree where parent_id = %s;', (i[0], ) )
      sublayers = cursor.fetchall()
      if sublayers :
        self.hidden(on_off, sublayers, cursor)

  #
  # pub: Function to identify and remove a password. Setting a password is 
  #      available either for individual layers.
  def pub ( self, on_off, idlayer, login, passwd ) :
    layer = self.get( id = int(idlayer) )
    if (on_off == 1) :
      if ( (layer.login == login) and (layer.passwd == passwd) ) :
        layer.login = None
        layer.passwd = None
        layer.pub = on_off
        layer.save()
    else :
      layer.login = login
      layer.passwd = passwd
      layer.pub = on_off
      layer.save()

  #
  # addstyle: Adds style SLD to the layer.
  def addstyle ( self, currentLayer, name, url ) :
    if (currentLayer and name and url) :
      idsld = SLD.objects.add(name, url)
      layer = self.get( id = currentLayer )
      layer.sld = idsld
      layer.save()

  #
  # delstyle: Removes   a style SLD of the layer.
  def delstyle ( self, currentLayer ) :
    if currentLayer :
      layer = self.get( id = currentLayer )
      idsld = layer.sld_id
      if idsld :
        layer.sld_id = None
        layer.save()
        SLD.objects.dell(int(idsld))


###########################################
#             LayerSetManager             #
###########################################
class LayerSetManager ( models.Manager ) :
  #
  # add_newset: Creates a new set of layers. By default, th new set is available
  #             to all users.
  def add_newset (self, name, title, abstract, keywords, user ) :
    try:
      setObj = self.create( name = name, title = title, abstract = abstract,\
                         author_id = user, pub = 1\
                        )
    except:
      transaction.rollback_unless_managed()
      setObj = 0
    return setObj

  #
  # edit_set: Edit the parametrs set.
  def edit_set ( self, set, name, title, abstract, keywords, user ) :
    setObj = self.get( id = set )
    setObj.name = name;
    setObj.title = title;
    setObj.abstract = abstract;
  #  set_obj.pub = spub;
  #  set_obj.keywords = skeywords;
    try:
      setObj.save()
      return 0
    except:
      transaction.rollback_unless_managed()
      return 1

  #
  # del_set: Removes a set with all the layers.
  def del_set ( self, set, cursor ) :
    cursor.execute( '''SELECT id from tree_layertree 
                       WHERE parent_id IS NULL and lset_id = %s;
                    ''', (set, ) )
    layers = cursor.fetchall()
    LayerTree.objects.dellayer(layers, cursor)

    cursor.execute( 'DELETE FROM tree_layerset where id = %s;', (set, ) )
    transaction.commit_unless_managed()


###########################################
#             ServersManager              #
###########################################
class ServersManager ( models.Manager ) :
  #
  # add: Adds a new resource.
  def add ( self, server ) :
    URL = server[5:]
    #parser

  #
  # editURL: Changes the URL of the resource.
  def editURL ( self, server, serverURL ) :
    URL = serverURL[5:]
    serverObj = self.get( id = server )
    serverObj.url = URL
    serverObj.save()

  #
  # update: Update resource.
  def update ( self, server ) :
    if server :
      serverObj = self.get( id = server )
      if serverObj:
        URL = serverObj.url
        #parser

  # delete: Deletes a resource with all its layers.
  def delete ( self, server, cursor ) :
    cursor.execute( """
                       SELECT tree_layerset.name 
                       FROM tree_layers, tree_layerset, tree_layertree, tree_servers 
                       WHERE tree_servers.id = tree_layers.server_id  
                       AND tree_layers.server_id = %s 
                       AND tree_layertree.layer_id = tree_layers.id 
                       GROUP BY tree_layerset.name;
                     """, (server, ) )
    list_sets = cursor.fetchall()
    if not list_sets :
      cursor.execute( '''
                         SELECT id from tree_layers 
                         WHERE server_id = %s and parent_id IS NULL;
                      ''', (server, ) )
      layers = cursor.fetchall()
      errorLayers = 0
    
      if layers :
        errorLayers = Layers.objects.delete_layers(layers, cursor)
    
      if not errorLayers :
        cursor.execute( '''DELETE FROM tree_servers where id = %s;''', (server, ) )
        transaction.commit_unless_managed()
      return errorLayers
    else :
      return list_sets


#########################################
#             LayersManager             #
#########################################
class LayersManager ( models.Manager ) :
  #
  # delete_layers: Removes the list of layers.
  def delete_layers ( self, layers, cursor ) :
    for i in layers :
      cursor.execute( '''SELECT tree_layerset.name
                         FROM tree_layerset, tree_layertree 
                         WHERE tree_layertree.layer_id = %s 
                         and tree_layertree.lset_id = tree_layerset.id;
                      ''', (i[0], ) )
      list_sets = cursor.fetchall()
      if list_sets :
        return list_sets
      else :
        cursor.execute( 'SELECT id from tree_layers where parent_id = %s;', (i[0], ) )
        sublayers = cursor.fetchall()
        if sublayers :
          errorLayers = self.delete_layers(sublayers, cursor)
          if errorLayers :
            return errorLayers

        cursor.execute( '''DELETE FROM tree_layers where id = %s;''', (i[0], ) );
        transaction.commit_unless_managed()


#################################
#             Users             #
#################################
class Users ( models.Model ) :
  username = models.CharField(max_length = 20, unique = True)
  pwdhash  = models.CharField(max_length = 20, unique = True)
  email    = models.CharField(max_length = 28, unique = True)
  role     = models.IntegerField(null = True, blank = True)

  def __unicode__(self):
    return self.username


###################################
#             Servers             #
###################################
class Servers ( models.Model ) :
  name  = models.CharField(max_length = 200, unique = True, null = True, blank = True)
  title = models.CharField(max_length = 200, unique = True)
  url   = models.CharField(max_length = 1024, unique = True)
  capabilites = models.TextField(null = True, blank = True)
  login  = models.CharField(max_length = 20, unique = True, null = True, blank = True)
  passwd = models.CharField(max_length = 128, unique = True, null = True, blank = True)
  owner  = models.ForeignKey(Users)
  pub    = models.NullBooleanField(null = True, blank = True)
  nwms   = models.IntegerField(null = True, blank = True)
  
  objects = ServersManager()
  
  def __unicode__(self):
    return self.name


##################################
#             Layers             #
##################################
class Layers ( models.Model ) :
  server = models.ForeignKey(Servers)
  name   = models.CharField(max_length = 128, unique = True)
  title  = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField(null = True, blank = True)
  keywords = models.TextField(null = True, blank = True)
  latlngbb = models.TextField(null = True, blank = True)
  capabilites = models.TextField()
  pub = models.BooleanField()
  parent    = models.ForeignKey('self', null = True, blank = True, related_name = 'children')
  layer     = models.IntegerField(null = True, blank = True)
  nl_group  = models.IntegerField(null = True, blank = True)
  available = models.BooleanField()
  
  objects = LayersManager()
  
  def __unicode__(self):
    return self.name


####################################
#             LayerSet             #
####################################
class LayerSet ( models.Model ) :
  name     = models.CharField(max_length = 32, unique = True)
  title    = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField(null = True, blank = True)
  #keywords = models.TextField(null = True, blank = True)
  author = models.ForeignKey(Users)
  pub    = models.BooleanField()
  login  = models.CharField(max_length = 20, unique = True, null = True, blank = True)
  passwd = models.CharField(max_length = 128, unique = True, null = True, blank = True)  
  
  objects = LayerSetManager()
    
  def __unicode__(self):
    return self.name


###############################
#             SLD             #
###############################
class SLD ( models.Model ) :
  name  = models.CharField(max_length = 32, unique = True)
  url   = models.CharField(max_length = 1024, unique = True)
  owner = models.ForeignKey(Users, null = True, blank = True)
  
  objects =  SLDManager()
  
  def __unicode__(self):
    return self.name


#####################################
#             LayerTree             #
#####################################
class LayerTree ( models.Model ) :
  name   = models.CharField(max_length = 32, unique = True, null = True, blank = True)
  layer  = models.ForeignKey(Layers, null = True, blank = True)
  lset   = models.ForeignKey(LayerSet)
  ordr   = models.IntegerField()
  hidden = models.BooleanField()
  parent = models.ForeignKey('self', null = True, blank = True, related_name = 'children')
  sld    = models.ForeignKey(SLD, null = True, blank = True)
  login  = models.CharField(max_length = 20, unique = True, null = True, blank = True)
  passwd = models.CharField(max_length = 128, unique = True, null = True, blank = True)  

  objects =  LayerTreeManager()

  def __unicode__(self):
    return self.name



