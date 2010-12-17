from django.db import models
from mptt.models import MPTTModel
from django.contrib.auth.models import User, UserManager
from django.conf import settings
import mptt
from django import forms
from django.core import validators
from django.db import connection, transaction

class LayerTreeManager(models.Manager):
  def add(self, layers, lparent, set, maxs, cursor):
    if lparent:
      cursor.execute('''SELECT MAX(ordr) FROM tree_layertree where parent_id = %d;'''%lparent);
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
    for i in layers:
      layer_obj = 0
      layer_obj = Layers.objects.get(id = i[0])
      if(layer_obj):
        if lparent:
          self.create(id = int(maxs + counts), name = layer_obj.name, layer_id = int(i[0]),\
                                   parent_id = int(lparent), hidden = parent_obj.hidden,\
                                   ordr = int(ordr_max + counts), lset_id = int(set),\
                                   lft = 0, rght = 0, tree_id=0, level=0\
                                   );
        else:
          self.create(id = int(maxs + counts), name = layer_obj.name, layer_id = int(i[0]),\
                                   hidden = 0,\
                                   ordr = counts, lset_id = int(set),\
                                   lft = 0, rght = 0, tree_id=0, level=0\
                                   );
        parent = maxs + counts
        counts += 1
        cursor.execute('SELECT id from tree_layers where parent_id = %d;'%i[0])
        all_sublayer = cursor.fetchall()
        if all_sublayer:
          maxs = self.add(all_sublayer, int(parent), set, int(maxs+counts-1), cursor)
    return maxs + counts

  def add_inset(self, request):
    layer = request.GET.get('layer', -1)
    set_layer = request.GET.get('set_layer', -1)
    list_server = request.GET.get('list_servers', 0)
    list_set = request.GET.get('list_sets', 0)
    
    if((set_layer!= -1) and (list_server) and (list_set)):
      cursor = connection.cursor()
      layers = []
      if not layer:
        cursor.execute('SELECT id from tree_layers where parent_id IS NULL and server_id = %s;'%list_server)
        layers = cursor.fetchall()
      if layer == -1:
        list_layers = request.GET.get('layers', -1)
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
        cursor.execute('''SELECT MAX(id) FROM tree_layertree;''');
        tmp = cursor.fetchone()
        if not tmp:
          maxs = 0
        else:
          if not tmp[0]:
            maxs = 0
          else:
            maxs = int(tmp[0])
        self.add(layers, int(set_layer), list_set, maxs+1, cursor)

  def dellayer(self, layers, cursor):
    for i in layers:
      cursor.execute('SELECT id from tree_layertree where parent_id = %s;'%i[0])
      all_sublayer = cursor.fetchall()
      self.dellayer(all_sublayer, cursor)
      cursor.execute('''DELETE FROM tree_layertree where id= %s;'''%i[0]);
      transaction.commit_unless_managed()

  def del_fromset(self, request):
    set_layer = request.GET.get('set_layer', -1)
  
    if(set_layer != -1):
      cursor = connection.cursor()
      layers = []
      ll = (int(set_layer), )
      layers.append(ll)
      self.dellayer(layers, cursor)

  def add_newgroup(self, request):
    title_group = request.GET.get('title_group', 0)
    lparent = request.GET.get('where_layer', -1)
    list_set = request.GET.get('list_sets', 0)
    if(list_set and title_group and (lparent!=-1)):
      cursor = connection.cursor()
      cursor.execute('''SELECT MAX(id) FROM tree_layertree;''');
      tmp = cursor.fetchone()
      if not tmp:
        maxs = 0
      else:
        if not tmp[0]:
          maxs = 0
        else:
          maxs = int(tmp[0])
      if int(lparent):
        cursor.execute('''SELECT MAX(ordr) FROM tree_layertree where parent_id = %s;'''%lparent);
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
        self.create(id = int(maxs + 1), name = title_group, \
                    hidden = 0, \
                    ordr = 0, lset_id = int(list_set),\
                    lft = 0, rght = 0, tree_id=0, level=0\
                    )
      else:
        self.create(id = int(maxs + 1), name = title_group,\
                    parent_id = int(lparent), hidden = parent_obj.hidden,\
                    ordr = int(ordr_max + 1), lset_id = int(list_set),\
                    lft = 0, rght = 0, tree_id=0, level=0\
                    )

  def hidden(self, hdd, layers, cursor):
    for i in layers:
      layer_obj = self.get(id=int(i[0]))
      layer_obj.hidden = hdd
      layer_obj.save()
      cursor.execute('SELECT id from tree_layertree where parent_id = %d;'%i[0])
      all_layers = cursor.fetchall()
      if all_layers:
        self.hidden(hdd, all_layers, cursor)
    
class LayerSetManager(models.Manager):
  def add_newset(self, request):
    sname = request.GET.get('name_set', 0)
    stitle = request.GET.get('title_set', 0)
    sabstract = request.GET.get('abstract_set', 0)
    skeywords = request.GET.get('keywords_set', 0)
    susers = 1 #hz
    self.create(name = sname, title = stitle, abstract = sabstract,\
                author_id = susers, pub = 1\
                )
  def edit_set(self, request):
    sname = request.GET.get('name_set', 0)
    stitle = request.GET.get('title_set', 0)
    sabstract = request.GET.get('abstract_set', 0)
    skeywords = request.GET.get('keywords_set', 0)
    list_set = request.GET.get('list_sets', 0)
    susers = 1 #hz

    set_obj = self.get(id = list_set)
    set_obj.name = sname;
    set_obj.title = stitle;
    set_obj.abstract = sabstract;
  #  set_obj.keywords = skeywords;
    set_obj.save()

  def del_set(self, request):
    list_set = request.GET.get('list_sets', 0)

    cursor = connection.cursor()
    cursor.execute('SELECT id from tree_layertree where parent_id IS NULL and lset_id = %s;'%list_set)
    layers = cursor.fetchall()
    LayerTree.objects.dellayer(layers, cursor)
    cursor.execute('''DELETE FROM tree_layerset where id = %s;'''%list_set);
    transaction.commit_unless_managed()

class ServersManager(models.Manager):
  def editURL(self, request, servers):
    list_set = request.GET.get('list_servers', 0)
    URL = servers[5:]
    server = self.get(id = list_set)
    server.url = URL
    server.save()
  def add(self, request, servers):
    URL = servers[5:]
    #parser
  def update(self, request):
    server = request.GET.get('list_servers', 0)
    if server:
      server_obj = self.get(id = server)
      URL = server_obj.url
      #parser
  def delete(self, request):
    server = request.GET.get('list_servers', 0)

class LayersManager(models.Manager):
  def delete(self, request):
    server = request.GET.get('list_servers', 0)
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

  objects = LayerSetManager()
    
  def __unicode__(self):
    return self.name
  

class SLD(models.Model):
  name = models.CharField(max_length = 32, unique = True)
  url = models.CharField(max_length = 1024, unique = True)
  owner = models.ForeignKey(Users)
  
  def __unicode__(self):
    return self.name

class LayerTree(MPTTModel):
  name = models.CharField(max_length = 32, unique = True, null=True, blank=True)
  #layer = models.ForeignKey(Layers, null=True, blank=True)
  layer = models.ForeignKey(Layers, null=True, blank=True)
  lset = models.ForeignKey(LayerSet)
  ordr = models.IntegerField()
  #sld = models.ForeignKey(SLD, null=True, blank=True)
  hidden = models.BooleanField()
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

  objects =  LayerTreeManager()

  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name



