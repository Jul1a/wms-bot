#!/usr/bin/python

#
# WMS_RMset.cgi: Proxy server. Receives request for schema, GetCapabilities,
#                GetMap, GetFeatureInfo.

import cgi, sys, os
import create_bd as BD
#import parser_xml as docs
import output_request as REQ
import errors
import urllib

#                <H1>The list of accessible wms layers</H1>
html_begin = """<HTML>
                <HEAD>
                <TITLE>Get XML</TITLE>
                </HEAD>
                <BODY>
                <TABLE>
                <form action = "WM.cgi" method = "GET"><TR><TD align = "center">
                """
form = cgi.FieldStorage()

flschema = form.has_key("schema")
flnamefile = form.has_key("Set")
flrequest = form.has_key("request")
flformat = form.has_key("format")

# Determining the type of request
if not flrequest:
  flrequest = form.has_key("REQUEST")
  if flrequest:
    # Request is specified as "REQUEST"
    form_req = form["REQUEST"].value
  else:
    form_req = " "
else:
  # Request is specified as "request"
  form_req = form["request"].value

# Determine the format for the answer
if not flformat:
  # Format is specified as "FORMAT"
  flformat = form.has_key("FORMAT")
  if flformat:
    format = form["FORMAT"].value
  else:
    format = "text/html"
else:
  # Format is specified as "format"
  format = form["format"].value
# Open database 
conn, cur, directory = BD.open_BD()

# Forming the path to the proxy
mytext = os.environ["HTTP_HOST"] + os.environ["REQUEST_URI"]
tmp_ = mytext.find("?")
wayURL = "http://" + mytext[0:tmp_]

#print wayURL

# Definition of SLD in the request
if form.has_key("Style"):
#  print "Content-Type:application/octet-stream; name=\"%s.xml\"\r\n"%("style");
  print "Content-type: text/xml; charset=utf-8\n" # xml
  SLD = urllib.unquote(form["Style"].value)
  REQ.get_SLD(cur, SLD, directory.strip())

if flschema:
#  print "Content-type: text/html\n"
#  html = html_begin + "<p>Error file name</p>" + "</TD></TR></FORM></TABLE></BODY><HTML>"
#  print flschema
#  print "Content-Disposition: attachment; filename=\"%s.xml\"\r\n\n"%(filename),\
  Nwms = form["schema"].value
#  print Nwms
  # Transfer of the requested scheme
  REQ.schema(cur, Nwms, wayURL)
else:
  if (form_req in ["capabilities", "GetCapabilities"]):
  # If the request is GetCapabilities
    if flnamefile:
      filename = form["Set"].value
#      print "Content-type: text/html; charset=utf-8\n"

      # Transfer of the requested "Capabilities"
      REQ.capabilities(cur, filename, wayURL)

#   print wayURL
#   print "Content-Type:application/octet-stream; name=\"%s.xml\"\r\n"%(form["file"].value);
#   print cgi.escape(docs.parser_xmlfile(form["Nset"].value, filename, cur, listlayer))
#   print "Content-Disposition: attachment; filename=\"%s.xml\"\r\n\n"%(filename),\

    else:
      print "Content-type: text/html; charset=utf-8\n"
      html = html_begin + "<p>Error file name</p>" + "</TD></TR></FORM></TABLE></BODY><HTML>"
      print html

  if form_req == "GetMap":
  # If the request is GetMap
    # Determine the format for the answer
    if (format in ["application/openlayers", "atom xml", "atom+xml"]):
      print "Content-type: text/html; charset=utf-8\n"
    else:
      print "Content-type: %s; charset=utf-8\n"%format
#    print "Content-type: text/html; charset=utf-8\n"
    
    # Determination of the requested layers
    flNlayer = form.has_key("Nlayer")
    Nlayer = 0
    if flNlayer:
      Nlayer = form["Nlayer"].value
    fllayer = form.has_key("layers")
    namelayer = " "
    strlayer = ""
    if fllayer:
      namelayer = urllib.unquote(form["layers"].value)
      strlayer = "layers"
    if form.has_key("LAYERS"):
      namelayer = urllib.unquote(form["LAYERS"].value)
      strlayer = "LAYERS"
  
  #  print namelayer

    # Query definition
    reqURL = wayURL + "?" + os.environ["QUERY_STRING"]
    #iffile = open("request", "w")
    #iffile.write(reqURL)
  #  print reqURL

    # Definition of SLD in the request
    if form.has_key("SLD"):#SLD
      SLD = urllib.unquote(form["SLD"].value)#SLD
    else:
      if form.has_key("Sld"):#Sld
        SLD = urllib.unquote(form["Sld"].value)#Sld
      else:
        SLD = 0
    # Definition set name
    SET = " "
    if form.has_key("Set"):
      SET = urllib.unquote(form["Set"].value)

#    print "GetRequest", SLD
    # Definition of style in the request
    style = ""
    strstyle = ""
    for i in ["STYLES", "styles", "Styles"]:
      if form.has_key(i):
        style = form[i].value
        strstyle = i
        break
    # Creating a list of required layers
    lst_layer = namelayer.split(',')
    lst_style = style.split(',')
    len_l = len(lst_layer)
#    iffile.write("\n%d"%len_l)
    if len_l > 0 and len_l < 2:
    # If requested by a single layer
      print REQ.GetRequest(cur, conn, Nlayer, namelayer, SLD, SET, reqURL, wayURL, directory)
    else:
      if len_l > 0:
      # If the request is more than one layer
        if len(lst_style) == len_l:
        # If the number of required layers equals the number of required styles
          req = ""
          Nwms_tmp = ""
          flag = 0
          for j in range(0, len_l):
            # Determine the Nwms j-layer
            vals = {}
            vals["Name"] = "\'%s\'"%lst_layer[j]
            tables = []
            tables.append("Nwms")
            # Search layer by name
            res = BD.ifsome_tables(cur, tables, vals, "KnownLayers")
            URL = " "
            if not res:
              # Search the layer with similar names ":name"
              req = """SELECT Nlayer, Nwms FROM KnownLayers WHERE Name LIKE '%%:%s';"""\
                        % namelayer
              try:
                errors.transact(cur, req)
              except:
                errors.exit_error(1, "Get_Map:Error Select")
              res = cur.fetchall()
            # Check supplies of all required layers of a single resource (flag=0)
            Nwms_t = res[0][0]
            if (Nwms_t):
              if Nwms_tmp:
                if Nwms_t != Nwms_tmp:
                  flag = 1
                  break
              else:
                Nwms_tmp = Nwms_t
            else:
              flag = 1
          
          if flag == 0:
          # Required layers belong to the same resource
            namelayer = lst_layer[0]
            SLD = -1
            # Pass the response to complete request
            print REQ.GetRequest(cur, conn, Nlayer, namelayer, SLD, SET, reqURL, wayURL, directory)
          else:
          # Required layers belong to different resources
            for j in range(0, len_l):
              # For each layer is formed by the desired request with one layer
              # and an appropriate style
              pos1 = reqURL.find(strlayer)
              pos1 += 6 #LAYERS - 6 letter
              pos2 = reqURL.find("&", pos1)
              strs = reqURL[pos1:pos2]
              reqURL1 = reqURL[:pos1] + "=%s&"%lst_layer[j] + reqURL[pos2+1:]
              pos1_style = reqURL1.find(strstyle)
              pos1_style += 6
              pos2_style = reqURL1.find("&", pos1_style)
              reqURL1 = reqURL1[:pos1_style] + "=%s&"%lst_style[j] + reqURL1[pos2_style+1:]

              # Pass the response to complete request
              namelayer = lst_layer[j]
              req = REQ.GetRequest(cur, conn, Nlayer, namelayer, SLD, SET, reqURL1, wayURL, directory)
              print req
            
  if form_req == "GetFeatureInfo":
  # If the request is GetFeatureInfo
    # Determine the format for the answer
    if not (form.has_key("INFO_FORMAT")):
      if form.has_key("infoFormat"):
        format = urllib.unquote(form["infoFormat"].value)
      else:
        format = "text/html"
    else:
      format = form["INFO_FORMAT"].value
    
    # Determination of the requested layers
    namelayer = " "
    if (form.has_key("layers")):
      namelayer = urllib.unquote(form["layers"].value)
    if (form.has_key("LAYERS")):
      namelayer = urllib.unquote(form["LAYERS"].value)
    if (form.has_key("Layers")):
      namelayer = urllib.unquote(form["Layers"].value)
    
    # Query definition
    reqURL = wayURL + "?" + os.environ["QUERY_STRING"]
    
    # Determine the format for the answer
    if (format in ["application/vnd.ogc.gml"]) and namelayer:
      print "Content-Disposition: attachment; charset=utf-8; filename=\"%s\"\r\n"%(namelayer)
    else:
      print "Content-type: %s; charset=utf-8\n"%format
    
    SLD = -1
    # Definition set name
    SET = " "
    if form.has_key("Set"):
      SET = urllib.unquote(form["Set"].value)
    # Transfer of the requested "FeatureInfo"
    print REQ.GetRequest(cur, conn, 0, namelayer, SLD, SET, reqURL, wayURL, directory)

