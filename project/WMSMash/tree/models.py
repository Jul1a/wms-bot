from django.db import models
from mptt.models import MPTTModel
import mptt

class Users(models.Model):
  username = models.CharField(max_length = 20, unique = True)
  pwdhash = models.CharField(max_length = 20, unique = True)
  email = models.CharField(max_length = 28, unique = True)
  role = models.IntegerField()
  def __unicode__(self):
    return self.username

class Servers(models.Model):
  Name = models.CharField(max_length = 200, unique = True)
  Title = models.CharField(max_length = 200, unique = True)
  URL = models.CharField(max_length = 1024, unique = True)
  Capabilities = models.TextField()
  srv_login = models.CharField(max_length = 20, unique = True)
  srv_passwd = models.CharField(max_length = 128, unique = True)
  Owner_id = models.ForeignKey(Users)
  Pub = models.BooleanField()
  def __unicode__(self):
    return self.Name

class Layers(MPTTModel):

  server_id = models.ForeignKey(Servers)
  name = models.CharField(max_length = 128, unique = True)
  title = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField()
  keywords = models.TextField()
  LatLngBB = models.TextField()
  Capabilities = models.TextField()
  Pub = models.BooleanField()

  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name
  
class LayerSet(models.Model):
  name = models.CharField(max_length = 32, unique = True)
  title = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField()
  keywords = models.TextField()
  author_id = models.ForeignKey(Users)
  pub = models.BooleanField()
  
  def __unicode__(self):
    return self.name

class SLD(models.Model):
  name = models.CharField(max_length = 32, unique = True)
  url = models.CharField(max_length = 1024, unique = True)
  owner_id = models.ForeignKey(Users)
  
  def __unicode__(self):
    return self.name

class LayerTree(MPTTModel):
  name = models.CharField(max_length = 32, unique = True)
  layer_id = models.ForeignKey(Layers)
  ls_id = models.ForeignKey(LayerSet)
  Ord = models.IntegerField()
  sld_id = models.ForeignKey(SLD)
  
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name

  




