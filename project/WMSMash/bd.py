from WMSMash.tree.models import Users, Servers, Layers, LayerSet, SLD, LayerTree

p = Users(username='Julia',pwdhash='Julia', email='Julia@julia.com', role=1);
p.save()
id_user = p.id

p = Servers(Name='WMSresource1',Title='WMSresource 1', URL = 'wmsresource1@host.com', Capabilities = 'text', Owner_id = id_user);
p.save()
id_resource = p.id
p = Servers(Name='WMSresource2',Title='WMSresource 2', URL = 'wmsresource2@host.com', Capabilities = 'text', Owner_id = id_user);
p.save()

p = Layers(server_id = id_resource, name='Layer1',title='Layer 1', abstract= 'layer 1', Capabilities = 'text', Pub = 1, tree_id=1, level=0);
p.save()
id_layer1 = p.id
p = Layers(server_id = id_resource, name='Layer1.1',title='Layer 1.1', abstract= 'layer 1.1', Capabilities = 'text', Pub = 1, parent_id = id_layer1, tree_id=1, level=1);
p.save()
id_layer1_1 = p.id
p = Layers(server_id = id_resource, name='Layer2',title='Layer 2', abstract= 'layer 2', Capabilities = 'text', Pub = 1, tree_id=1, level=0);
p.save()
id_layer2 = p.id
p = Layers(server_id = id_resource, name='Layer1.2',title='Layer 1.2', abstract= 'layer 1.2', Capabilities = 'text', Pub = 1, parent_id = id_layer1, tree_id=1, level=1);
p.save()
id_layer1_2 = p.id
p = Layers(server_id = id_resource, name='Layer2.1',title='Layer 2.1', abstract= 'layer 2.1', Capabilities = 'text', Pub = 1, parent_id = id_layer2, tree_id=1, level=1);
p.save()
id_layer2_1 = p.id
p = Layers(server_id = id_resource, name='Layer3',title='Layer 3', abstract= 'layer 3', Capabilities = 'text', Pub = 1, tree_id=1, level=0);
p.save()
id_layer3 = p.id

p = LayerSet(name='Set1',title='Set 1', abstract= 'Set 1', author_id = id_user, pub = 1);
p.save()
id_set = p.id
p = LayerSet(name='Set2',title='Set 2', abstract= 'Set 2', author_id = id_user, pub = 1);
p.save()

p = SLD(name='SLD1', url = 'SLD1@host.com', owner_id = id_user);
p.save()
id_sld = p.id

p = LayerTree(name='Layer2', layer_id=id_layer2, ls_id=id_set, Ord=0, level=0, tree_id=1);
p.save()
id_setlayer2= p.id
p = LayerTree(name='Layer1.1', layer_id=id_layer1_1, ls_id=id_set, Ord=1, level=1, tree_id=1, parent_id = id_setlayer2);
p.save()
id_setlayer1_1= p.id
p = LayerTree(name='Layer3', layer_id=id_layer3, ls_id=id_set, Ord=1, level=1, tree_id=1, parent_id = id_setlayer2);
p.save()
id_setlayer3= p.id
p = LayerTree(name='Layer1', layer_id=id_layer1, ls_id=id_set, Ord=0, level=0, tree_id=1);
p.save()
id_setlayer1= p.id
p = LayerTree(name='Layer1.2', layer_id=id_layer1_2, ls_id=id_set, Ord=1, level=1, tree_id=1, parent_id = id_setlayer1);
p.save()
id_setlayer1_2= p.id


