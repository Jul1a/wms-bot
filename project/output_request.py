#!/usr/bin/python

#
# output_request.py: 
#   This file contains functions for handling request.

import parser_xml as docs
import create_bd as BD
import urllib
import os
import platform
import errors


#
# schema: Passes the requested schema
def schema(cur, Nwms, wayURL):
  # Query the URL of the resource
  vals = {}
  vals["Nwms"] = Nwms
  tables = []
  tables.append("URL_dtd")
  res = BD.ifsome_tables(cur, tables, vals, "WMSresources")
  URL_dtd = res[0][0]
#  print URL_dtd

  # Transfer scheme
  try:
    req = urllib.urlopen(URL_dtd).read()
  except:
    errors.input_error("schema: error request \"%s\""%URL_dtd)
  print "Content-Disposition: attachment; charset=utf-8; filename=\"%s\"\r\n\n"\
        %("WMS_MS_Capabilities.dtd"), req

#
# get_SLD: Passes the requested SLD
def get_SLD(cur, SLD, directory):
#  print "%s%s"%(directory, SLD)

  # Formation name of the stored file
  tmp = SLD.find("/", 0)
  str_ = tmp
  while(tmp != -1):
    str_t = str_
    str_ = tmp
    tmp = SLD.find("/", str_ + 1)
  namefile = SLD[str_ + 1:]
  # Formation name of the set
  nameset = SLD[str_t + 1:str_]
#  print nameset, namefile
  
  if nameset != "tmp":
  # If the file is not stored in the temporary folder
    # Define a URL style
    keywords = {}
    keywords["SLD.name"] = "\'%s\'" % namefile
    keywords["SLD.Nsld"] = "SLDset.Nsld"
    keywords["AuthorsSets.name"] = "\'%s\'" % nameset
    keywords["AuthorsSets.Nset"] = "SLDset.Nset"
    tables = []
    tables.append("SLD.URL")
    req = BD.ifsome_tables(cur, tables, keywords, "SLD", "SLDset", "AuthorsSets")
#    print req
    # Specifies the path to the file
    if req:
      for i in req:
        realname = i[0]
#      print realname
      tmp = realname.find("://", 0)
      if tmp != -1:
        realname = realname[tmp + 3:]
#        print realname
        realname = realname.replace("/", "_")
      else:
        tmp = realname.find("localhost_", 0)
        if tmp != -1:
          realname = realname[0:tmp] + realname[tmp+10:]
  else:
  # If the file is stored in the temporary folder
    # Specifies the path to the file
    tmp = namefile.find("://", 0)
    if tmp != -1:
      namefile = namefile[tmp + 3:]
#       print realname
      namefile = namefile.replace("/", "_")
    realname= namefile
#  print "%s%s/%s"%(directory, SLD[0:str_], realname)

  # Read file
  if platform.system() == 'Linux':
    try:
      texts = open("%s%s/%s"%(directory, SLD[0:str_], realname)).read()
    except:
      print "Error File"
      exit(1)
  else:
    try:
      texts = open("%s%s\\%s"%(directory.replace("\\", "\\\\"), SLD[0:str_], realname)).read()
    except:
      print "Error File"
      exit(1)
#  texts = infile.read()
  # Pass read
  print texts
#  infile.close()
  exit(1)

#
# capabilities: Passes the requested Capabilities
def capabilities(cur, filename, wayURL):
  # Define a set number of his name
  vals = {}
  vals["Name"] = "\'%s\'"%filename
  tables = []
  tables.append("Nset")
  res = BD.ifsome_tables(cur, tables, vals, "AuthorsSets")
  Nset = int(res[0][0])
  
  # Define layers and sublayers set
  vals = {}
  listlayer = {}
  WMSlist = []
  vals["SetLayer.Nset"] = "%d"%Nset
  vals["SetLayer.Nlayer"] = "KnownLayers.Nlayer"
  vals["WMSresources.Nwms"] = "KnownLayers.Nwms"
  #vals["WMSresources.author"] = " "
  tables = []
  tables.append("SetLayer.Nlayer")
  tables.append("SetLayer.sub_group")
  tables.append("WMSresources.Nwms")
  tables.append("WMSresources.author")
  res = BD.ifsome_tables(cur, tables, vals, "SetLayer", "WMSresources", "KnownLayers")
#  print res
  
  for Nl, subgroup, Nwms, author in res:
    listlayer[Nl] = Nwms
    if not author:
      WMSlist.append(Nwms)
    if not subgroup:
      continue
      
    # Creating a list of nested layers from subgroup
    lstsub = subgroup.split(";")
    length = len(lstsub)
    for i in range(0, length-1):
      if lstsub[i].find(",") == -1:
        keywords = {}
        keywords["KnownLayers.Nlayer"] = "%s"%lstsub[i]
        keywords["KnownLayers.Nwms"] = "WMSresources.Nwms"
        tables = []
        tables.append("WMSresources.Nwms")
        tables.append("WMSresources.author")
        req = BD.ifsome_tables(cur, tables, keywords, "WMSresources",  "KnownLayers")
        for Nwms_, auth in req:
          if not auth:
            WMSlist.append(Nwms_)
      else:
        lst1sub = lstsub[i].split(",")
        lens = len(lst1sub)
        k = []
        for j in range(0, lens):
          if lst1sub[j].find("=") == -1:
            keywords = {}
            keywords["KnownLayers.Nlayer"] = "%s"%lst1sub[j]
            keywords["KnownLayers.Nwms"] = "WMSresources.Nwms"
            tables = []
            tables.append("WMSresources.Nwms")
            tables.append("WMSresources.author")
            req = BD.ifsome_tables(cur, tables, keywords, "WMSresources",  "KnownLayers")
            for Nwms_, auth in req:
              if not auth:
                WMSlist.append(Nwms_)
          else:
            equal = lst1sub[j].split("=")
            keywords = {}
            keywords["KnownLayers.Nlayer"] = "%s"%equal[1]
            keywords["KnownLayers.Nwms"] = "WMSresources.Nwms"
            tables = []
            tables.append("WMSresources.Nwms")
            tables.append("WMSresources.author")
            req = BD.ifsome_tables(cur, tables, keywords, "WMSresources",  "KnownLayers")
            for Nwms_, auth in req:
              if not auth:
                WMSlist.append(Nwms_)
#          print equal[1]

  # Formation of XML file and send it
  docs.parser_xmlfile(Nset, filename, cur, listlayer, WMSlist, wayURL)

#  print "Nset", Nset, filename, listlayer

#
# GetRequest: Passes the requested "Request"
def GetRequest(cur, conn, Nlayer, namelayer, SLD, SET, reqURL, wayURL, directory):
#  print namelayer
  if not namelayer:
    print "Error Name Layer"
    return -1
  Nset = 0
#  print "SET"
  if SET:
  # Define a set number of his name
#    print SET
    vals = {}
    vals["Name"] = "\'%s\'"%SET
    tables = []
    tables.append("Nset")
    res = BD.ifsome_tables(cur, tables, vals, "AuthorsSets")
#    print "res", res
    if res:
      Nset = res[0][0]
#      print "Nset", Nset
  # Determine the number demanded layer and number of its resource
  vals = {}
  vals["Name"] = "\'%s\'"%namelayer
  tables = []
  tables.append("Nlayer")
  tables.append("Nwms")
  res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
  URL = " "
  if not res:
    req = """SELECT Nlayer, Nwms FROM KnownLayers WHERE Name LIKE '%%:%s';"""\
             % namelayer
    try:
      errors.transact(cur, req)
    except:
      errors.exit_error(1, "Get_Map:Error Select")
    res = cur.fetchall()
  NWMS = -1
#  print res
  for Nl, Nwms in res:
#    print Nset

    # Search for the desired layer in the set
    if Nset:
      req = """SELECT Nset_layer FROM SetLayer WHERE Nset=%s and (Nlayer=%s or 
               sub_group SIMILAR TO '(|%%= |%%, |%%; |%%;)%s( |;|,)%%');"""%(Nset, Nl, Nl)
#      print "req", req
      try:
        errors.transact(cur, req)
      except:
        errors.exit_error(1, "GetRequest:Error Select")
      rem = cur.fetchall()
#      print "rem", rem
      if rem:
        NWMS = Nwms
        break
    else:
      NWMS = Nwms
#  print "NWMS", Nwms
  if NWMS == -1:
    errors.input_error("GetMap: error Layer in request \"%s\""%reqURL)
    exit(1)
  # Definition of the URL of the resource layer
  vals = {}
  vals["Nwms"] = "\'%s\'"%NWMS
  tables = []
  tables.append("URL")
  res = BD.ifsome_tables(cur, tables, vals, "WMSresources")
  for i in res:
    URL = i
    break
#  print "URL = ", URL
  
  # Change the original URL in the request for
  tmp = reqURL.find("?", 0)
  oldURL = reqURL[0:tmp]
#  print oldURL, reqURL
  reqURL = reqURL.replace(oldURL, "%s"%URL, 1)
#  print "reqURL = ", reqURL
#  print "Nset", Nset
  local = oldURL.find("localhost", 0)
  servlocal = URL[0].find("localhost", 0)
  
  # Define a set of SLD
  if Nset and (SLD != -1):
    if not SLD:
    # If the request doesn't specify the style
#      print "not SLD", SLD, Nset
      # Find in table style number for set
      vals = {}
      vals["SLDset.Nset"] = "%s"%Nset
      vals["SLDset.Nsld"] = "SLD.Nsld"
      tables = []
      tables.append("SLD.name")
      tables.append("SLD.Nsld")
      tables.append("SLD.URL")
      res = BD.ifsome_tables(cur, tables, vals, "SLDset", "SLD")
      if res:
      # Adding to the query style
        for i , j, URLsld in res:
          name_SLD = i
          if local == -1:
            reqURL = reqURL + "&SLD=%s?Style=SLDset/%s/%s"%(wayURL, SET, name_SLD)#SLD
            break
          else:
            if (servlocal != -1):
              reqURL = reqURL + "&SLD=%s?Style=SLDset/%s/%s"%(wayURL, SET, name_SLD)#SLD
              break
            if URLsld.find("localhost", 0) == -1:
              reqURL = reqURL + "&SLD=%s"%(URLsld)#STYLE
              break
    else:
    # If the request specify the style
#      print "SLD", SLD
      # Searching in the style set
      vals = {}
      vals["SLDset.Nset"] = "%d"%Nset
      vals["SLDset.Nsld"] = "SLD.Nsld"
      vals["SLD.URL"] = "\'%s\'"%SLD
      tables = []
      tables.append("SLD.name")
      tables.append("SLD.URL")
      res = BD.ifsome_tables(cur, tables, vals, "SLDset", "SLD")
      
      if res:
      # Adding to the query style
        for i, URLsld in res:
          name_SLD = i
          if local == -1:
            reqURL = reqURL.replace(SLD, "%s?Style=SLDset/%s/%s"%(wayURL, SET, name_SLD), 1)
          else:
            if (servlocal != -1):
              reqURL = reqURL.replace(SLD, "%s?Style=SLDset/%s/%s"%(wayURL, SET, name_SLD), 1)
              break
      else:
        # Look the file to a temporary directory
        tmp = SLD.find("://", 0) + 3
#        print tmp
        name_SLD = SLD[tmp:].replace("/", "_")
#        print name_SLD
        fl = 0
#        print "%sSLD/tmp"%directory.strip()
        if platform.system() == 'Linux':
          for filename in os.listdir("%sSLDset/tmp"%directory.strip()):
#          print filename, name_SLD
            if filename == name_SLD.strip():
              fl = 1
              break
        else:
          directory = directory.strip()
          for filename in os.listdir("%sSLDset\\tmp"%directory.replace("\\", "\\\\")):
#          print filename, name_SLD
            if filename == name_SLD.strip():
              fl = 1
              break
        if not fl:
        # If the file is not found in the temporary directory
#          print fl, SLD
          try:
            texts = urllib.urlopen(SLD).read()
          except:
            errors.input_error("GetRequest: error request \"%s\""%SLD)
#          print "%sSLD/tmp/%s"%(directory.strip(), name_SLD)

          # Save the file to a temporary directory
          if platform.system() == 'Linux':
            try:
              infile = open("%sSLDset/tmp/%s"%(directory.strip(), name_SLD), 'w')
            except:
              errors.input_error("GetRequest: error open \"%s\""%name_SLD)
          else:
            try:
              infile = open("%sSLDset\\tmp\\%s"%(directory.replace("\\", "\\\\"), name_SLD), 'w')
            except:
              errors.input_error("GetRequest: error open \"%s\""%name_SLD)
          infile.write(texts)
          try:
            infile.close()
          except:
            errors.input_error("GetRequest: error close \"%s\""%name_SLD)
        # Replace the query path to the style
        if local == -1:
          reqURL = reqURL.replace(SLD, "%s?Style=SLDset/tmp/%s" % (wayURL, name_SLD), 1)
        else:
          if (servlocal != -1):
            reqURL = reqURL.replace(SLD, "%s?Style=SLDset/tmp/%s" % (wayURL, name_SLD), 1)
#          print "req", reqURL
#        print name_SLD
#  print reqURL    

  # Forwards the data on inquiries received
  try:
    ifile = urllib.urlopen(reqURL)
    req = ifile.read()
  except:
    errors.input_error("GetMap: error request \"%s\""%reqURL)
  ifile.close()
  return req
  
