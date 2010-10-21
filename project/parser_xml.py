#
# parser_xml.py: Function to parse the received WMS servers and the construction
#                of a new virtual WMS server.
#

import xml.dom.minidom 
import create_bd as BD
import Service
import urllib
import errors
import re
import platform

Nwms = 0
URL_dtd = " "

#
# get_TextfromTag: If the node "child_value" is a text print a name of a column 
#              "name_stolb" and its value "child_value.nodeValue". Method 
#              "strip" deletes initial and trailing blanks in string.
def get_TextfromTag(name_stolb, child_value):

  for child in child_value:
    # it is parametrs bettwen 2 tags
    if child.nodeType == child.TEXT_NODE and child.nodeValue.strip(): 
      # if string child_value.nodeValue.strip() != NULL 
      strin = child.nodeValue.strip()

      return strin.replace("\'", "\'\'")

  return ""

#
# get_URLfromTag: Finds in attribute of the node of URL. Returns URL in case of success
#          and -1 differently. 
def get_URLfromTag(node):
  # Method attributes() get attributes of the node. Else atts is a NULL
  atts = node.attributes or {}
  # k is a key, v - value. Method items() return key and values atts
  if atts.has_key("xlink:href"):
    return atts["xlink:href"]
  return -1

#
# parse_subtreeService: Fills fields of table WMSresources and return 0 in case
#                       of success. Return primary key this record.
def parse_subtreeService(node, cur, conn, name_xmlfile):
  # Defined URL, where the DTD file is stored
  global URL_dtd

  # Value_table saved list values for table as (key, value)
  value_table = {}
  value_table["request"] = request
  value_table["access"] = ""
  value_table["URL_dtd"] = "%s"%URL_dtd
  # view all nested tags in <Service> </Service>
  for child in node.childNodes:
    if child.nodeName in ["Name", "Title"]:
      value_table[child.nodeName] = get_TextfromTag(child.nodeName, child.childNodes)

    if child.nodeName == "OnlineResource":
      value_table["URL"] = get_URLfromTag(child)
  
  # Create values in table WMSresources and return primary key. Find records 
  # in table with fields "Name" and "URL".
  # SELECT Nwms FROM WMSresources WHERE Title = value_table['Title'] and 
  #                  Name = value_table['Name'] and URL = value_table['URL'];
  # IF this recors alredy exists
  #    UPDATE WMSresources SET 
  #           request = value_table(request), 
  #           access = value_table(access), URL_dtd = value_table(URL_dtd),
  #           Name = value_table(Name), Title = value_table(Title), 
  #           URL = value_table(URL)
  #    WHERE Nwms = Nwms;
  # ELSE
  #    INSERT INTO WMSresources (
  #                Nwms, request, access, Name, Title, URL_dtd, URL)
  #    VALUES (
  #                Nwms, 'value_table(request)', 'value_table(access)', 
  #               'value_table(Name)', 'value_table(Title)', 
  #               'value_table(URL_dtd)','value_table(URL)');
  return BD.create_table(cur, conn, "WMSresources", "Nwms", value_table,\
                         "Name", "URL")

#
# parse_subtreeLayer: Fills fields of table KnownLayers. Considers quantity of 
#                     nested tags "Layer" and adds for them tables KnownLayers.
def parse_subtreeLayer(node, newlayer, cur, conn, parent_id):
  # Defined number of Server
  global Nwms
  # Will store the number of Layer
  Nlayers = 0

#  BD.create_KnownLayers(cur, conn)
  # Value_table saved list values for table KnownLayers as (key, value)
  value_table = {}
  
  # Saved key Nwms which has this layer
  value_table["Nwms"] = Nwms
  value_table["Nl_group"] = parent_id
  value_table["access_mode"] = ""
  # view all nested tags in <Layer> </Layer>
  for child in node.childNodes:
    if child.nodeName in ["Name", "Title", "Abstract"]:
      value_table[child.nodeName] = get_TextfromTag(child.nodeName, child.childNodes)
    if child.nodeName in ["LatLonBoundingBox", "BoundingBox"]:
      # connect all attributes (k - keys and v - value) in one string "att_string"
      atts = child.attributes or {}
      att_string = " ".join(["%s=%s " % (k, v) for k, v in atts.items()])
      if att_string :
        value_table[child.nodeName] = att_string
    if child.nodeName == "KeywordList":
      # Formed from all the key words one string
      keyword = " "
      for child1 in child.childNodes:
        # Get list keyword via space
        if child1.nodeName in ["Keyword"]:
          keyword = keyword + " %s " % get_TextfromTag(child1.nodeName,\
                                                   child1.childNodes)
          value_table[child.nodeName] = keyword
    if child.nodeName == "Layer":
    # If it have nested layers
      if not Nlayers:
      # If this layer has not yet been added to the database
        # Create values in table KnownLayers and get primary key. Find records 
        # in table with field "Nwms"
        lstfind = {}
        lstfind["Nwms"] = Nwms
        if "Name" in value_table:
          lstfind["Name"] = "\'%s\'"%value_table["Name"]
        else:
          lstfind["Title"] = "\'%s\'"%value_table["Title"]
        # SELECT Nlayer FROM KnownLayers 
        # WHERE Nwms = lstfind[Nwms] and 
        #       Name = lstfind[Name] and
        #       Title = lstfind[Title];
        # IF this records not exists
        #    INSERT INTO KnownLayers (Nlayer, Nwms, Nl_group, access_mode, 
        #       Name, Title, Abstract, LatLonBoundingBox, BoundingBox, Keyword)
        #    VALUES (Nlayer, value_table[Nwms], value_table[Nl_group], 
        #       value_table[access_mode], value_table[Name], value_table[Title],
        #       value_table[Abstract], value_table[LatLonBoundingBox], 
        #       value_table[BoundingBox], value_table[Keyword]);
        Nlayers = BD.crtable(cur, conn, "KnownLayers", "Nlayer",\
                                  value_table, lstfind)
        # UPDATE KnownLayers SET 
        #        LayerCapabilites = 'node.toxml('utf-8').replace("\", "\'\'")'
        # WHERE Nlayer = Nlayers;
        BD.updatebd_xmlfield(cur, conn, "KnownLayers", "LayerCapabilites", node,\
                             "Nlayer", Nlayers)
      # Recurses inner layer with the specified parent as Nlayers
      parse_subtreeLayer(child, newlayer, cur, conn, Nlayers)
    
  # Create values in table KnownLayers and get primary key. Find records 
  # in table with field "Nwms"
  if not Nlayers:
  # If this layer has not yet been added to the database
    lstfind = {}
    lstfind["Nwms"] = Nwms
    if "Name" in value_table:
      lstfind["Name"] = "\'%s\'"%value_table["Name"]
    else:
      lstfind["Title"] = "\'%s\'"%value_table["Title"]
    # Entry is added as described above
    Nlayers = BD.crtable(cur, conn, "KnownLayers", "Nlayer",\
                          value_table, lstfind)
    BD.updatebd_xmlfield(cur, conn, "KnownLayers", "LayerCapabilites", node,\
                       "Nlayer", Nlayers)
  # Adds a layer to the list created by layers of servers
  newlayer.append(Nlayers)

#
# passing_XMLtree: Passes through the built XML-tree from document "Capabilities".
#                  Find node as flowing: Service, Layer, Capability, <!DOCTYPE>.
def passing_XMLtree(node, oldlayers_Server, newlayers_Server, cur, conn, name_xmlfile):
  # Will store the number of Server and URL where store .DTD file
  global Nwms, URL_dtd

  # If the node not the text (is not between opening and closing tags)
  if node.nodeType != node.TEXT_NODE:
    if(node.nodeName == "Service"):
      # Handler is called subtree tag <Service> and defined number of Server
      Nwms = 0
      Nwms = parse_subtreeService(node, cur, conn, name_xmlfile)
      
      # Get all the layers of this server already exists in the database
      # SELECT Nlayer, Name From KnownLayers WHERE Nwms = Nwms;
      condition = {}
      condition["Nwms"] = Nwms
      oldlayers_Server = BD.ifselect_table(cur, "KnownLayers", "Nlayer", condition, "Name")
      
      # access to the following brother of the node that not to handle the
      # node some times
      node = node.nextSibling
    if(node.nodeName == "Layer"):
      # Handler is called subtree tag <Service> and defined number of Server
      parse_subtreeLayer(node, newlayers_Server, cur, conn, -1)
      
      # access to the following brother of the node
      node = node.nextSibling
    if(node.nodeName == "Capability"):
      # Update table WMSresources. Find record with primary key = Nwms
      # SELECT Nwms, Name FROM WMSresources WHERE Nwms = Nwms;
      condition = {}
      condition["Nwms"] = Nwms
      res = BD.ifselect_table(cur, "WMSresources", "Nwms", condition, "Name")
      if res:
        # If this Server already exists in the database
        # UPDATE WMSresources SET 
        #        Capabilites = 'node.toxml('utf-8').replace("\", "\'\'")'
        # WHERE Nwms = Nwms;
        BD.updatebd_xmlfield(cur, conn, "WMSresources", "Capabilites", node,\
                             "Nwms", Nwms)

    if(node.nodeType != node.TEXT_NODE):
      if node.nodeType == node.DOCUMENT_TYPE_NODE:
      # If the node is tag <!DOCTYPE>
        global URL_dtd
        # URL where store .DTD file
        URL_dtd = node.systemId
      # Recursively goes through all subnodes
      for child in node.childNodes:
        oldlayers_Server = passing_XMLtree(child, oldlayers_Server, newlayers_Server,\
                                           cur, conn, name_xmlfile)

  # Returns a list of server layers, that were already in the database
  return oldlayers_Server


#
# getRemoteCapabilities: Open file with name "name_xmlfile". Flag "its_file"
#                        indicates that the transmitted path. 
#
def getRemoteCapabilities(name_xmlfile, cur, conn, its_file):

  if its_file:
    if platform.system() == 'Linux':
      try:
        doc = open(name_xmlfile)
      except:
        errors.input_error("xml_partition: Xml %s file don't open" % name_xmlfile)
    else:
      try:
        doc = open(name_xmlfile.replace("\\", "\\\\"))
      except:
        errors.input_error("xml_partition: Xml %s file don't open" % name_xmlfile)
  else:
  # its URL adress
    try:
      doc = urllib.urlopen(name_xmlfile)
    except:
      errors.input_error("xml_partition: Xml %s file don't open" % name_xmlfile)
  
  return parseCapabilities(name_xmlfile, cur, conn, doc)

# 
# parseCapabilities: Partition xml file with name "name_xmlfile" and add data in 
#                database with cursor "cur" and connection "conn". Return in 
#                sucessful case 0, else -1.
def parseCapabilities(name_xmlfile, cur, conn, doc):
  # Will store the number of Server
  global Nwms

  # Analysis of XML-document with the product of an object class Document - dom
  try:
    dom = xml.dom.minidom.parse(doc)
  except:
    errors.exit_error(1, "xml_partition: Error xml file ", name_xmlfile)

  # Method normilize that all text fragments have been gathered
  dom.normalize()

  # Contains a list of server layers that were already in the database
  oldlayers_Server = []
  # Contains a list of server layers, which are described in the file 
  # "Capabilities"
  newlayers_Server = []
  # Contains a list of server layers that is not in the file "Capabilities"
  excesslayers_Server = []

  # Partition xml file for table and create records
  oldlayers_Server = passing_XMLtree(dom, oldlayers_Server, newlayers_Server,\
                                     cur, conn, name_xmlfile)
  
  for WMS, Name in oldlayers_Server:
    if not (WMS in newlayers_Server):
      excesslayers_Server.append(WMS)
  
  delete_Layer(excesslayers_Server, cur, conn)
  
  return Nwms

#
# delete_Layer: Removes the layers that were already in the database but not 
#               listed in the new "Capabilities" server. If it was added to 
#               some set of the layer is marked as unavailable.
def delete_Layer(list_layers, cur, conn):
  length = len(list_layers)
  if length:
    # Search all layers of set and their sublayers 
    req = BD.select_table(cur, "SetLayer", "Nset_layer", "Nlayer", "sub_group")
    # Alist of layers to be removed from the database
    list_dellayer = list_layers
    for Nset, Nlayer, subgroup_layer in req:
      # Search layer in the list of candidates for deletion
      fl = Nlayer in list_layers
      if fl == 1:
        # The layer is marked as unavailable
        res = "UPDATE KnownLayers SET access_mode = \'notWMS\' WHERE Nlayer = %s;"%Nlayer
        try:
          errors.save_transact(cur, conn, res)
        except:
          errors.err_transact(conn, "delete_Layer: Error update KnownLayers")
        # Remove the layer from the contact list
        list_dellayer.remove(Nlayer)
    # Searching for removal of layers among a set of sublayers
    i = len(list_dellayer) - 1
    while(i >= 0):
      for Nset, Nlayer, subgroup_layer in req:
        strs = "%s"%list_dellayer[i]
        fl = subgroup_layer.find(strs)
        strs = list_dellayer[i]
        if fl != -1:
          # The layer is marked as unavailable
          res = "UPDATE KnownLayers SET access_mode = \'notWMS\' WHERE Nlayer = %s;"%strs
          try:
            errors.save_transact(cur, conn, res)
          except:
            errors.err_transact(conn, "delete_Layer: Error update KnownLayers")
          # Remove the layer from the contact list
          list_dellayer.remove(strs)
          break
      i = i - 1
    # Remove all the layers that remain on the list
    length = len(list_dellayer)
    if length:
      for i in range(0, length):
        val = {}
        val["Nlayer"] = list_dellayer[i]
        BD.delete(cur, conn, "KnownLayers", val)

#
# insert_tag: Inserts a list of strings in a position. flend - specifies whether 
#             to insert the end of the closing tag.
def insert_tag(string, capabilities, opentag, closetag, flend):      
  # Splitting a string into a list
  list_strings = string.split(closetag)
  # Stores formed by a list string without the tag already exist in the "Capabilities"
  list_addstr = []
  for string in list_strings:
    # Search string into the "Capabilities", if such there is inserted
    fl = capabilities.find("%s"%string)
    if fl == -1:
      if flend:
        list_addstr.append("%s%s\n\t"%(string, closetag))
      else:
        list_addstr.append("%s\n\t" % string)
  
  # Combining the list to a string
  newstr = " "
  for string in list_addstr:
    newstr = newstr + "%s"%string
  # Search for a place to insert the resulting string
  posit_tag = capabilities.find(opentag)
  if posit_tag != -1:
    capabilities = capabilities[0:tmp-1] + "%s"%newstr + capabilities[posit_tag:]
  else:
    posit_tag = capabilities.find("</Layer>")
    if posit_tag != -1:
      capabilities = capabilities[0:posit_tag-1] + "%s"%newstr + capabilities[posit_tag:]
    else:
      capabilities = capabilities + "%s"%newstr
  return capabilities

#
# form_layerInfo: Recursive forms a layer information stored 
#                 in "Capabilities" all parent layer. Information about:
#                 SRS, LatLonBoundingBox, BoundingBox, Style.
def form_layerInfo(cur, layer_id, capabilities):
  # Requested by the parent layer "parent_id"
  values = {}
  values["Nlayer"] = layer_id
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Nl_group")
  
  for Nlayer, parent_id in res:
    # Requested tag SRS from "Capabilities"
    # SELECT xpath_nodeset(LayerCapabilites, '/Layer/SRS') WHERE Nlayer = Nlayer;
    result = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/SRS", "Nlayer", Nlayer)
    if result:
      capabilities = insert_tag(result[0][0], capabilities, "<SRS>", "</SRS>", 1)

    # Requested tag LatLonBoundingBox from "Capabilities"
    # SELECT xpath_nodeset(LayerCapabilites, '/Layer/LatLonBoundingBox') WHERE Nlayer = Nlayer;
    result = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/LatLonBoundingBox", "Nlayer", Nlayer)
    if result:
      capabilities = insert_tag(result[0][0], capabilities, "<LatLonBoundingBox", "</LatLonBoundingBox>", 0)

    # Requested tag BoundingBox from "Capabilities"
    # SELECT xpath_nodeset(LayerCapabilites, '/Layer/BoundingBox') WHERE Nlayer = Nlayer;
    result = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/BoundingBox", "Nlayer", Nlayer)
    if result:
      capabilities = insert_tag(result[0][0], capabilities, "<BoundingBox", "</BoundingBox>", 0)
    
    # Requested tag Style from "Capabilities"
    # SELECT xpath_nodeset(LayerCapabilites, '/Layer/Style') WHERE Nlayer = Nlayer;
    result = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/Style", "Nlayer", Nlayer)
    if result:
      capabilities = insert_tag(result[0][0], capabilities, "<Style>", "</Style>", 1)
    if parent_id != -1:
      capabilities = form_layerInfo(cur, parent_id, capabilities)
  return capabilities

#
# form_subxml: Formed "Capabilities" for sublayer.
def form_subxml(cur, Nlayer, capabilities, server_URL, flnogroup):
  # Requested to number the server layers, the parent layer and Capabilities.
  values = {}
  values["Nlayer"] = Nlayer
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Nwms", "Nl_group", "LayerCapabilites")

  for Nlayer, Nwms, parent_id, sub_capabilities in res:
    if flnogroup:
    # If the layer is not a group
      if parent_id != -1:
        sub_capabilities = form_layerInfo(cur, parent_id, sub_capabilities)
      capabilities = capabilities + form_layer(sub_capabilities, Nlayer, server_URL)
    else:
    # If the layer is a group
      capabilities = capabilities + form_layerGroup(cur, Nlayer)
  return capabilities
  
#
# change_layerGroup: Forms a layer in which the sublayer group if it has not 
#               already been formed.
def change_layerGroup(capabilities):
  # Search for the lowest open tag <Layer>
  tmp = capabilities.find("<Layer", 0)
  layer_ = -1
  while tmp != -1:
    layer_ = tmp
    tmp = capabilities.find("<Layer", layer_ + 1)
  if layer_ == -1:
    return capabilities
  else:
    if (capabilities.find("</Layer>", layer_ + 1)) != -1:
      return capabilities
  # Layer tag is replaced with its internal parameters of the usual tag <Layer>
  tmp = capabilities.find(">", layer_ + 1)
  capabilities = capabilities[0:layer_ - 1] + "<Layer>" + capabilities[tmp + 1:] 
  # Search open tag <SRS> in the lowest Layer
  srs = capabilities.find("<SRS>", layer_)
  # Search the latest closing tag </SRS> in Layer
  if srs != -1:
    tmp = capabilities.find("</SRS>", srs + 1)
    while tmp != -1:
      srs_ = tmp
      tmp = capabilities.find("</SRS>", srs_ + 1)
    srs_ = srs_ + 6
    # Deleted tag <SRS>
    capabilities = capabilities[0:srs - 1] + capabilities[srs_ :]
  # Search open tag <LatLonBoundingBox> in the lowest Layer
  LatLon = capabilities.find("<LatLonBoundingBox", layer_)
  if LatLon != -1:
    # Search the latest closing tag <LatLonBoundingBox> is /> in Layer
    LatLon_t = LatLon
    tmp = LatLon
    while tmp != -1:
      LatLon_t = tmp
      tmp = capabilities.find("<LatLonBoundingBox", LatLon_t+1)
    LatLon_ = capabilities.find(">", LatLon_t + 1)
    # Deleted tags <LatLonBoundingBox>
    capabilities = capabilities[0:LatLon-1] +  capabilities[LatLon_ + 1:]
  # Search open tag <BoundingBox> in the lowest Layer
  Bounding = capabilities.find("<BoundingBox", layer_)
  if Bounding != -1:
    # Search the latest closing tag <BoundingBox> is /> in Layer
    Bounding_t = Bounding
    tmp = Bounding_t
    while tmp != -1:
      Bounding_t = tmp
      tmp = capabilities.find("<BoundingBox", Bounding_t + 1)
    Bounding_ = capabilities.find(">", Bounding_t + 1)
    # Deleted tags <BoundingBox>
    capabilities = capabilities[0:Bounding - 1] + capabilities[Bounding_ + 1:]
  # Search open tag <Style> in the lowest Layer
  style = capabilities.find("<Style>", layer_)
  if style != -1:
    # Search the latest closing tag </Style> in Layer
    tmp = capabilities.find("</Style>", style + 1)
    while tmp != -1:
      style_ = tmp
      tmp = capabilities.find("</Style>", style_ + 1)
    style_ = style_ + 8
    # Deleted tags <Style>
    capabilities = capabilities[0:style - 1] + capabilities[style_:]

  return capabilities

#
# form_sublayers: Splits a string into sublayers "subgroup" and forms the
#                 corresponding "Capabilities".
def form_sublayers(cur, Nwms, subgroup_layers, capabilities, server_URL, list_layernoset, Nlayer):
  if not subgroup_layers:
  # If there is no internal layers
    return capabilities
  # The string is divided into a list of groups of layers
  lst_sublayers = subgroup_layers.split(";")
  length = len(lst_sublayers)
  for i in range(0, length-1):
  # Through the whole list of groups of layers
    if lst_sublayers[i].find(",") == -1:
    # If the layer is no internal sublayers
      # Check whether you need a layer to  display in the "Capabilities"
      if (list_layernoset.find("; %s_%s"%(Nlayer, lst_sublayers[i].strip()) + ";") != -1):
        continue;
      else:
        if list_layernoset.find("%s_%s"%(Nlayer, lst_sublayers[i].strip()) + ";") == 0:
          continue;
      # If the layer you want to display
      capabilities = form_subxml(cur, lst_sublayers[i], capabilities, server_URL, 1)
      capabilities = capabilities + "</Layer>\n\t"
    else:
    # If the layer is sublayers
      # Line breaks sublayer sublayers
      lst1sub = lst_sublayers[i].split(",")
      lens = len(lst1sub)
      # Stores hierarchical embedding layers for futher closing tags
      nestedlayers = []
      for j in range(0, lens):
      # Through the whole list of groups of sublayers
        if lst1sub[j].find("=") == -1:
        # If the layer is no internal sublayers
          # Check whether you need a layer to  display in the "Capabilities"
          if (list_layernoset.find("; %s_%s"%(Nlayer, lst1sub[j].strip()) + ";") != -1):
            continue;
          else:
            if list_layernoset.find("%s_%s"%(Nlayer, lst1sub[j].strip()) + ";") == 0:
              continue;
          # If the layer you want to display
          capabilities = form_subxml(cur, lst1sub[j], capabilities, server_URL, 0)
          # Layer is added to the list is not closed tag
          nestedlayers.append(lst1sub[j])
        else:
        # If the layer is internal sublayers
          # Line breaks up into a layer equal[1] who owns equal[0]
          equal = lst1sub[j].split("=") 
          # Check whether you need a layer to  display in the "Capabilities"
          if (list_layernoset.find("%s_%s_%s"%(Nlayer, equal[0].strip(), equal[1].strip()) + ";") != -1):
            continue;
          # Search tags layers which must be closed tag before inserting a new sublayer
          mmm = len(nestedlayers)
          while (nestedlayers[mmm-1].strip() != equal[0].strip()) and (mmm > 0):
            # Closed tag
            capabilities = capabilities + "</Layer>\n\t"
            # Removed from the list
            del nestedlayers[mmm-1]
            mmm = mmm - 1
          # If the layer you want to display
          capabilities = change_layerGroup(capabilities)
          capabilities = form_subxml(cur, equal[1], capabilities, server_URL, 1)
          # Layer is added to the list is not closed tag
          nestedlayers.append(equal[1])
      # Search tags layers which must be closed tag
      mmm = len(nestedlayers)
      while(mmm > 0):
        capabilities = capabilities + "</Layer>\n\t"
        mmm = mmm - 1
  
  return capabilities

#
# form_layerGroup: Modifies "Capabilities" layer.for form group
def form_layerGroup(cur, Nlayer):
  capabilities = "<Layer>\n\t"
  # Requested tag Name from "Capabilities"
  # SELECT xpath_nodeset(LayerCapabilites, '/Layer/Name') WHERE Nlayer = Nlayer;
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Name", "Nlayer", Nlayer)
  if res:
    for Name in res:
      capabilities = capabilities + "%s\n"%Name
  # Requested tag Title from "Capabilities"
  # SELECT xpath_nodeset(LayerCapabilites, '/Layer/Title') WHERE Nlayer = Nlayer;
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Title", "Nlayer", Nlayer)
  if res:
    for Title in res:
      capabilities = capabilities + "%s\n"%Title
  # Requested tag Abstract from "Capabilities"
  # SELECT xpath_nodeset(LayerCapabilites, '/Layer/Abstract') WHERE Nlayer = Nlayer;
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Abstract", "Nlayer", Nlayer)
  if res:
    for Abstract in res:
      capabilities = capabilities + "%s\n"%Abstract
  # Requested tag KeywordList from "Capabilities"
  # SELECT xpath_nodeset(LayerCapabilites, '/Layer/KeywordList') WHERE Nlayer = Nlayer;
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/KeywordList", "Nlayer", Nlayer)
  if res:
    for KeywordList in res:
      capabilities = capabilities + "%s\n"%KeywordList
  return capabilities

#
# form_layer: Modifies "Capabilities" layer without the inner layers
def form_layer(capabilities, Nlayer, server_URL):
  # Remove all the internal layers leaving only the outger tag <Layer>
  subLayer = capabilities.find("<Layer", 0) + 6
  strs = capabilities.find("<Layer", subLayer)# - 2
  if strs != -1:
  # If layer has the internal layers
    subLayer = strs
    tmp = capabilities[subLayer:]
    capabilities = capabilities.replace(tmp, "")
  else:
    strs = capabilities.find("</Layer>", subLayer)
    tmp = capabilities[strs:]
    capabilities = capabilities[:strs] + capabilities[strs + 8:]
  
  # Forming a request for access to the layer
  Online = capabilities.find("<OnlineResource", 0)
  while (Online != -1):
    posit_xlink = capabilities.find("xlink:href", Online + 1)
    if posit_xlink == -1:
      break
    posit_equal = capabilities.find("=", posit_xlink)
    left_quote = capabilities.find("\"", posit_equal)
    right_quote = capabilities.find("\"", left_quote + 1)
    resource_URL = capabilities[left_quote:right_quote]
    if resource__URL.find("/img/") != -1:
      Online = capabilities.find("<OnlineResource", Online + 1)
      continue
    if resource__URL.find("?") == -1:
      if Nlayer:
        capabilities = capabilities[:posit_equal + 1] + "\"%s"%(server_URL) + capabilities[right_quote:]
      Online = capabilities.find("<OnlineResource", Online + 1)
      continue
    quest_mark = capabilities.find("?", posit_equal)
    if Nlayer:
      capabilities = capabilities[:posit_equal + 1] + "\"%s?Nlayer=%s&"%(server_URL, Nlayer) + capabilities[quest_mark+1:]
    else:
      capabilities = capabilities[:posit_equal + 1] + "\"%s?"%(server_URL) + capabilities[quest_mark + 1:]
    Online = capabilities.find("<OnlineResource", Online + 1)
  
  return capabilities

#
# gather_capabilities: Creates new "Capabilities" file for new virtual server.
#                      list_WMSservers - list of used servers.
#
def gather_capabilities(Nset, nameSet, cur, set_layers, list_WMSservers, server_URL):
  # Generated file name 
  name_file = nameSet + ".xml"
  
  # Product of an object class Document - dom
  dom = xml.dom.minidom.Document()
  
  # DTD schema takes one of the servers
  Nwms_dtd = list_WMSservers[0]

  # create service tag with need information (see Service.py).Return subtree dom
  tag_service = Service.get_tag(dom, server_URL, nameSet, Nwms_dtd)

  # create tag Capability.
  capability = dom.createElement("Capability")
  tag_service.appendChild(capability)
  
  # create tag in Capability: Request
  request_dom = dom.createElement("Request")
  capability.appendChild(request_dom)
  # Formated a tag Request with the intersection of all formats by all used servers
  request_dom = Service.get_tagRequest(dom, "GetCapabilities", request_dom,\
                                       server_URL, cur, list_WMSservers, nameSet, 0)
  request_dom = Service.get_tagRequest(dom, "GetMap", request_dom, server_URL,\
                                       cur, list_WMSservers, nameSet, 0)  
  request_dom = Service.get_tagRequest(dom, "GetFeatureInfo", request_dom, \
                                       server_URL, cur, list_WMSservers, nameSet, 0)  
  request_dom = Service.get_tagRequest(dom, "DescribeLayer", request_dom, \
                                       server_URL, cur, list_WMSservers, nameSet, 0)  
  request_dom = Service.get_tagRequest(dom, "GetLegendGraphic", request_dom, \
                                       server_URL, cur, list_WMSservers, nameSet, 0)  

  Nwms_used = -1
  count_servers = 0
  oldlist_formats = []
  for server_id in list_WMSservers:
  # Enumerates all used servers
    # Check their recurrence
    if Nwms_used == server_id:
      continue
    Nwms_used = server_id
    # Requested format of the tag with the name "Exception" of the server server_id
    # SELECT xpath_nodeset(Capabilites, '"//Capability/Exception/Format"') 
    # FROM WMSresources
    # WHERE Nwms = server_id;
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                              "//Capability/Exception/Format", "Nwms", server_id)
    # Stores intersection list formats
    result = []
    if res:
    # If there is a format
      for tagFormat in res:
        strformat = tagFormat.replace("</Format>", "</Format>\n")
        if count_servers:
        # This is not the first list of formats
          oldlist_formats = list_formats
          # The string format is divided into a list
          list_formats = strformat.split("\n")
          # Created by the intersection of the lists of formats belonging to two servers
          for m in oldlist_formats:
            for j in list_formats:
              if m == j:
                result.append(m)
                break
          # The result of suppresion of record in the list of formats
          list_formats = result
        else:
        # This is the first list of formats
          # The string format is divided into a list
          list_formats = strformat.split("\n")
          count_servers += 1
  # Formed a string from the list of formats
  strformat = " "
  for k in list_formats:
    strformat = strformat + "%s\n\t"%k

  # Create tag "Exception"
  exception = dom.createElement("Exception")
  capability.appendChild(exception)
  except_format = dom.createTextNode("%s" % strformat)
  exception.appendChild(except_format)  

  count_servers = 0
  Nwms_used = -1
  oldlist_formats = " "
  for server_id in list_WMSservers:
  # Enumerates all used servers
    result = " "
    # Check their recurrence
    if Nwms_used == server_id:
      continue
    Nwms_used = server_id
    # Requested format of the tag with the name "Exception" of the server server_id
    # SELECT xpath_nodeset(Capabilites, '"//Capability/UserDefinedSymbolization"') 
    # FROM WMSresources
    # WHERE Nwms = server_id;
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                              "//Capability/UserDefinedSymbolization",\
                              "Nwms", server_id)
    if res:
    # If there is a UserDefinedSymbolization
      for tagSymbolization in res:
        if count_servers:
        # This is not the first string UserDefinedSymbolization
          oldlist_formats = list_formats
          list_formats = tagSymbolization
          if oldlist_formats == list_formats:
            result = list_formats
        else:
          list_formats = tagSymbolization
          count_servers += 1
    list_formats = result
  # Create tag UserDefinedSymbolization
  symb = dom.createTextNode("%s" % list_formats)
  capability.appendChild(symb)
  
  # External layer - layer containing all the layers set
  external_Layer = dom.createElement("Layer")
  capability.appendChild(external_Layer)
  Name_exLayer = dom.createElement("Name")
  Name_exLayer.appendChild(dom.createTextNode("%s"%nameSet))
  external_Layer.appendChild(Name_exLayer)
  Title_exLayer = dom.createElement("Title")
  Title_exLayer.appendChild(dom.createTextNode("WMS Resource Manager of SB RAS"))
  external_Layer.appendChild(Title_exLayer)
  
  # Requested a list of layers which don't display in "Capabilities"
  tables = []
  keywords = {}
  tables.append("AuthorsSets.layer_noset")
  keywords["AuthorsSets.Nset"] = Nset
  res = BD.ifsome_tables(cur, tables, keywords, "AuthorsSets")
  if res:
    list_layernoset = res[0][0]
  else:
    list_layernoset = ""

  # For all layers of the set 
  for Nlayer, Nwms in set_layers.items():
    # Checking whether to display the layer in "Capabilities"
    place_instr = list_layernoset.find("%d"%Nlayer + ";")
    if (place_instr != -1):
      if ((place_instr != 0 and (list_layernoset[place_instr-1:place_instr])!='_') or (place_instr == 0)):
        # If the layer is not necessary to display, then its inner layers too
        continue;

    # Requested by the parent layer, a list of internal layers and Capabilities.
    tables = []
    keywords = {}
    tables.append("KnownLayers.Nl_group")
    tables.append("KnownLayers.LayerCapabilites")
    tables.append("SetLayer.sub_group")
    keywords["KnownLayers.Nwms"] = Nwms
    keywords["SetLayer.Nlayer"] = Nlayer
    keywords["KnownLayers.Nlayer"] = "SetLayer.Nlayer"
    keywords["SetLayer.Nset"] = Nset
    res = BD.ifsome_tables(cur, tables, keywords, "KnownLayers", "SetLayer")
    
    for parent_id, capabilities, subgroup_layers in res:
      if not subgroup_layers:
      # If there is no internal layers 
        capabilities = form_layer(capabilities, Nlayer, server_URL)
        if parent_id != -1:
        # If the layer has a parent
          capabilities = form_layerInfo(cur, parent_id, capabilities)
      else:
      # Another group is formed from layer
        capabilities = form_layerGroup(cur, Nlayer)
      # Is the formation of sublayers
      capabilities = form_sublayers(cur, Nwms, subgroup_layers, capabilities,\
                                      server_URL, list_layernoset, Nlayer)
      capabilities = capabilities + "</Layer>\t"
      # Create new node "Layer"
      text = dom.createTextNode("%s" % capabilities) 
      external_Layer.appendChild(text)
  # transform tree in string
  texts = tag_service.toprettyxml(indent='  ', newl='\n')
  # transform psevdo codes in symbols
  texts = texts.replace("&lt;", "<")
  texts = texts.replace("&gt;", ">")
  texts = texts.replace("&quot;", "\"")
  texts = texts.replace("&amp;amp;", "&amp;")
  
  print texts
  
