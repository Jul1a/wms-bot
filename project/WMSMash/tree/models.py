# -*- coding: utf-8 -*-
#

from django.db import models
from mptt.models import MPTTModel
from django.contrib.auth.models import User, UserManager
from django.conf import settings
import mptt
from django import forms
from django.core import validators
from django.db import connection, transaction


class SLDManager(models.Manager):
  def add(self, name, url):
    idsld = 0
    try:
      idsld = self.create(name = name, url = url)
    except:
      transaction.rollback_unless_managed()        
      idsld = self.get(name = name, url = url)
    return idsld

  def dell(self, idsld):
    cursor = connection.cursor()
    try:
      cursor.execute('''DELETE FROM tree_sld where id= %s;''', (idsld, ));
      transaction.commit_unless_managed()
    except:
      transaction.rollback_unless_managed()        

class LayerTreeManager(models.Manager):
  def add(self, err_layer, layers, lparent, set, cursor, namelayer):
    if lparent:
      cursor.execute('''SELECT MAX(ordr) FROM tree_layertree where parent_id = %s;''', (lparent, ));
      tmp = cursor.fetchone()
      if not tmp:
        ordr_max = 0
      else:
        if not tmp[0]:
          ordr_max = 0
        else:
          ordr_max = int(tmp[0])
      parent_obj = self.get(id = lparent)
    counts = 1;
    err_name = ""
    err_parent = 0
    err_layerid = 0

    for i in layers:
      layer_obj = 0
      err_flag = 0
      try:
        layer_obj = Layers.objects.get(id = i[0])
      except:
        transaction.rollback_unless_managed()
      if(layer_obj):
        if namelayer and (counts == 1):
          lname = namelayer
        else:
          lname = layer_obj.name
        if lparent:
          try:
            parent = (self.create(name = lname, layer_id = int(i[0]),\
                                   parent_id = int(lparent), hidden = parent_obj.hidden,\
                                   ordr = int(ordr_max + counts), lset_id = int(set),\
                                   lft = 0, rght = 0, tree_id=0, level=0\
                                   )).id;
          except:
            transaction.rollback_unless_managed()
            err_flag = 1
            err_name = lname
            err_parent = int(lparent)
            err_layerid = int(i[0])
            err_layer.append((err_name, err_parent, err_layerid))
            #return lname, lparent, int(i[0])
        else:
          try:
            parent = (self.create(name = lname, layer_id = int(i[0]),\
                                   hidden = 0,\
                                   ordr = counts, lset_id = int(set),\
                                   lft = 0, rght = 0, tree_id=0, level=0\
                                   )).id;
          except:
            transaction.rollback_unless_managed()
            err_flag = 1
            err_name = lname
            err_parent = 0
            err_layerid = int(i[0])
            err_layer.append((err_name, err_parent, err_layerid))
            #return lname, 0, int(i[0])
        counts += 1
        if not err_flag:
          cursor.execute('SELECT id from tree_layers where parent_id = %s;', (i[0], ))
          all_sublayer = cursor.fetchall()
          if all_sublayer:
            err_layer = self.add(err_layer, all_sublayer, parent, set, cursor, 0)
    
    return err_layer

  def add_inset(self, list_server, list_set, layer, set_layer, namelayer, list_layers, cursor):
    if(list_server and list_set):
      layers = []
      err_layer = []
      if not layer or list_layers == 0:
        cursor.execute('SELECT id from tree_layers where parent_id IS NULL and server_id = %s;', (list_server, ))
        layers = cursor.fetchall()
      if layer == -1 and list_layers != 0:
        if list_layers == -1:
          return
        list_layers = list_layers.split(',')
        for i in list_layers:
          ll = (int(i), )
          layers.append(ll)
      if(layer and layer != -1 and set_layer):
        ll = (int(layer), )
        layers.append(ll)

      if layers:
        return self.add(err_layer, layers, int(set_layer), list_set, cursor, namelayer)

  def dellayer(self, layers, cursor):
    for i in layers:
      cursor.execute('SELECT id from tree_layertree where parent_id = %s;', (i[0], ))
      all_sublayer = cursor.fetchall()
      self.dellayer(all_sublayer, cursor)
      layer_obj = self.get(id = i[0])
      if layer_obj:
        sld = layer_obj.sld_id
      cursor.execute('''DELETE FROM tree_layertree where id= %s;''', (i[0], ));
      transaction.commit_unless_managed()
      if sld:
        SLD.objects.dell(sld)

  def del_fromset(self, set_layer, cursor):
    if set_layer:
      layers = []
      ll = (int(set_layer), )
      layers.append(ll)
      self.dellayer(layers, cursor)

  def add_newgroup(self, title_group, lparent, list_set):
    if(list_set and title_group and (lparent != -1)):
      if int(lparent):
        cursor = connection.cursor()
        cursor.execute('''SELECT MAX(ordr) FROM tree_layertree where parent_id = %s;''', (lparent, ));
        tmp = cursor.fetchone()
        if not tmp:
          ordr_max = 0
        else:
          if not tmp[0]:
            ordr_max = 0
          else:
            ordr_max = int(tmp[0])
        parent_obj = self.get(id = lparent)
      if not int(lparent):
        try:
          self.create(name = title_group, \
                      hidden = 0, \
                      ordr = 0, lset_id = int(list_set),\
                      lft = 0, rght = 0, tree_id=0, level=0\
                      )
        except:
          transaction.rollback_unless_managed()
          return title_group
      else:
        try:
          self.create(name = title_group,\
                      parent_id = int(lparent), hidden = parent_obj.hidden,\
                      ordr = int(ordr_max + 1), lset_id = int(list_set),\
                      lft = 0, rght = 0, tree_id=0, level=0\
                      )
        except:
            transaction.rollback_unless_managed()
            return title_group

    return None

  def hidden(self, hdd, layers, cursor):
    for i in layers:
      layer_obj = self.get(id=int(i[0]))
      layer_obj.hidden = hdd
      layer_obj.save()
      cursor.execute('SELECT id from tree_layertree where parent_id = %s;', (i[0], ))
      all_layers = cursor.fetchall()
      if all_layers:
        self.hidden(hdd, all_layers, cursor)
  
  def pub(self, flpub, layer, login, passwd):
    layer_obj = self.get(id=int(layer))
    if flpub == 1:
      if (layer_obj.login == login and layer_obj.passwd == passwd):
        layer_obj.login = None
        layer_obj.passwd = None
        layer_obj.pub = flpub
        layer_obj.save()
    else:
      layer_obj.login = login
      layer_obj.passwd = passwd
      layer_obj.pub = flpub
      layer_obj.save()

  def addstyle(self, set_layer, name, url):
    if (set_layer and name and url):
      idsld = SLD.objects.add(name, url)
      layerinset = self.get(id = set_layer)
      layerinset.sld = idsld
      layerinset.save()
  
  def delstyle(self, set_layer):
    if set_layer:
      layerinset = self.get(id = set_layer)
      idsld = layerinset.sld_id
      if idsld:
        layerinset.sld_id = None
        layerinset.save()
        SLD.objects.dell(int(idsld))
    
class LayerSetManager(models.Manager):
  def add_newset(self, sname, stitle, sabstract, skeywords, susers):
    try:
      set = self.create(name = sname, title = stitle, abstract = sabstract,\
                author_id = susers, pub = 1\
                )
    except:
      transaction.rollback_unless_managed()
      set = 0
    return set
    
  def edit_set(self, list_set, sname, stitle, sabstract, skeywords, susers):
    set_obj = self.get(id = list_set)
    set_obj.name = sname;
    set_obj.title = stitle;
    set_obj.abstract = sabstract;
  #  set_obj.pub = spub;
  #  set_obj.keywords = skeywords;
    try:
      set_obj.save()
      return 0
    except:
      transaction.rollback_unless_managed()
      return 1

  def del_set(self, list_set, cursor):
    cursor.execute('SELECT id from tree_layertree where parent_id IS NULL and lset_id = %s;', (list_set, ))
    layers = cursor.fetchall()
    LayerTree.objects.dellayer(layers, cursor)
    cursor.execute('''DELETE FROM tree_layerset where id = %s;''', (list_set, ));
    transaction.commit_unless_managed()

class ServersManager(models.Manager):
  def add(self, server):
    URL = server[5:]
    #parser

  def editURL(self, list_set, servers):
    URL = servers[5:]
    server = self.get(id = list_set)
    server.url = URL
    server.save()

  def update(self, server):
    if server:
      server_obj = self.get(id = server)
      if server_obj:
        URL = server_obj.url
        #parser

  def delete(self, server, cursor):
    cursor.execute("""SELECT tree_layerset.name 
                       FROM tree_layers, tree_layerset, tree_layertree, tree_servers 
                       WHERE tree_servers.id = tree_layers.server_id  
                       AND tree_layers.server_id = %s 
                       AND tree_layertree.layer_id = tree_layers.id GROUP BY tree_layerset.name
                       ;
                    """, (server, ))
    lists = cursor.fetchall()
    if not lists:
      cursor.execute('SELECT id from tree_layers where server_id = %s and parent_id IS NULL;', (server, ))
      layers = cursor.fetchall()
      name_sets = 0
      if layers:
        name_sets = Layers.objects.delete_layers(layers, cursor)
      if not name_sets:
        cursor.execute('''DELETE FROM tree_servers where id = %s;''', (server, ));
        transaction.commit_unless_managed()
      return name_sets
    else:
      return lists

class LayersManager(models.Manager):
  def delete_layers(self, layers, cursor):
    for i in layers:
      cursor.execute('''SELECT tree_layerset.name
                        FROM tree_layerset, tree_layertree 
                        WHERE tree_layertree.layer_id = %s and tree_layertree.lset_id = tree_layerset.id;''', (i[0], ))
      name = cursor.fetchall()
      if name:
        return name
      else:
        k = 0
        cursor.execute('SELECT id from tree_layers where parent_id = %s;', (i[0], ))
        allayers = cursor.fetchall()
        if allayers:
          name = self.delete_layers(allayers, cursor)
          if name:
            return name
        cursor.execute('''DELETE FROM tree_layers where id = %s;''', (i[0], ));
        transaction.commit_unless_managed()
    

class ObjectPermission(models.Model):
  user = models.ForeignKey(User)


class Users(models.Model):
  username = models.CharField(max_length = 20, unique = True)
  pwdhash = models.CharField(max_length = 20, unique = True)
  email = models.CharField(max_length = 28, unique = True)
  role = models.IntegerField(null=True, blank=True)
  def __unicode__(self):
    return self.username


class Servers(models.Model):
  name = models.CharField(max_length = 200, unique = True, null=True, blank=True)
  title = models.CharField(max_length = 200, unique = True)
  url = models.CharField(max_length = 1024, unique = True)
  capabilites = models.TextField(null=True, blank=True)
  login = models.CharField(max_length = 20, unique = True, null=True, blank=True)
  passwd = models.CharField(max_length = 128, unique = True, null=True, blank=True)
  owner = models.ForeignKey(Users)
  pub = models.NullBooleanField(null=True, blank=True)
  nwms = models.IntegerField(null=True, blank=True)
  
  objects = ServersManager()
  
  def __unicode__(self):
    return self.name

class Layers(MPTTModel):

  server = models.ForeignKey(Servers)
  name = models.CharField(max_length = 128, unique = True)
  title = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField(null=True, blank=True)
  keywords = models.TextField(null=True, blank=True)
  latlngbb = models.TextField(null=True, blank=True)
  capabilites = models.TextField()
  pub = models.BooleanField()

  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
  layer = models.IntegerField(null=True, blank=True)
  nl_group = models.IntegerField(null=True, blank=True)
  available = models.BooleanField()
  
  objects = LayersManager()
  
  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name

class LayerSet(models.Model):
  name = models.CharField(max_length = 32, unique = True)
  title = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField(null=True, blank=True)
  #keywords = models.TextField(null=True, blank=True)
  author = models.ForeignKey(Users)
  pub = models.BooleanField()
  login = models.CharField(max_length = 20, unique = True, null=True, blank=True)
  passwd = models.CharField(max_length = 128, unique = True, null=True, blank=True)  
  
  objects = LayerSetManager()
    
  def __unicode__(self):
    return self.name
  

class SLD(models.Model):
  name = models.CharField(max_length = 32, unique = True)
  url = models.CharField(max_length = 1024, unique = True)
  owner = models.ForeignKey(Users, null=True, blank=True)
  
  objects =  SLDManager()
  
  def __unicode__(self):
    return self.name

class LayerTree(MPTTModel):
  name = models.CharField(max_length = 32, unique = True, null=True, blank=True)
  layer = models.ForeignKey(Layers, null=True, blank=True)
  lset = models.ForeignKey(LayerSet)
  ordr = models.IntegerField()
  hidden = models.BooleanField()
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
  sld = models.ForeignKey(SLD, null=True, blank=True)
  login = models.CharField(max_length = 20, unique = True, null=True, blank=True)
  passwd = models.CharField(max_length = 128, unique = True, null=True, blank=True)  

  objects =  LayerTreeManager()

  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name



