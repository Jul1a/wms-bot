#!/usr/bin/python

import cgi, sys
import create_bd as BD
import parser_xml as docs
import Menu
import errors

print "Content-type: text/html\n"


values = {}
listSet = {}

lists = ""
set_layers = ""
listcheckbox = ""
namefile = ""
#                <H1>The list of accessible wms layers</H1>
html_begin = """<HTML>
                <HEAD>
                <TITLE>Control system WMS resources</TITLE>
                <meta http-equiv="Content-Type" content="test/html" charset="utf-8">
                <style type = "text/css">
                .luinput {
                  color: black;
                  background-color: black;
                  background: #fffacd;
                }
                checkbxinput {
                  vertical-align: top;
                }
                .widthed {
                  width: 100%;
                  height: 100%;
                  font-size:12pt;
                }
                .errdisable {
                  color: #717D7D;
                  background-color: white;
                }
                </style>
                </HEAD>
                <BODY>
                """

form = cgi.FieldStorage()

flgroup = form.has_key("overgroup")
flname = form.has_key("filename")
flwms = form.has_key("Nwms")
fleditgr = form.has_key("editgr")

filename = ""
Nwms = ""

if flname:
  filename = form["filename"].value
#  filename = "".join(filename)
#  print filename
if flwms:
  Nwms = "<INPUT TYPE=hidden name=\"wmslists\" value = %s>"%form["Nwms"].value
else:
  Nwms = ""
#  print Nwms
if not fleditgr:
  html = html_begin + """
                      <H1>New group of layers<H1>                
                      <TABLE>
                    <form action = "WM.cgi" method = "GET"><TR><TD align = "center">
                    <TR><TD>Name new group of layers</TD>
                        <TD><INPUT TYPE=text name="name_gr" size = 20 maxlen = 20></TD>
                    </TR>
                    <TR><TD>Title</TD>
                        <TD><INPUT TYPE=text name="title_gr" size = 20 maxlen = 20></TD>
                    </TR>
                    <TR><TD>Abstract</TD>
                        <TD><INPUT TYPE=text name="abstract_gr" size = 50 maxlen = 50></TD>
                    </TR>
                    <TR>
                        <TD>
                            <INPUT TYPE=hidden name="filename" value = %s></TD>
                        <TD> %s</TD>
                    </TR>
                    <TR>
                    <TD><INPUT TYPE=SUBMIT value = "Ok_layer" name="OK"></TD>
                    </TR>
                    """%(filename, Nwms)
else:
  conn, cur, directory = BD.open_BD()
  vals = {}
  tables = []
  vals["Nlayer"] = int(form["newgroup"].value)
  tables.append("Name")
  tables.append("Title")
  tables.append("Abstract")
  res = BD.ifsome_tables(cur, tables, vals,  "KnownLayers")
  for n, t, a in res:
    name = n
    title = t
    abstract = a 
  html = html_begin + """
                      <H1>Edit new group of layers<H1>                
                      <TABLE>
                      <form action = "WM.cgi" method = "GET">
                      <TR>
                        <TD align = "center">
                        <TR>
                          <TD>New name group of layers</TD>
                          <TD>
                            <INPUT TYPE=text name="name_gr" size = 20 maxlen = 20
                             value = "%s">
                          </TD>
                        </TR>
                        <TR>
                          <TD>Title</TD>
                          <TD>
                            <INPUT TYPE=text name="title_gr" size = 20 maxlen = 20
                             value = "%s">
                          </TD>
                        </TR>
                        <TR>
                          <TD>Abstract</TD>
                          <TD>
                            <INPUT TYPE=text name="abstract_gr" size = 50 maxlen = 50
                             value = "%s">
                          </TD>
                        </TR>
                        <TR>
                          <TD>
                            <INPUT TYPE=hidden name="filename" value = %s>
                            <INPUT TYPE=hidden name="newgroup" value = %s>
                          </TD>
                          <TD>%s</TD>
                        </TR>
                        <TR>
                          <TD>
                            <INPUT TYPE=SUBMIT value = "Edit" name="Edit_group">
                          </TD>
                        </TR>
                     """%(name, title, abstract, filename, form["newgroup"].value, Nwms)
html +=  """
              </form>
              </TABLE>
              </BODY>
              </HTML>
           """

print html

