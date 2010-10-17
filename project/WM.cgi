#!/usr/bin/python

import cgi, sys, os
import create_bd as BD
import parser_xml as docs
import administration as adminMenu
import html_code as hcode
import Menu
import errors
import re, urllib

print "Content-type: text/html; charset=utf-8\n"

# Open database "mydb", "julia"
conn, cur, directory = BD.open_BD()

#docs.xml_partition("wms.xml", cur, conn, 1)
#docs.xml_partition("nativecap.xml", cur, conn, 1)
#docs.xml_partition("wms1.xml", cur, conn, 1)

MAXLENSTR = 100

values = {}
listSet = {}

lists = ""
listcheckbox = ""
namefile = ""
wayURL = ""
SLD_def = ""
listSLD = ""
list_noset = ""

ppkey = 0 
pkey = 0
lst = 0
wmslists = 0
Nwms = 0
Nwms_user = 0
lst_layer = []
lstset = []
lstsub = []
lstnewgr = []
form = cgi.FieldStorage()

wmslists = form.has_key("wmslists")
flrsc = form.has_key("resources")
flupdate = form.has_key("Update")
fldeleters = form.has_key("RSDelete")

flnamefile = form.has_key("filename")
flnameset = form.has_key("setlists")
fleditset = form.has_key("editSet")
fldelset = form.has_key("DeleteSet")

flnewgr = form.has_key("newgroup")
flnamegr = form.has_key("name_gr")
fltitlegr = form.has_key("title_gr")
flabstrgr = form.has_key("abstract_gr")
fleditgr = form.has_key("Edit_group")
fladdgrset = form.has_key("Add")
fldelgr = form.has_key("delgr")

fl_SLD = form.has_key("SLD")
fladd_SLD = form.has_key("OK_SLD")
flcache = form.has_key("clearCache")

flsave = form.has_key("save")

flayer = form.has_key("Layer")
fl_noset = form.has_key("list_noset")
fldelete = form.has_key("deletes")
flset = form.has_key("inset")
flgroup = form.has_key("ingroup")
flinset = form.has_key("Set")
flinsub = form.has_key("subSet")
fladdgr = form.has_key("Add_inset")


pkey = adminMenu.Author(cur, conn, "Anonim", "Anonim")

if form.has_key("addSLD") and (form.has_key("filename") or form.has_key("setlists")):
  if form.has_key("setlists"):
    try:
      ppkey = int(form["setlists"].value)
    except:
      print "WM.cgi: Error name set"
      exit(1)
    value = {}
    tables = []
    value["Nset"] = ppkey
    tables.append("Name")
    res = BD.ifsome_tables(cur, tables, value, "AuthorsSets")
    namefile = res[0][0]
  else:
    namefile = form["filename"].value
  if wmslists:
    wmslists = form["wmslists"].value
  else:
    wmslists = ""
  if flnewgr:
    newgroup = form["newgroup"].value
  else:
    newgroup = ""
  html = hcode.hlist_newSLD()%(namefile, wmslists, newgroup)
  print html
  exit(0)

if fldelset:
  if flnameset:
    try:
      ppkey = int(form["setlists"].value)
    except:
      print "WM.cgi: Error name set"
      exit(1)
  if flnamefile:
    namefile = form["filename"].value
    value = {}
    tables = []
    value["name"] = "\'%s\'"%namefile
    tables.append("Nset")
    res = BD.ifsome_tables(cur, tables, value, "AuthorsSets")
    ppkey = res[0][0]
  if ppkey:
    lst = adminMenu.deleteSet(cur, conn, ppkey, directory)
    if lst != -1:
      ppkey = lst
      value = {}
      tables = []
      value["Nset"] = ppkey
      tables.append("Name")
      res = BD.ifsome_tables(cur, tables, value, "AuthorsSets")
      namefile = res[0][0]
      if namefile:
        flnameset = 1
        flnamefile = 1
    else:
      ppkey = 0
      flnameset = 0


if flayer:
  strlst = urllib.unquote(form["Layer"].value).strip()
  lst_layer = strlst.split(";")
  if "" in lst_layer:
    lst_layer.remove("")
    
if wmslists:
  try:
    Nwms = int(form["wmslists"].value)
  except:
    print "WM.cgi: Error name resources%d"%wmslists
    exit(1)

  if fldeleters:
    lst = adminMenu.delete_rs(cur, conn, Nwms, pkey)
    if lst != -1:
      wmslists = 1
      Nwms = lst
    else:
      if pkey:
        wmslists = 0
        Nwms = 0
if flupdate:
  Nwms = adminMenu.update_bd(cur, conn, pkey)
  if Nwms:
    wmslists = 1
if flinset:
  #tmp = ""
  lstset = form.getlist("Set")
  #lstset.append("%s"%tmp)
if flinsub:
  lstsub = form.getlist("subSet")
if flnewgr:
  lstnewgr = form.getlist("newgroup")
  
if flrsc:
  namersc = urllib.unquote(form["resources"].value)
  if len(namersc) > MAXLENSTR:
    print "WM.cgi: Error too long query string"
    flrsc = 0
  if flrsc:
    fl = 0
    for request in ["REQUEST", "request", "Request"]:
      if namersc.find(request, 0) != -1:
        fl = 1
        break
    if not fl:
      if (namersc.find("?", 0)) != -1:
        namersc = namersc + "&REQUEST=GetCapabilities"
      else:
        namersc = namersc + "?REQUEST=GetCapabilities"
    Nwms = docs.xml_partition(namersc, cur, conn, 0)
    wmslists = 1
if flnameset and (not ppkey):
  try:
    ppkey = int(form["setlists"].value)
  except:
      print "WM.cgi: Error name set"
      exit(1)
  value = {}
  tables = []
  value["Nset"] = ppkey
  tables.append("Name")
  res = BD.ifsome_tables(cur, tables, value, "AuthorsSets")
#  print res[0][0]
  namefile = res[0][0]
  if namefile:
    flnamefile = 1
else:
  if flnamefile and (not ppkey):
    namefile = form["filename"].value
    if len(namefile) > MAXLENSTR:
      print "WM.cgi: Error set name too long %s"% namefile
      namefile = " "
      flnamefile = 0
    if not re.match('[a-z, A-Z, 0-9, -, _]', namefile):
      print "Error name set %s"% namefile
      namefile = " "
      flnamefile = 0
    else:
      namefile = re.sub(".xml$", "", namefile)
      namefile = namefile.replace(" ", "_")
      ppkey = adminMenu.get_namesetbd(cur, conn, namefile, pkey)

if fleditset and form.has_key("editname"):
  newname = form["editname"].value
  value = {}
  tables = []
  value["name"] = "\'%s\'"%newname
  tables.append("Nset")
  keys = BD.ifsome_tables(cur, tables, value, "AuthorsSets")
  if (not keys) and ppkey:
    req = "UPDATE AuthorsSets SET name = \'%s\' WHERE Nset = %d;"%(newname, ppkey)
    try:
      errors.save_transact(cur, conn, req)
      namefile = newname
    except:
      errors.exit_error(1, "Error edit name set")
if fldelete:
  if ppkey and (form["deletes"].value != 0):
    #lst = form.getlist("Set")
    if lstset:
      adminMenu.shaper_setbd(cur, conn, ppkey, lstset)
    else:
      if lstsub:
        adminMenu.shaper_subset(cur, conn, ppkey, lstsub)

if fl_noset and pkey and ppkey:
  lst = urllib.unquote(form["list_noset"].value)
  if ((lst == "-1") or (lst == "None")):
    req = "UPDATE AuthorsSets SET layer_noset = \'%s\' WHERE Nset = %d;"%("", ppkey)
    try:
      errors.save_transact(cur, conn, req)
    except:
      errors.exit_error(1, "Error update set")
  else:
    req = "UPDATE AuthorsSets SET layer_noset = \'%s\' WHERE Nset = %d;"%(lst, ppkey)
    try:
      errors.save_transact(cur, conn, req)
    except:
      errors.exit_error(1, "Error update set")
if pkey and ppkey:
  vals = {}
  tables = []
  vals["AuthorsSets.Nauthor"] = pkey
  vals["AuthorsSets.Nset"] = ppkey
  vals["AuthorsSets.Nauthor"] = "WMSUsers.UID"
  tables.append("AuthorsSets.layer_noset")
  res = BD.ifsome_tables(cur, tables, vals, "AuthorsSets", "WMSUsers")
  if res:
    list_noset = res[0][0]
    if list_noset:
      lst = list_noset.split(';')
      if ('' in lst):
        lst.remove('')
      add_inset = len(lst)
  else:
    list_noset = ""
if flayer:
  if flinset and ppkey and pkey:
    adminMenu.add_ingroup(cur, conn, ppkey, pkey, lstset, lst_layer)
  if flinsub and ppkey and pkey:
    adminMenu.addsub_ingroup(cur, conn, ppkey, pkey, lstsub, lst_layer)

if flnamegr and fltitlegr and pkey and fleditgr:
  if (len(form["name_gr"].value) > MAXLENSTR) or (len(form["title_gr"].value) > MAXLENSTR):
    print "WM.cgi: Error incorrectly entered parameters of a new layer group"
  else:
    req = "UPDATE KnownLayers SET Name = \'%s\', Title = \'%s\'"%\
          (urllib.unquote(form["name_gr"].value), \
           urllib.unquote(form["title_gr"].value))
    if flabstrgr:
      req += ", Abstract = \'%s\'"%urllib.unquote(form["abstract_gr"].value)
    req += " WHERE Nlayer = %s;"%(form["newgroup"].value)
    try:
      errors.save_transact(cur, conn, req)
    except:
      errors.exit_error(1, "Error edit new group")
if flnamegr and fltitlegr and pkey and (not fleditgr):
  if (len(form["name_gr"].value) > MAXLENSTR) or (len(form["title_gr"].value) > MAXLENSTR):
    print "WM.cgi: Error incorrectly entered parameters of a new layer group"
  else:
    value = {}
    value["Name"] = "user"
    value["Title"] = "user_wms"
    value["author"] = pkey
    value["access"] = ""
    Nwms_user = BD.create_table(cur, conn, "WMSresources", "Nwms", value, "Name", "author")
    #print Nwms_user
    #conn.set_character_set('utf8')
    #conn.commit()
    value = {}
    value["Nwms"] = Nwms_user
    value["Nl_group"] = -1
    value["Name"] = "%s"%urllib.unquote(form["name_gr"].value)
    value["Title"] = "%s"%urllib.unquote(form["title_gr"].value)
    strs = ""
    if flabstrgr:
      strs = form["abstract_gr"].value
      if len(strs) > MAXLENSTR:
        value["Abstract"] = strs[0:MAXLENSTR]
      else:
        value["Abstract"] = "%s"%urllib.unquote(form["abstract_gr"].value)
      strs = "<Abstract>%s</Abstract>"%value["Abstract"]
    value["LayerCapabilites"] = """<Layer>\n<Name>%s</Name>\n<Title>%s</Title>\n%s
                                </Layer>"""%(value["Name"].strip(),\
                                   value["Title"].strip(), strs.strip())
    lstfind = {}
    lstfind["Name"] = "\'%s\'"%urllib.unquote(form["name_gr"].value)
    lstfind["Nwms"] = Nwms_user
    #Nlayer_user = BD.create_table(cur, conn, "KnownLayers", "Nlayer", value, "Name", "Nwms")
    Nlayer_user = BD.crtable(cur, conn, "KnownLayers", "Nlayer", value, lstfind)
    if Nlayer_user:
      lstnewgr.append("%d"%Nlayer_user)
      flnewgr = 1

if flnewgr and fladdgr:
  fl = 1
  fladdinset = int(form["Add_inset"].value);
  if flinset and ppkey and (fladdinset != 0) and (not flayer) and pkey:
    adminMenu.add_ingroup(cur, conn, ppkey, pkey, lstset, lstnewgr)
    fl = 0
  if flinsub and ppkey and (fladdinset != 0) and (not flayer) and pkey:
    adminMenu.addsub_ingroup(cur, conn, ppkey, pkey, lstsub, lstnewgr)
    fl = 0

if flnewgr and ppkey and fladdgrset and (not flayer):
  adminMenu.get_inset(cur, conn, ppkey, lstnewgr)

if flnewgr and fldelgr:
  lst = adminMenu.delnewgr(cur, conn, pkey, lstnewgr)
  if lst == -2:
    flnewgr = 1
    lstnewgr = form.getlist("newgroup")
  if (lst != -1) and (lst != -2):
    flnewgr = 1
    lstnewgr = lst

if flsave:
  if ppkey and namefile:
    #print ppkey
    mytext = os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"]
    tmp_ = mytext.find("WM.cgi?")
    #service=WMS&version=1.1.0&request=capabilities&
    wayURL = "http://" + mytext[0:tmp_] + "WMS_RMset.cgi?Set=%s"%(namefile)
    #    print "URL: ", wayURL
  else:
    errors.input_error("<p>Error save: don't input name file</p>")
if flcache:
  adminMenu.clear_Cache(directory)
if fl_SLD:
  SLD_def = form["SLD"].value
  if form.has_key("deleteSLD"):
#    print "delete_SLD", SLD_def, ppkey, namefile, directory
    lst = adminMenu.delete_SLD(cur, conn, SLD_def, ppkey, namefile, directory)
    if lst != -1:
      SLD_def = "%d"%lst
    else:
      SLD_def = ""
if fladd_SLD:
  fl = -1
  fileSLD = ""
  if form.has_key("file_local") and form["file_local"].filename != "":
    fileSLD = form["file_local"]
    fl = 0
    lst = adminMenu.get_SLDset(cur, conn, directory, ppkey, pkey, namefile, fileSLD, fl)
    if lst:
      SLD_def = "%d"%lst
  if form.has_key("file_http") and (not form.has_key("file_local")):
    fileSLD = urllib.unquote(form["file_http"].value)
    maxstr = 2*MAXLENSTR
    if len(fileSLD) > maxstr:
      print "WM.cgi: Error too long query string"
    else:
      fl = 1
      lst = adminMenu.get_SLDset(cur, conn, directory, ppkey, pkey, namefile, fileSLD, fl)
      if lst:
        SLD_def = "%d"%lst

message = ""
if wmslists:
#  if not flayer:
  if flnamefile:
    if wayURL:
      message = "%s"%wayURL
#int(form["deletes"].value) == 0
if flayer and (not flinset) and (not flinsub) and (not fldelete):
  adminMenu.get_inset(cur, conn, ppkey, lst_layer)
if (not Nwms) and pkey:
  val = {}
  tables = []
  res = BD.select_table(cur, "WMSresources", "Nwms", "author", "access")
  for N, author, access in res:
    if author or access:
      continue
    Nwms = N
    wmslists = 1
    break
add_inset = 0
#iffile = open("log", "w");
#iffile.write("dsfds%s"%list_noset)
#iffile.close()
if wmslists:
  strNwms = "%d"%Nwms
else:
  strNwms = ""

if (not ppkey) and pkey:
  vals = {}
  tables = []
  vals["AuthorsSets.Nauthor"] = pkey
  vals["AuthorsSets.Nauthor"] = "WMSUsers.UID"
  tables.append("AuthorsSets.Nset")
  tables.append("AuthorsSets.Name")
  res = BD.ifsome_tables(cur, tables, vals, "AuthorsSets", "WMSUsers")
  for Nset, name in res:
    ppkey = Nset
    namefile = name
    break
if ppkey:
  strppkey = "%d"%ppkey
else:
  strppkey = ""
if not lstnewgr:
  if not Nwms_user and pkey:
    tables = []
    tables.append("Nwms")
    value = {}
    value["author"] = "\'%d\'"%pkey
    Nwm = BD.ifsome_tables(cur, tables, value, "WMSresources")
    if Nwm:
      Nwms_user = int(Nwm[0][0])
  if Nwms_user:
    tables = []
    value = {}
    tables.append("Nlayer")
    value["Nwms"] = "%s"%Nwms_user
    res = BD.ifsome_tables(cur, tables, value, "KnownLayers")
    if res:
      lstnewgr.append("%s"%res[0])
      flnewgr = 1
if flnewgr:
  strnwgr = "%s"%lstnewgr
  Nnwgr = "%d"%(int(lstnewgr[0]))
else:
  strnwgr = ""
  Nnwgr = ""
if (not SLD_def) and ppkey:
  val = {}
  tables = []
  val["SLDset.Nset"] = "%s"%ppkey
  val["SLDset.Nsld"] = "SLD.Nsld"
  tables.append("SLD.Nsld")
  res = BD.ifsome_tables(cur, tables, val, "SLDset", "SLD")
  if res:
    SLD_def = "%d"%res[0][0]

if ppkey:
  set_layers, set_checkdel, set_checkincl =  Menu.MenuSet(cur, conn, namefile, ppkey)
else:
  set_layers, set_checkdel, set_checkincl =  Menu.MenuSet(cur, conn, namefile, 0)
str_newgr = ""
if Nnwgr:
  val = {}
  tables = []
  val["Nlayer"] = "%s"%Nnwgr
  tables.append("Name")
  res = BD.ifsome_tables(cur, tables, val, "KnownLayers")
  str_newgr = """<span class = "moves" onmousedown="drag_object(event, this, 'lr_%s')" >
                  %s
                  </span>
              """%(Nnwgr, res[0][0])
  #str_newgr = ""
#set_checkdel = ""
#set_checkincl = ""
#message = ""
html = hcode.hmain_list()%\
            (\
             Menu.MenuResources(cur, conn, wmslists, Nwms, "%d"%pkey),\
             strppkey, Nnwgr, SLD_def, \
             strppkey, strNwms, Nnwgr, SLD_def, \
             strppkey, strNwms, Nnwgr, SLD_def, \
             strppkey, strNwms, Nnwgr, SLD_def, \
             Menu.MenuLayers(cur, ppkey, Nwms, " "),\
             strppkey, strNwms, Nnwgr, SLD_def, \
             Menu.get_newlayers(cur, conn, Nwms_user, Nwms, Nnwgr, pkey, namefile),\
             strppkey, strNwms, SLD_def, \
             str_newgr,\
             namefile, strNwms, SLD_def, \
             Nnwgr, strppkey, strNwms, SLD_def, \
             Nnwgr, strppkey, strNwms, SLD_def, \
             Menu.get_listset(cur, conn, "%d"%pkey, namefile),\
             Nnwgr, strNwms, \
             Nnwgr, strNwms, \
             namefile, \
             Nnwgr, strppkey, strNwms,\
             namefile, \
             Nnwgr, strppkey, strNwms,\
             namefile, \
             set_layers,\
             strppkey, strNwms, Nnwgr, SLD_def, \
             set_checkincl, add_inset, list_noset,\
             set_checkdel, \
             message, \
             Nnwgr, strppkey, strNwms,\
             Menu.get_SLD(cur, conn, ppkey, SLD_def), \
             Nnwgr, strppkey, strNwms, \
             Nnwgr, strppkey, strNwms, \
             SLD_def, Nnwgr, strppkey, strNwms, \
             SLD_def, Nnwgr, strppkey, strNwms \
             ) 

print html
# Menu.MenuSet(cur, conn, namefile), \
# Close database
BD.close_BD(conn)

