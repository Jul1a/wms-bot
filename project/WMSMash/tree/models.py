from django.db import models
from mptt.models import MPTTModel
import mptt

class Users(models.Model):
  username = models.CharField(max_length = 20, unique = True)
  pwdhash = models.CharField(max_length = 20, unique = True)
  email = models.CharField(max_length = 28, unique = True)
  role = models.IntegerField(null=True, blank=True)
  def __unicode__(self):
    return self.username

class Servers(models.Model):
  Name = models.CharField(max_length = 200, unique = True, null=True, blank=True)
  Title = models.CharField(max_length = 200, unique = True)
  URL = models.CharField(max_length = 1024, unique = True)
  Capabilities = models.TextField(null=True, blank=True)
  srv_login = models.CharField(max_length = 20, unique = True, null=True, blank=True)
  srv_passwd = models.CharField(max_length = 128, unique = True, null=True, blank=True)
  Owner = models.ForeignKey(Users)
  Pub = models.NullBooleanField(null=True, blank=True)
  def __unicode__(self):
    return self.Name

class Layers(MPTTModel):

  server = models.ForeignKey(Servers)
  name = models.CharField(max_length = 128, unique = True)
  title = models.CharField(max_length = 128, unique = True)
  abstract = models.TextField(null=True, blank=True)
  keywords = models.TextField(null=True, blank=True)
  LatLngBB = models.TextField(null=True, blank=True)
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
  abstract = models.TextField(null=True, blank=True)
  keywords = models.TextField(null=True, blank=True)
  author = models.ForeignKey(Users)
  pub = models.BooleanField()
  
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
  ls = models.ForeignKey(LayerSet)
  Ord = models.IntegerField()
  sld = models.ForeignKey(SLD, null=True, blank=True)
  
  parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name




