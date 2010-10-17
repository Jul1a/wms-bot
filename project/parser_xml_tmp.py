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
# print_table: If the node "child_value" is a text print a name of a column 
#              "name_stolb" and its value "child_value.nodeValue". Method 
#              "strip" deletes initial and trailing blanks in string.
def print_table(name_stolb, child_value):

  for child in child_value:
    # it is parametrs bettwen 2 tags
    if child.nodeType == child.TEXT_NODE and child.nodeValue.strip(): 
      # if string child_value.nodeValue.strip() != NULL 
      strin = child.nodeValue.strip()

      return strin.replace("\'", "\'\'")

  return " "

#
# get_URL: Finds in attribute of the node of URL. Returns URL in case of success
#          and -1 differently. 
def get_URL(node):
  # Method attributes() get attributes of the node. Else atts is a NULL
  atts = node.attributes or {}
  # k is a key, v - value. Method items() return key and values atts
  for k, v in atts.items():
    if k == "xlink:href":
      return v
  return -1

#
# get_WMSresource: Fills fields of table WMSresources and return 0 in case of 
#                  success. Return primary key this record.
def get_WMSresource(node, cur, conn, request):
  global URL_dtd

  # Value_table saved list values for table as (key, value)
  value_table = {}
  value_table["request"] = request
  value_table["access"] = ""
  value_table["URL_dtd"] = "%s"%URL_dtd
  # view all nested tags in <Service> </Service>
  for child in node.childNodes:
    if child.nodeName in ["Name", "Title"]:
      value_table[child.nodeName] = print_table(child.nodeName, child.childNodes)

    if child.nodeName == "OnlineResource":
      value_table["URL"] = get_URL(child)
    
  # Create values in table WMSresources and return primary key. Find records 
  # in table with fields "Name" and "URL"
  return BD.create_table(cur, conn, "WMSresources", "Nwms", value_table,\
                         "Name", "URL")

#
# get_KnownLayers: Fills fields of table KnownLayers. Considers quantity of 
#                  nested tags "Layer" and creates for them tables KnownLayers.
def get_KnownLayers(node, newlayer, cur, conn, Nl_group):

  global Nwms
  Nlayers = 0

#  BD.create_KnownLayers(cur, conn)
  # Value_table saved list values for table KnownLayers as (key, value)
  value_table = {}
  
  # Saved key Nwms which has this layer
  value_table["Nwms"] = Nwms
  
  value_table["Nl_group"] = Nl_group
  value_table["access_mode"] = ""
  # view all nested tags in <Layer> </Layer>
  for child in node.childNodes:
    if child.nodeName in ["Name", "Title", "Abstract"]:
      value_table[child.nodeName] = print_table(child.nodeName, child.childNodes)
    if child.nodeName in ["LatLonBoundingBox", "BoundingBox"]:
      atts = child.attributes or {}
      # connect all attributes (k - keys and v - value) in one string "att_string"
      att_string = " ".join(["%s=%s " % (k, v) for k, v in atts.items()])
      if att_string :
        value_table[child.nodeName] = att_string
    if child.nodeName == "KeywordList":
      keyword = " "
      for child1 in child.childNodes:
        # Get list keyword via space
        if child1.nodeName in ["Keyword"]:
          keyword = keyword + " %s " % print_table(child1.nodeName,\
                                                   child1.childNodes)
          value_table[child.nodeName] = keyword
    if child.nodeName == "Layer":
      # Create values in table KnownLayers and get primary key. Find records 
      # in table with field "Nwms"

      if not Nlayers:
        lstfind = {}
        lstfind["Nwms"] = Nwms
        if "Name" in value_table:
          lstfind["Name"] = "\'%s\'"%value_table["Name"]
        else:
          lstfind["Title"] = "\'%s\'"%value_table["Title"]

        Nlayers = BD.crtable(cur, conn, "KnownLayers", "Nlayer",\
                                  value_table, lstfind)
        BD.updatebd_xmlfield(cur, conn, "KnownLayers", "LayerCapabilites", node,\
                             "Nlayer", Nlayers)
      # increase counter
      get_KnownLayers(child, newlayer, cur, conn, Nlayers)
    
  # Create values in table KnownLayers and get primary key. Find records 
  # in table with field "Nwms"
  if not Nlayers:
    lstfind = {}
    lstfind["Nwms"] = Nwms
    if "Name" in value_table:
      lstfind["Name"] = "\'%s\'"%value_table["Name"]
    else:
      lstfind["Title"] = "\'%s\'"%value_table["Title"]
    Nlayers = BD.crtable(cur, conn, "KnownLayers", "Nlayer",\
                          value_table, lstfind)
    BD.updatebd_xmlfield(cur, conn, "KnownLayers", "LayerCapabilites", node,\
                       "Nlayer", Nlayers)
  newlayer.append(Nlayers)

#
# output_tree: Bypasses all tree and handles nodes.
def output_tree(node, WMSlayer, newlayer, cur, conn, request):
    
  global Nwms, URL_dtd

  # if the node not the text (is not between opening and closing tags)
  if node.nodeType != node.TEXT_NODE:
    if(node.nodeName == "Service"):
      Nwms = 0
      Nwms = get_WMSresource(node, cur, conn, request)
      # access to the following brother of the node that not to handle the
      # node some times
      keywords = {}
      keywords["Nwms"] = Nwms
      
      WMSlayer = BD.ifselect_table(cur, "KnownLayers", "Nlayer", keywords, "Name")
      node = node.nextSibling
    if(node.nodeName == "Layer"):
      get_KnownLayers(node, newlayer, cur, conn, -1)
      # access to the following brother of the node
      node = node.nextSibling
    if(node.nodeName == "Capability"):
      # Update table WMSresources. Find record with primary key = Nwms
      keyw = {}
      keyw["Nwms"] = Nwms
      res = BD.ifselect_table(cur, "WMSresources", "Nwms", keyw, "Name")
      if res:
        BD.updatebd_xmlfield(cur, conn, "WMSresources", "Capabilites", node,\
                             "Nwms", Nwms)

    if(node.nodeType != node.TEXT_NODE):
      if node.nodeType == node.DOCUMENT_TYPE_NODE:
        global URL_dtd
        URL_dtd = node.systemId
      for child in node.childNodes:
        WMSlayer = output_tree(child, WMSlayer, newlayer, cur, conn, request)

  return WMSlayer


#
# getRemoteCapabilities:
#
def getRemoteCapabilities(name_xmlfile, cur, conn, fl):

  if fl:
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
    try:
      doc = urllib.urlopen(name_xmlfile)
    except:
      errors.input_error("xml_partition: Xml %s file don't open" % name_xmlfile)
  
  return parseCapabilities(name_xmlfile, cur, conn, doc)

# 
# parseCapabilities: Partition xml file with name "name_xmlfile" and create data in 
#                database with cursor "cur" and connection "conn". Return in 
#                sucessful case 0, else -1.
def parseCapabilities(name_xmlfile, cur, conn, doc):

  global Nwms
  request = ""

  try:
    dom = xml.dom.minidom.parse(doc)
  except:
    errors.exit_error(1, "xml_partition: Error xml file ", name_xmlfile)

  # method normilize that all text fragments have been gathered
  dom.normalize()

  WMSlayer = []
  newlayer = []
  nwlist = []
  # Partition xml file for table and create records
  request = name_xmlfile  
  WMSlayer = output_tree(dom, WMSlayer, newlayer, cur, conn, request)
  
  for WMS, Name in WMSlayer:
    if not (WMS in newlayer):
      nwlist.append(WMS)
  
  delete_Layer(nwlist, cur, conn)
  
  return Nwms

#
# delete_Layer:
def delete_Layer(nwlist, cur, conn):
  length = len(nwlist)
  if length:
    req = BD.select_table(cur, "SetLayer", "Nset_layer", "Nlayer", "sub_group")
    lists = nwlist
    for Nset, Nl, sub_group in req:
      fl = Nl in nwlist
      if fl == 1:
        res = "UPDATE KnownLayers SET access_mode = \'notWMS\' WHERE Nlayer = %s;"%Nl
        try:
          errors.save_transact(cur, conn, res)
        except:
          errors.err_transact(conn, "delete_Layer: Error update KnownLayers")
        lists.remove(Nl)
    i = len(lists) - 1
    while(i >= 0):
      for Nset, Nl, sub_group in req:
        strs = "%s"%lists[i]
        fl = sub_group.find(strs)
        strs = lists[i]
        if fl != -1:
          res = "UPDATE KnownLayers SET access_mode = \'notWMS\' WHERE Nlayer = %s;"%strs
          try:
            errors.save_transact(cur, conn, res)
          except:
            errors.err_transact(conn, "delete_Layer: Error update KnownLayers")
          lists.remove(strs)
          break
      i = i - 1
    length = len(lists)
    if length:
      for i in range(0, length):
        val = {}
        val["Nlayer"] = lists[i]
        BD.delete(cur, conn, "KnownLayers", val)

#
# find_str:
def find_str(string, xmls, strreq1, strreq2, flend):      
  strs = string.split("%s"%strreq2)
  tmpstr = []
  for i in strs:
    fl = xmls.find("%s"%i)
    if fl == -1:
      if flend:
        tmpstr.append("%s%s\n\t"%(i, strreq2))
      else:
        tmpstr.append("%s\n\t" % i)
  strSRS = " "
  for i in tmpstr:
    strSRS = strSRS + "%s"%i
  tmp = xmls.find("%s" % strreq1)
  if tmp != -1:
    xmls = xmls[0:tmp-1] + "%s"%strSRS + xmls[tmp:]
  else:
    tmp = xmls.find("</Layer>")
    if tmp != -1:
      xmls = xmls[0:tmp-1] + "%s"%strSRS + xmls[tmp:]
    else:
      xmls = xmls + "%s"%strSRS
  return xmls

#
# infoNlayer:
def infoNlayer(cur, Nlayer, xmls):
  values = {}
  values["Nlayer"] = Nlayer
  # find all layers WMS-resource's
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Nl_group")
  for Nl, Nl_group in res:
    resul = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/SRS", "Nlayer", Nl)
    if resul:
      strSRS = resul[0][0]
      xmls = find_str(strSRS, xmls, "<SRS>", "</SRS>", 1)
    resul = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/LatLonBoundingBox", "Nlayer", Nl)
    if resul:
      strSRS = resul[0][0]
      xmls = find_str(strSRS, xmls, "<LatLonBoundingBox", "</LatLonBoundingBox>", 0)
    resul = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/BoundingBox", "Nlayer", Nl)
    if resul:
      strSRS = resul[0][0]
      xmls = find_str(strSRS, xmls, "<BoundingBox", "</BoundingBox>", 0)
    resul = BD.interset_request(cur, "KnownLayers", "LayerCapabilites", "/Layer/Style", "Nlayer", Nl)
    if resul:
      strSRS = resul[0][0]
      xmls = find_str(strSRS, xmls, "<Style>", "</Style>", 1)
    if Nl_group != -1:
      xmls = infoNlayer(cur, Nl_group, xmls)
  return xmls

#
# sub_xmls:
def sub_xmls(cur, Nlayer, xmls, wayURL, flvariant):
  values = {}
  values["Nlayer"] = Nlayer
  # find all layers WMS-resource's
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Nwms", "Nl_group", "LayerCapabilites")
  for Nl, Nwms, Nl_group, txml in res:
    if flvariant:
      if Nl_group != -1:
        txml = infoNlayer(cur, Nl_group, txml)
      xmls = xmls + pastLayer(txml, Nl, wayURL)
    else:
      xmls = xmls + pastGroupLayer(cur, Nlayer)
  return xmls
  
#
# getXML_group:
def getXML_group(xmls):
  tmp = xmls.find("<Layer", 0)
  layer_ = -1
  while tmp != -1:
    layer_ = tmp
    tmp = xmls.find("<Layer", layer_ + 1)
  if layer_ == -1:
    return xmls
  else:
    if (xmls.find("</Layer>", layer_ + 1)) != -1:
      return xmls
  tmp = xmls.find(">", layer_ + 1)
  xmls = xmls[0:layer_ - 1] + "<Layer>" + xmls[tmp + 1:] 
  srs = xmls.find("<SRS>", layer_)
  if srs != -1:
    tmp = xmls.find("</SRS>", srs + 1)
    while tmp != -1:
      srs_ = tmp
      tmp = xmls.find("</SRS>", srs_ + 1)
    srs_ = srs_ + 6
    xmls = xmls[0:srs - 1] + xmls[srs_ :]
  LatLon = xmls.find("<LatLonBoundingBox", layer_)
  if LatLon != -1:
    LatLon_t = LatLon
    tmp = LatLon
    while tmp != -1:
      LatLon_t = tmp
      tmp = xmls.find("<LatLonBoundingBox", LatLon_t+1)
    LatLon_ = xmls.find(">", LatLon_t + 1)
    xmls = xmls[0:LatLon-1] +  xmls[LatLon_ + 1:]
  Bounding = xmls.find("<BoundingBox", layer_)
  if Bounding != -1:
    Bounding_t = Bounding
    tmp = Bounding_t
    while tmp != -1:
      Bounding_t = tmp
      tmp = xmls.find("<BoundingBox", Bounding_t + 1)
    Bounding_ = xmls.find(">", Bounding_t + 1)
    xmls = xmls[0:Bounding - 1] + xmls[Bounding_ + 1:]
  style = xmls.find("<Style>", layer_)
  if style != -1:
    tmp = xmls.find("</Style>", style + 1)
    while tmp != -1:
      style_ = tmp
      tmp = xmls.find("</Style>", style_ + 1)
    style_ = style_ + 8
    xmls = xmls[0:style - 1] + xmls[style_:]

  return xmls

#
# parser_sublayers:
def parser_sublayers(cur, Nwms, subgroup, xmls, wayURL, list_noset, Nlayer):
  if not subgroup:
    return xmls
  lstsub = subgroup.split(";")
  length = len(lstsub)
  for i in range(0, length-1):
    if lstsub[i].find(",") == -1:
      if (list_noset.find("; %s_%s"%(Nlayer, lstsub[i].strip()) + ";") != -1):
        continue;
      else:
        if list_noset.find("%s_%s"%(Nlayer, lstsub[i].strip()) + ";") == 0:
          continue;
      xmls = sub_xmls(cur, lstsub[i], xmls, wayURL, 1)
      xmls = xmls + "</Layer>\n\t"
    else:
      lst1sub = lstsub[i].split(",")
      lens = len(lst1sub)
      k = []
      for j in range(0, lens):
        if lst1sub[j].find("=") == -1:
          if (list_noset.find("; %s_%s"%(Nlayer, lst1sub[j].strip()) + ";") != -1):
            continue;
          else:
            if list_noset.find("%s_%s"%(Nlayer, lst1sub[j].strip()) + ";") == 0:
              continue;
          xmls = sub_xmls(cur, lst1sub[j], xmls, wayURL, 0)
          k.append(lst1sub[j])
        else:
          equal = lst1sub[j].split("=") 
          if (list_noset.find("%s_%s_%s"%(Nlayer, equal[0].strip(), equal[1].strip()) + ";") != -1):
            continue;
          mmm = len(k)
          while (k[mmm-1].strip() != equal[0].strip()) and (mmm > 0):
            xmls = xmls + "</Layer>\n\t"
            del k[mmm-1]
            mmm = mmm - 1
          xmls = getXML_group(xmls)
          xmls = sub_xmls(cur, equal[1], xmls, wayURL, 1)
          k.append(equal[1])
      mmm = len(k)
      while(mmm > 0):
        xmls = xmls + "</Layer>\n\t"
        mmm = mmm - 1
  
  return xmls

#
#pastGroupLayer:
def pastGroupLayer(cur, Nlayer):
  xmls = "<Layer>\n\t"
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Name", "Nlayer", Nlayer)
  if res:
    for k in res:
      xmls = xmls + "%s\n"%k
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Title", "Nlayer", Nlayer)
  if res:
    for k in res:
      xmls = xmls + "%s\n"%k
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/Abstract", "Nlayer", Nlayer)
  if res:
    for k in res:
      xmls = xmls + "%s\n"%k
  res = BD.interset_request(cur, "KnownLayers", "LayerCapabilites",\
                            "/Layer/KeywordList", "Nlayer", Nlayer)
  if res:
    for k in res:
      xmls = xmls + "%s\n"%k
  return xmls

#
# pastLayer:
def pastLayer(xmls, Nl, wayURL):
  subLayer = xmls.find("<Layer", 0) + 6
  strs = xmls.find("<Layer", subLayer)# - 2
  if strs != -1:
    subLayer = strs
    tmp = xmls[subLayer:]
    xmls = xmls.replace(tmp, "")
  else:
    strs = xmls.find("</Layer>", subLayer)
    tmp = xmls[strs:]
    xmls = xmls[:strs] + xmls[strs + 8:]
  start = 0
  layerstr = ""
  Online = xmls.find("<OnlineResource", 0)
  while (Online != -1):
    xlink = xmls.find("xlink:href", Online + 1)
    if xlink == -1:
      break
    tmp1 = xmls.find("=", xlink)
    tmp2 = xmls.find("\"", tmp1)
    tmp3 = xmls.find("\"", tmp2 + 1)
    needstr = xmls[tmp2:tmp3]
    if needstr.find("/img/") != -1:
      Online = xmls.find("<OnlineResource", Online + 1)
      continue
    if needstr.find("?") == -1:
      if Nl:
        xmls = xmls[:tmp1 + 1] + "\"%s"%(wayURL) + xmls[tmp3:]
      Online = xmls.find("<OnlineResource", Online + 1)
      continue
    href = xmls.find("?", tmp1)
    if Nl:
      xmls = xmls[:tmp1 + 1] + "\"%s?Nlayer=%s&"%(wayURL, Nl) + xmls[href+1:]
    else:
      xmls = xmls[:tmp1 + 1] + "\"%s?"%(wayURL) + xmls[href + 1:]
    Online = xmls.find("<OnlineResource", Online + 1)
  return xmls

#
# parser_xmlfile: Get xml file with name name_file. 
#
def parser_xmlfile(Nset, flname, cur, set_layers, WMSlist, wayURL):
  # open name file for write 
  name_file = flname + ".xml"

  dom = xml.dom.minidom.Document()

  Ntmp = WMSlist[0]
  # create service tag with need information (see Service.py).Return subtree dom
  wmt = Service.get_tag(dom, Nset, wayURL, flname, Ntmp)

  # create tag Capability.
  capability = dom.createElement("Capability")
  wmt.appendChild(capability)
  # get all wms resources, which BD has it's
  #result = BD.select_table(cur, "WMSresources", "Nwms", "Name", "Title")
  
  request = dom.createElement("Request")
  capability.appendChild(request)

  request = Service.Get_Request(dom, "GetCapabilities", request, wayURL, cur, WMSlist, flname, 0)#1  
  request = Service.Get_Request(dom, "GetMap", request, wayURL, cur, WMSlist, flname, 0)  
  request = Service.Get_Request(dom, "GetFeatureInfo", request, wayURL, cur, WMSlist, flname, 0)#1  
  request = Service.Get_Request(dom, "DescribeLayer", request, wayURL, cur, WMSlist, flname, 0)  
  request = Service.Get_Request(dom, "GetLegendGraphic", request, wayURL, cur, WMSlist, flname, 0)  

  Ntmp = -1
  i = 0
  spis_pred = []
  for v in WMSlist:
    if Ntmp == v:
      continue
    Ntmp = v
    result = []
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                              "//Capability/Exception/Format", "Nwms", v)
    if res:
      for k in res:
        strformat = "%s"%k
        strformat = strformat.replace("</Format>", "</Format>\n")
        if i:
          spis_pred = spis
          spis = strformat.split("\n")
          for m in spis_pred:
            for j in spis:
              if m == j:
                result.append(m)
                break
          spis = result
        else:
          spis = strformat.split("\n")
          i = i + 1
  strformat = " "
  for k in spis:
    strformat = strformat + "%s\n\t"%k
  exception = dom.createElement("Exception")
  capability.appendChild(exception)
  
  except_format = dom.createTextNode("%s" % strformat)
  exception.appendChild(except_format)  

  i = 0
  Ntmp = -1
  spis_pred = " "
  for v in WMSlist:
    result = " "
    if Ntmp == v:
      continue
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                              "//Capability/UserDefinedSymbolization",\
                              "Nwms", v)
    if res:
      for k in res:
        if i:
          spis_pred = spis
          spis = "%s" % k
          if spis_pred == spis:
            result = spis
        else:
          spis = "%s" % k
          i = i + 1
    spis = result
  symb = dom.createTextNode("%s" % spis)
  capability.appendChild(symb)
  
  # External layer
  Layer = dom.createElement("Layer")
  capability.appendChild(Layer)
  Name_ = dom.createElement("Name")
  Name_.appendChild(dom.createTextNode("%s"%flname))
  Layer.appendChild(Name_)
  Title_ = dom.createElement("Title")
  Title_.appendChild(dom.createTextNode("WMS Resource Manager of SB RAS"))
  Layer.appendChild(Title_)
  
  tables = []
  keywords = {}
  tables.append("AuthorsSets.layer_noset")
  keywords["AuthorsSets.Nset"] = Nset
  res = BD.ifsome_tables(cur, tables, keywords, "AuthorsSets")
  if res:
    list_noset = res[0][0]
  else:
    list_noset = ""

  # for all wms resources 
  for Nlayer, Nwms in set_layers.items():
    posit = list_noset.find("%d"%Nlayer + ";")
    if (posit != -1):
      if ((posit != 0 and (list_noset[posit-1:posit])!='_') or (posit == 0)):
        continue;
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
    for Nl_group, xmls, subgroup in res:
      if not subgroup:
        xmls = pastLayer(xmls, Nlayer, wayURL)
        if Nl_group != -1:
          xmls = infoNlayer(cur, Nl_group, xmls)
      else:
        xmls = pastGroupLayer(cur, Nlayer)

      xmls = parser_sublayers(cur, Nwms, subgroup, xmls, wayURL, list_noset, Nlayer)
      xmls = xmls + "</Layer>\t"
      text = dom.createTextNode("%s" % xmls) 
      Layer.appendChild(text)
  # transform tree in string
  texts = wmt.toprettyxml(indent='  ', newl='\n')
  # transform psevdo codes in symbols
  texts = texts.replace("&lt;", "<")
  texts = texts.replace("&gt;", ">")
  texts = texts.replace("&quot;", "\"")
  texts = texts.replace("&amp;amp;", "&amp;")
  
  print texts
  
