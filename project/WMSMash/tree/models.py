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
  name = models.CharField(max_length = 200, unique = True, null=True, blank=True)
  title = models.CharField(max_length = 200, unique = True)
  url = models.CharField(max_length = 1024, unique = True)
  capabilites = models.TextField(null=True, blank=True)
  login = models.CharField(max_length = 20, unique = True, null=True, blank=True)
  passwd = models.CharField(max_length = 128, unique = True, null=True, blank=True)
  owner = models.ForeignKey(Users)
  pub = models.NullBooleanField(null=True, blank=True)
  nwms = models.IntegerField(null=True, blank=True)
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

  class Meta:
    ordering = ['parent_id']
  
  def __unicode__(self):
    return self.name




