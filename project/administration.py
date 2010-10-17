#
# administration.py:

import create_bd as BD 
import parser_xml as docs
import errors
import os, platform
import urllib

#
# Author: Fills table WMSUsers. Cur and conn - cursor of database, Name - name
#         author, pwhash - password. Return primary key of field in database.
def Author(cur, conn, Name, pwhash):
  keywords = {}
  lstfind = {}
  lstfind["Name"] = "\'%s\'" % Name
  keywords["Name"] = Name
  keywords["pwhash"] = pwhash
  pkey = BD.crtable(cur, conn, "WMSUsers", "UID", keywords, lstfind)

  return pkey

#
# get_listsub: Generates a string "sub_group" containning sublayers are in "Nl".
def get_listsub(cur, conn, Nl, sub_group):
  # Solicited layers that are in the "Nl"
  vals = {}
  vals["Nl_group"] = Nl
  tables = []
  tables.append("Nlayer")  
  tables.append("access_mode")  
  res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
  for i, access in res:
    # If the layer is available it is added to the string
    if access != "notWMS":
      sub_group = sub_group + ", %s = %d"%(vals["Nl_group"], i)
      # Fromed by its sublayers
      sub_group = get_listsub(cur, conn, i, sub_group)

  return sub_group

#
# get_inset: Fills table SetLayer. Cur and conn - cursor of database, flset - flag
#            about inputed button Add layers, ppkey - flag about inputed name file,
#            lst_layer - list layers for saved.
def get_inset(cur, conn, ppkey, lst_layer):
  # If not inputed button Add layers
  if ppkey:
    keywords = {}
    lstfind = {}
    keywords["Nset"] = ppkey
    for i in lst_layer:
      # Set had this layer
      vals = {}
      vals["Nlayer"] = i
      vals["Nset"] = ppkey
      tables = []
      tables.append("Nset_layer")  
      res = BD.ifsome_tables(cur, tables, vals, "SetLayer")
      if res:
        continue
      sub_group = ""
      vals = {}
      vals["Nl_group"] = i
      tables = []
      tables.append("Nlayer")  
      tables.append("access_mode")  
      res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
      for j, access in res:
        if access != "notWMS":
          sub_group = sub_group + " %d"%j
          sub_group = get_listsub(cur, conn, j, sub_group)
          sub_group = sub_group + ";"
      keywords["Nlayer"] = i
      lstfind = {}
      lstfind["Nlayer"] = i
      lstfind["Nset"] = ppkey
      if sub_group:
        lstfind["sub_group"] = "%s"%sub_group.strip()
      else:
        lstfind["sub_group"] = "%s"%sub_group
      keys = BD.crtable(cur, conn, "SetLayer", "Nset_layer", lstfind, keywords)
  else:
    errors.input_error("get_inset: Please input name file")

#
# get_namesetbd: Fills table AuthorsSets. Cur and conn - cursor of database, 
#                namefile - name of set, pkey - Author primary key. 
#                Return primary key of field in BD.
def get_namesetbd(cur, conn, namefile, pkey):
  keywords = {}
  lstfind = {}
  lstfind["Name"] = "\'%s\'"%namefile
  keywords["Title"] = "XML"
  keywords["Abstract"] = "XML"
  keywords["Nauthor"] = int(pkey)
  keywords["Name"] = "%s" % namefile
  ppkey = BD.crtable(cur, conn, "AuthorsSets", "Nset", keywords, lstfind)
  
  return ppkey
  
#
# shaper_setbd: Deletes not selected layers from a set. Cur and conn - cursor 
#               of database, ppkey - ppkey - flag about inputed name file, lst -
#               list layers from set defined user.
def shaper_setbd(cur, conn, ppkey, lst):
  if not lst:
    return 1

  # Get all layers from set ppkey
  values = {}
  values["Nset"] = ppkey
  for i, Nl in enumerate(lst):
    values["Nlayer"] = Nl
    BD.delete(cur, conn, "SetLayer", values)
    
#
# shaper_subset: Removes a set  "ppkey" of sublayers specified in the list "lst".
def shaper_subset(cur, conn, ppkey, lst):
  if not lst:
    return 1

  # Get all layers from set ppkey
  values = {}
  vals = {}
  tables = []
  tables.append("Nset_layer")
  tables.append("sub_group")
  values["Nset"] = ppkey
  for i, Nl in enumerate(lst):
    # Requested in layer "lst_layer[0]" and sublayers are in the set
    tables = []
    tables.append("Nset_layer")
    tables.append("sub_group")
    values = {}
    values["Nset"] = ppkey
    lst_layer = Nl.split("_")
    values["Nlayer"] = lst_layer[0]
    res = BD.ifsome_tables(cur, tables, values, "SetLayer")
    # Remove the layer from the list "lst"
    lst_layer.remove(lst_layer[0])
    length = len(lst_layer)
    sub = ""
    vals = {}
    for Nset, sub_group in res:
      vals["Nset_layer"] = Nset
      sub = sub_group
      break
    if length > 1:
      strs = ", %s = %s"%(lst_layer[length-2], lst_layer[length-1])
      lst_layer.remove(lst_layer[length-1])
      length = length - 1
      pstart = sub.find(strs)
      pend = sub.find(";", pstart)
      ptmp = 0
      phvost = sub.find(";", 0)
      while((phvost != pend)and(phvost != -1)):
        ptmp = phvost + 1
        phvost = sub.find(";", ptmp)
      tmps = sub[ptmp:pstart]
      lenstrs = len(strs.strip())
      ktmp = tmps.split(",")
      ltmp = len(ktmp)
      for m in range(0, ltmp):
        fl = ktmp[ltmp -1 - m].find("=")
        if fl == -1:
          tmp = "%s = "%ktmp[ltmp -1 - m].strip()
        else:
          equl = ktmp[ltmp - 1 - m].split('=')
          tmp = " %s = "%equl[1].strip()
        tmp = tmp.strip()
        pnd = sub.find(tmp, pstart+lenstrs, pend)
        if (pnd > -1) and (pnd < pend):
          pend = pnd - 2 
      subx = sub[pstart:pend]
      subx = subx.strip()
      sub = sub.replace(subx, "", 1)
    else:
      #iffile = open("lst", "w")
      #strs_k = '%s'%lst_layer[0].strip()
      pstart = sub.find('; '+lst_layer[0])
      if pstart == -1:
        pstart = sub.find(lst_layer[0])
      else:
        pstart += 2
      #iffile.write("%s %s %d"%(lst_layer, strs_k, pstart))
      pend = sub.find(";", pstart)
      #pend = len(strs_k)
      subx = sub[pstart:pend+1]
      sub = sub.replace(subx, "", 1)
      #iffile.close()
    sub = ' '.join(sub.split())
    req = "UPDATE SetLayer SET sub_group = \'%s\' WHERE Nset_layer = %d;"\
           %(sub, Nset)
    try:
      errors.save_transact(cur, conn, req)
    except:
      errors.save_transact(conn, "shaper_subset: Error Update SetLayer")

#
# save_set: Saved set in XML file. Cur - cursor of database, lst - list layers 
#           from set, namefile - name file.
def save_set(Nset, cur, lst, namefile):
  vals = {}
  listset = {}
  tables = []
  tables.append("Nwms")
  # Get Nwms for either layer
  for i in lst:
    vals["Nlayer"] = i
    res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
    listset[i] = int(res[0][0])
  # Get XML file
  docs.parser_xmlfile(Nset, namefile, cur, listset)

#
# add_ingroup: Adds a list "layer" of layers and their sublayers in the list a 
#              layer group "lst" a set "ppkey".
def add_ingroup(cur, conn, ppkey, pkey, lst, layers):
  if not lst:
    return 1
  vals = {}
  tables = []
  tables.append("Nwms")
  vals["Name"] = "\'user\'"
  vals["Title"] = "\'user_wms\'"
  vals["author"] = "\'%d\'"%pkey
  res = BD.ifsome_tables(cur, tables, vals, "WMSresources")
  Nwms_tmp = 0
  if res:
    Nwms_tmp = int(res[0][0])
  for i in lst:
    # Request a list of sublayers which belong to layer "i"
    vals = {}
    tables = []
    tables.append("Nlayer")
    vals["Nl_group"] = i
    layer_group = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
    if Nwms_tmp:
      vals = {}
      tables = []
      tables.append("Nwms")
      vals["Nlayer"] = i
      res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
      Nwms_layer = 0
      if res:
        Nwms_layer = int(res[0][0])
      if Nwms_layer != Nwms_tmp:
        if not layer_group:
          continue
    else:
      if not layer_group:
        continue
    sub_group = ""
    vals = {}
    tables = []
    tables.append("Nset_layer")
    tables.append("sub_group")
    vals["Nlayer"] = i
    vals["Nset"] = ppkey
    res = BD.ifsome_tables(cur, tables, vals, "SetLayer")
    for k, l in res:
      Nset = k
      sub_group = l
    for j in layers:
      # Added layer in list sublayers
      sub_group = sub_group + " %s"%j
      # Added its sublayer in list
      sub_group = get_listsub(cur, conn, j, sub_group)
      sub_group = sub_group + ";"
      sub_group = sub_group.strip()
      req = "UPDATE SetLayer SET sub_group = \'%s\' WHERE Nset_layer = %d;"\
            %(sub_group, Nset)
      try:
        errors.save_transact(cur, conn, req)
      except:
        errors.save_transact(conn, "add_ingroup: Error Update SetLayer")

#
# addsub_ingroup: Adds a list "layers" of layers and their sublayers in the list a 
#                 sublayer group "lst" a set "ppkey".
def addsub_ingroup(cur, conn, ppkey, pkey, lst, layers):
  if not lst:
    return 1
  vals = {}
  tables = []
  tables.append("Nwms")
  vals["Name"] = "\'user\'"
  vals["Title"] = "\'user_wms\'"
  vals["author"] = "\'%d\'"%pkey
  res = BD.ifsome_tables(cur, tables, vals, "WMSresources")
  Nwms_tmp = 0
  if res:
    Nwms_tmp = int(res[0][0])
  for i in lst:
    # Request a list of sublayers which belong to layer "i"
    lst_layer = i.split("_")
    length = len(lst_layer)
    vals = {}
    tables = []
    tables.append("Nlayer")
    vals["Nl_group"] = lst_layer[length-1]
    layer_group = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
    if Nwms_tmp:
      vals = {}
      tables = []
      tables.append("Nwms")
      vals["Nlayer"] = lst_layer[length-1]
      res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
      Nwms_layer = 0
      if res:
        Nwms_layer = int(res[0][0])
      if Nwms_layer != Nwms_tmp:
        if not layer_group:
          continue;
    else:
      if not layer_group:
          continue;
    tables = []
    values = {}
    values["Nset"] = ppkey
    tables.append("Nset_layer")
    tables.append("sub_group")
    values["Nlayer"] = lst_layer[0]
    res = BD.ifsome_tables(cur, tables, values, "SetLayer")
    sub_group = ""
    values = {}
    for Nset, sub in res:
      values["Nset_layer"] = Nset
      sub_group = sub
    lst_layer.remove(lst_layer[0])
    length = len(lst_layer)
    if length > 1:
      strs = ", %s = %s"%(lst_layer[length-2], lst_layer[length-1])
      pstart = sub_group.find(strs)
      pend = pstart + len(strs)
      sub = strs
      strs = sub_group[pstart:pend]
      flag = strs.find(';')
      for j in layers:
        sub = sub + ", %s = %s"%(lst_layer[length-1], j)
        sub = sub.strip()
        sub = get_listsub(cur, conn, j, sub)
      if flag != -1:
        sub = sub + ";"
      sub_group = sub_group.replace(strs, sub)
    else:
      pstart = sub_group.find(lst_layer[0])
      pend = sub_group.find(";", pstart)
      subx = sub_group[pstart:pend]
      sub = subx
      subx = sub_group[pstart:pend+1]
      for j in layers:
        sub = sub + ", %s = %s"%(lst_layer[0], j)
        sub = sub.strip()
        sub = get_listsub(cur, conn, j, sub)
      sub = sub + ";"
      sub_group = sub_group.replace(subx, sub)
    req = "UPDATE SetLayer SET sub_group = \'%s\' WHERE Nset_layer = %d;"\
           %(sub_group, Nset)
    try:
        errors.save_transact(cur, conn, req)
    except:
        errors.save_transact(conn, "addsub_ingroup: Error Update SetLayer")
#
# dellayer: Removes laayer
def dellayer(cur, conn, req, lstnewgr, length, flag):
  lists = []
  lists = lstnewgr
  for Nset, Nl, namelayer, sub_group, nameset in req:
    strs = "%d"%Nl
    strs = strs.strip()
    fl = strs in lstnewgr
    if fl == 1:
      lists.remove(strs)
      errors.input_error("Set \"%s\" has layer \"%s\""%(nameset, namelayer))
      return 1

  i = len(lists) - 1
  condition = 0
  while((i >= 0) and (condition == 0)):
    for Nset, Nl, namelayer, sub_group, nameset in req:
      if sub_group:
        strs = " %s;"%lists[i]
        fl = sub_group.find(strs)
        strs = lists[i]
        if fl != -1:
          strs = "%s"%lists[i]
          lists.remove(strs)
          tables = []
          value = {}
          tables.append("Name")
          value["Nlayer"] = strs
          ress = BD.ifsome_tables(cur, tables, value, "KnownLayers")
          errors.input_error("Set %s has layer \"%s\""%(nameset, ress[0][0]))
          return 1
        strs = " %s,"%lists[i]
        fl = sub_group.find(strs)
        if fl != -1:
          strs = "%s"%lists[i]
          lists.remove(strs)
          tables = []
          value = {}
          tables.append("Name")
          value["Nlayer"] = strs
          ress = BD.ifsome_tables(cur, tables, value, "KnownLayers")
          errors.input_error("Set12 %s has layer \"%s\""%(nameset, ress[0][0]))
          return 1
        strs = "%s;"%lists[i]
        fl = sub_group.find(strs)
        if fl == 0:
          strs = "%s"%lists[i]
          lists.remove(strs)
          tables = []
          value = {}
          tables.append("Name")
          value["Nlayer"] = strs
          ress = BD.ifsome_tables(cur, tables, value, "KnownLayers")
          errors.input_error("Set13 %s has layer \"%s\""%(nameset, ress[0][0]))
          return 1
        strs = "%s,"%lists[i]
        fl = sub_group.find(strs)
        if fl == 0:
          strs = "%s"%lists[i]
          lists.remove(strs)
          tables = []
          value = {}
          tables.append("Name")
          value["Nlayer"] = strs
          ress = BD.ifsome_tables(cur, tables, value, "KnownLayers")
          errors.input_error("Set14 %s has layer \"%s\""%(nameset, ress[0][0]))
          return 1
    i = i - 1
  if condition == 1:
    return 1
  length_t = len(lists)
  if (length != length_t) and (flag == 1):
    return 1
  if length_t:
    for i in range(0, length_t):
      val = {}
      val["Nlayer"] = lists[i]
      BD.delete(cur, conn, "KnownLayers", val)
  if length == length_t:
    return 0
  else:
    return 1

#
# delnewgr: Removes layer have created a user "pkey".
def delnewgr(cur, conn, pkey, lstnewgr):
  if pkey == 0:
    return -1
  length = len(lstnewgr)
  if length:
    tables = []
    tables.append("SetLayer.Nset_layer")
    tables.append("SetLayer.Nlayer")
    tables.append("KnownLayers.Name")
    tables.append("SetLayer.sub_group")
    tables.append("AuthorsSets.Name")
    value = {}
    value["WMSUsers.UID"] = "\'%d\'"%pkey
    value["AuthorsSets.Nauthor"] = "WMSUsers.UID"
    value["AuthorsSets.Nset"] = "SetLayer.Nset"
    value["KnownLayers.Nlayer"] = "SetLayer.Nlayer"
#    print "to req"
    req = BD.ifsome_tables(cur, tables, value, "SetLayer", "AuthorsSets", "WMSUsers", "KnownLayers")
    res = dellayer(cur, conn, req, lstnewgr, length, 0)
    if res == 1:
      return -2
    tables = []
    values = {}
    values["WMSresources.name"] = "\'user\'"
    values["WMSresources.author"] = "\'%d\'"%pkey
    values["WMSresources.Nwms"] = "KnownLayers.Nwms"
    tables.append("KnownLayers.Nlayer")
    req = BD.ifsome_tables(cur, tables, values, "WMSresources", "KnownLayers")
    if req:
      lst = []
      for i in req:
        lst.append(i[0])
#        print lst
      return lst
    else:
      return -1
#
# update_bd: Refreshes all the resources from the database.
def update_bd(cur, conn, pkey):
  req = BD.select_table(cur, "WMSresources", "Nwms", "request", "author")
  Nwms_def = 0
  for Nwms, request, author in req:
    if author:
      continue
    if request:
      Nwms_def = docs.xml_partition(request, cur, conn, 0)
  errors.input_error("update_bd: Request Update")
  return Nwms_def
  
#
# deleteSet: Remove set "ppkey"
def deleteSet(cur, conn, ppkey, directr):
  values = {}
  values["Nset"] = "\'%d\'"%ppkey
  tables = []
  tables.append("Name")
  res = BD.ifsome_tables(cur, tables, values, "AuthorsSets")
  namefile = res[0][0]
  BD.delete(cur, conn, "Setlayer", values)
  tables = []
  tables.append("Nsld")
  res = BD.ifsome_tables(cur, tables, values, "SLDset")
  for i in res:
    delete_SLD(cur, conn, i[0], ppkey, namefile, directr)
  if platform.system() == 'Linux':
    wayfolder = "%sSLDset/%s"%(directr.strip(), namefile)
    if os.path.exists(wayfolder):
      os.rmdir(wayfolder)
  else:
    directr = directr.strip()
    wayfolder = "%sSLDset\%s"%(directr.replace("\\", "\\\\"), namefile)
    if os.path.exists(wayfolder):
        os.rmdir(wayfolder)
  BD.delete(cur, conn, "AuthorsSets", values)

  req = BD.select_table(cur, "AuthorsSets", "Nset")
  for i in req:
    return int(i[0])
  
  return -1
#
# delete_rs:Remove resources "Nwms".
def delete_rs(cur, conn, Nwms, pkey):
  if not pkey:
    if Nwms:
      return Nwms
    return -1
  if not Nwms:
    return -1
  val = {}
  val["Nwms"] = Nwms
  tables = []
  tables.append("Nlayer")
  res = BD.ifsome_tables(cur, tables, val, "KnownLayers")
  lst_layer = []
  length = 0
  for i in res:
    lst_layer.append("%d"%i)
  length = len(lst_layer)
  tables = []
  tables.append("SetLayer.Nset_layer")
  tables.append("SetLayer.Nlayer")
  tables.append("KnownLayers.Name")
  tables.append("SetLayer.sub_group")
  tables.append("AuthorsSets.Name")
  value = {}
  value["AuthorsSets.Nset"] = "SetLayer.Nset"
  value["KnownLayers.Nlayer"] = "SetLayer.Nlayer"
  req = BD.ifsome_tables(cur, tables, value, "SetLayer", "AuthorsSets", "KnownLayers")
  fl = dellayer(cur, conn, req, lst_layer, length, 1)
  if fl == 0:
    values = {}
    values["Nwms"] = Nwms
    BD.delete(cur, conn, "WMSresources", values)
  else:
    errors.input_error("delete_rs: Error delete resources")
    return Nwms
  req = BD.select_table(cur, "WMSresources", "Nwms", "author")
  for Nwms, author in req:
    if author:
      continue
    else:
#      print Nwms
      return Nwms

  return -1
#
# get_SLDset: Adds a file to the styles SLD in a folder and a set of 
#             information in the database.
def get_SLDset(cur, conn, directory, Nset, Nauthor, nameSet, fileSLD, fl):
  if (fl == -1) or (not Nset):
    return 0
  if fl:
    # file_http
    try:
      infile = urllib.urlopen(fileSLD)
    except:
      print "get_SLDset: Error request %s"%fileSLD
      return 0
    name = fileSLD  
    tmp = name.find("/", 0)
    str_ = tmp
    while(tmp != -1):
      str_ = tmp
      tmp = name.find("/", str_ + 1)
    name = name[str_+1:]
    tmp = fileSLD.find("://", 0) + 3
    URLsld = fileSLD
    fileSLD = fileSLD[tmp:]
    fileSLD = fileSLD.replace("/", "_")
  else:
    infile = fileSLD.file
    fileSLD = fileSLD.filename
    name = fileSLD 
    URLsld = "localhost_%s"%name
  try:
    texts = infile.read()
  except:
    print "get_SLDset: Error read file %s"%name
    return 0
  wayfile = "%sSLDset/%s"%(directory.strip(), nameSet)
    
  if not os.path.exists(wayfile):
    os.mkdir(wayfile, 0777)
  if platform.system() == 'Linux':
    if not os.path.isfile("%s/%s"%(wayfile, fileSLD)):
      try:
        outfile = open("%s/%s"%(wayfile, fileSLD), "wb")
      except:
        print "get_SLDset: File %s already exists"%fileSLD
        return 0
      outfile.write(texts)
      infile.close()
      outfile.close()
    else:
      print "get_SLDset: SLD file %s already exists" % name
      return 0
  else:
    waytofile = "%s\\%s"%(wayfile.replace("\\", "\\\\"), fileSLD.replace("\\", "\\\\"))
    if not os.path.isfile(waytofile):
      try:
        outfile = open(waytofile, "wb")
      except:
        print "get_SLDset: File %s already exists"%fileSLD.replace("\\", "\\\\")
        return 0
      outfile.write(texts)
      infile.close()
      outfile.close()
    else:
      print "get_SLDset: SLD file %s already exists" % name
      return 0
  
  keywords = {}
  lstfind = {}
  lstfind["Name"] = "\'%s\'"%name
  lstfind["URL"] = "\'%s\'"%URLsld
  keywords["Name"] = name
  keywords["URL"] = "%s"%URLsld
  keywords["Nauthor"] = Nauthor
  Nsld_def = BD.crtable(cur, conn, "SLD", "Nsld", keywords, lstfind)
  
  keywords = {}
  lstfind = {}
  lstfind["Nsld"] = "\'%d\'" % Nsld_def
  lstfind["Nset"] = "\'%d\'" % Nset
  keywords["Nsld"] = Nsld_def
  keywords["Nset"] = Nset
  Nsld = BD.crtable(cur, conn, "SLDset", "Nsldset", keywords, lstfind)
  
  return Nsld_def
#
# delete_SLD: Deletes a file to the styles SLD from a folder and a set of 
#             information from the database.
def delete_SLD(cur, conn, Nsld, Nset, nameSET, directr):
  val = {}
  val["SLD.Nsld"] = "%s"%Nsld
  val["SLDset.Nsld"] = "SLD.Nsld"
  tables = []
  tables.append("SLDset.Nset")
  tables.append("SLD.name")
  tables.append("SLDset.Nsldset")
  tables.append("SLD.URL")
  res = BD.ifsome_tables(cur, tables, val, "SLDset", "SLD")
  fl = 0
  namefile = ""
  URLsld = ""
  for Nset_table, name, Nsldset, URL in res:
    if Nset_table == Nset:
      val = {}
      val["Nsldset"] = Nsldset
      BD.delete(cur, conn, "SLDset", val)
      namefile = name
      URLsld = URL
      break
    else:
      fl = 1
  if (not fl) and namefile and URLsld:
    val = {}
    val["Nsld"] = Nsld
    BD.delete(cur, conn, "SLD", val)
  tmp = URLsld.find("://", 0)
  if tmp != -1:
    URLsld = URLsld[tmp+3:]
  URLsld = URLsld.replace("localhost_", "", 1)
  URLsld = URLsld.replace("/", "_")
  if platform.system() == 'Linux':
    waytofile = "%sSLDset/%s/%s"%(directr.strip(), nameSET, URLsld)
    if os.path.isfile(waytofile):
      try:
        os.remove(waytofile)
      except:
        print "delete_SLD: Error delete SLD file %s" % (URLsld)
    else:
      print "delete_SLD: File %s not exists"%URLsld
  else:
    directr = directr.strip()
    waytofile = "%sSLDset\\%s\\%s"%(directr.replace("\\", "\\\\"), nameSET, URLsld)
    if os.path.isfile(waytofile):
      try:
        os.remove(waytofile)
      except:
        print "delete_SLD: Error delete SLD file %s" % (URLsld)
    else:
      print "delete_SLD: File %s not exists"%URLsld
  values = {}
  tables = []
  values["SLDset.Nset"] = "%d"%Nset
  values["SLDset.Nsld"] = "SLD.Nsld"
  tables.append("SLD.Nsld")
  res = BD.ifsome_tables(cur, tables, values, "SLDset", "SLD")
  for Nsld in res:
    return Nsld[0]
  return -1
  
#
# clear_Cache: Deletes files stored in the temporary folder.
def clear_Cache(directory):
  if platform.system() == 'Linux':
    way = "%sSLDset/tmp"%directory.strip()
    tmp = os.listdir(way)
    for filename in tmp:
      os.remove(way + "/" + filename)
  else:
    directory = directory.strip()
    way = "%sSLDset\\tmp"%(directory.replace("\\", "\\\\"))
    tmp = os.listdir(way)
    for filename in tmp:
      os.remove(way + "\\" + filename)
    
