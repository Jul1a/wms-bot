# 
# Menu.py: Contains functions handles the menu window (lists of resources, 
#          layers, set, SLD and etc.). 

import create_bd as BD
import html_code as hcode
import errors

#
# get_layers: Builds hierarchy of layers defined WMS a resource. Cur - cursor of
#             database, Nset - set primary key defined user, Nwms - primary key WMS 
#             resources in BD, Nl_group - number of layer group, lists - html list.
#             Return html list.
def get_layers(cur, Nset, Nwms, Nl_group, instr, lists, lst_layer, i):
  values = {}
  keywords = {}
  tables = []
  keywords["Nset"] = Nset
  tables.append("Nset_layer")
  
  # Reception of the list of layers of a WMS resource being in group Nl_group
  values["Nwms"] = Nwms
  values["Nl_group"] = Nl_group
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Name",\
                            "Title", "access_mode")
  for Nl, name, title, access in res:
    if name:
      strhelp = name
    else:
      strhelp = title
    # Find layer Nl in set Nset
    keywords["Nlayer"] = Nl
    req = BD.ifsome_tables(cur, tables, keywords, "SetLayer")
    if access == "notWMS":
      continue;
    #lists = lists + "<TR>"
    values = {}
    values["Nwms"] = Nwms
    values["Nl_group"] = Nl
    req_sublayer = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Name",\
                            "Title", "access_mode")

    if i%2 == 0:
      class_style = "class = \"dd_even\""
    else:
      class_style = "class = \"dd_odd\""
    if req:
    #li class = "luinput"
      lists = lists + """<dd id = "layer_%d">"""%(Nl)
    else:
      lists = lists + """<dd id = "layer_%d">"""%(Nl)

#    lst_layer = lst_layer + "<p %s>"%class_style
# style = \"height: 19.9px;\"
#<INPUT type = "checkbox" 
    lst_layer = lst_layer + """ 
                                <dd id = "layer%d" style = "margin:0;">
                                  <p %s align = "center">
                                    <a class = "tooltip" href = "#">
                                      <img src = "/icons/empty_check4.gif" name = "Layer" class = "smallcheck"
                                        id = "checklayer%d" value = 0 onClick = "click_layer(this, this.form);" />
                                      <spany class = "classic">%s</spany>
                                    </a>
                                  </p>
                            """%(Nl, class_style, Nl, strhelp)
                            #
    lists = lists + "<p style = \"height: 19.89px;\" %s>"%class_style
    i += 1
    if req_sublayer:
    #<INPUT type = BUTTON class = "small_button" id = "button%d" name = "button%d" 
    #                      value = "+" onClick =  "JS('menu%d', 'button%d'); JS_check('span_checklayer%d');">
      lists = lists + """<img src = "/icons/plus.gif" class = "small_button" id = "button%d" name = "button%d" 
                          value = "+" onClick =  "JS('menu%d', 'button%d'); JS_check('span_checklayer%d');" />
                         <span class ="moves" onmousedown = "drag_object(event, this, 'lr_%d')"> 
                      """%(Nl, Nl, Nl, Nl, Nl, Nl)
    else:
      lists = lists + """
                         <span class ="moves" onmousedown="drag_object(event, this, 'lr_%d')"> 
                          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                      """%Nl
    
    if name:
      lists = lists + name
    else:
      lists = lists + title

    if req_sublayer:
      lists = lists + """</span></p><span id = "menu%d" style = "display: none;"><dl>"""%(Nl)
      lst_layer = lst_layer + """<span_check id = "span_checklayer%d" style = "display:none;"><dl>
                              """%Nl
    else:
      lists = lists + """</span></p>"""
#      lst_layer = lst_layer + "</p>"
    # If the layer belongs to a set that to mark it as selected

    # Sublayers Nl are recursively handled
    lists, lst_layer, i = get_layers(cur, Nset, Nwms, Nl, instr, lists, lst_layer, i)
    if req_sublayer:
      lists = lists + """</span></dd></dl>"""
      lst_layer = lst_layer + """</span_check></dd></dl>"""
    else:
      lists = lists + """</dd>"""
      lst_layer = lst_layer + """</dd>"""
  
  return lists, lst_layer, i

#
# get_listset: Displays a list of sets belonging to the user with a key "pkey". 
#              As an element is the "default" takes "filename".
def get_listset(cur, conn, pkey, filename):
  if not pkey:
    html_set = """<SELECT name = "setlists" id = "select_style" onChange = "this.form.submit();">
                  </SELECT>
               """
    return html_set
  html_set = """<SELECT name = setlists id = "select_style" onChange = "this.form.submit();">"""
  # Solicited names of all the sets of user "pkey"
  vals = {}
  tables = []
  vals["AuthorsSets.Nauthor"] = pkey
  vals["AuthorsSets.Nauthor"] = "WMSUsers.UID"
  tables.append("AuthorsSets.Nset")
  tables.append("AuthorsSets.Name")
  res = BD.ifsome_tables(cur, tables, vals, "AuthorsSets", "WMSUsers")

  name_f = "%s" % filename
  for Nset, name in res:
    if name == name_f:
      # As an element is the "default" takes "filename"
      html_set = html_set + """<OPTION selected value = %d id = "select_def"> %s """ % (Nset, name)
    else:
      html_set = html_set + """<OPTION value = %d> %s """ % (Nset, name)
  # Added output buttons
  html_set = html_set + """</SELECT>"""

  return html_set

#
# MenuResources: Forms the menu of the dropping out list of WMS resources existing 
#                in database and OK buttoms. Cur - cursor of database, wmslists - 
#                flag about taken WMS resource, Nwms - primary key taking WMS 
#                resource, filename - name file for saved XML. Return html list.

def MenuResources(cur, conn, wmslists, Nwms, pkey):
# % hcode.htext_resources() - create resources
  html = """<SELECT id = "select_style" name = "wmslists" 
                  onChange = "this.form.submit();">"""
# Get list of WMS resources from database
  result = BD.select_table(cur, "WMSresources", "Nwms", "Name", "Title", "author")
  for N, name, title, author in result:
    if author:
      continue
    if wmslists:
      if N == Nwms:
        html = html + """<OPTION selected  id = "select_def" value = %d>%s (%s) """ % (N, name, title)
      else:
        html = html + """<OPTION value = %d>%s (%s)""" % (N, name, title)
    else:
      html = html + """<OPTION value = %d>%s (%s)""" % (N, name, title)
    
  html = html + "</SELECT>"

  return html

#
# MenuLayers: Build Menu from layers for WMS resource Nwms.
#             Cur - cursor of database, Nset - set primary key defined user, 
#             Nwms - primary key WMS resources in BD, lists - html list.
#             Return html list.
def MenuLayers(cur, Nset, Nwms, lists):
  # Builds hierarchy of layers defined WMS a resource
  tablelist = """
                <TABLE id = "tabl5_t" border= "1" cellpadding = "0" cellspacing = "0">
                  <TR>
                    <form name = "myform3" action = "WM.cgi" method = "Get">
                      <TD style = "width: 98%%;">
                        %s
                      </TD>
                      <TD style = "width: 2%%;" align = "center">
                        %s
                        <INPUT type = hidden name = "layers_inset" value = "">
                      </TD>
                    </form>
                  </TR>
                </TABLE>
              """
  if not Nwms:
    lists = tablelist%("<dl></dl>", "<dl></dl>")
    return lists
  list_layer = "<dl>"
  lists = "<dl>"
  i = 0
  lists, list_layer, i = get_layers(cur, Nset, Nwms, -1, "Layer", lists, list_layer, i)
  lists = lists + "</dl>"
  list_layer = list_layer + "</dl>"
  lists = tablelist%(lists, list_layer)
  return lists

#
# list_Set: Add to the list of layers "set_layers" a given set of layer "Nlayer"
#           with value "nameid+Nlayer". If the layer is unavailable (not WMS), 
#           it displayed style "errdisable".
def list_Set(cur, Nlayer, nameid, set_layers):
  # Request parameters layer "Nlayer".
  values = {}
  values["Nlayer"] = Nlayer
  res = BD.ifselect_table(cur, "KnownLayers", "Nlayer", values, "Name", "Title",\
            "access_mode")

  for Nl, name, title, access in res:
    if name :
      strhelp = name
    else:
      strhelp = title
    nameid_t = nameid + "_%s"%Nl
    # Contains the name of the layer
    if name:
    #hcode.hcheckbox()%("subSet", nameid_t, "id = %s"%nameid_t),
      # If the layer is unavailable (not WMS)
      if access == "notWMS":
      #errdisable"
        set_layers = set_layers + """
                                     %s</p>
                                  """ % (name)
      else:
      #hcode.hcheckbox()%("subSet", nameid_t, "id = %s"%nameid_t),
        set_layers = set_layers + """
                                    %s</p>
                                  """ % (name)
    else:
      if access == "notWMS":
      #hcode.hcheckbox()%("subSet", nameid_t, "id = %s"%nameid_t),
        set_layers = set_layers + """
                                      %s</p>
                                  """ % (title)
      else:
      #hcode.hcheckbox()%("subSet", nameid_t, "id = %s"%nameid_t),
        set_layers = set_layers + """
                                      %s</p>
                                  """ % (title)
  return set_layers, strhelp

#
# get_sublayer: Adds in "set_layers" a sub-list layers belonging to the set. Nested
#               layers gets parsing "sub_group".
def get_sublayer(cur, Nl_group, set_layers, set_checkdel, set_checkincl, nameid, sub_group, evens, layer_noset):
  # "sub_group" divided into separate list of layers
  lstsub = sub_group.split(";")
  length = len(lstsub)
  join_layernoset = ""
  if layer_noset:
    join_layernoset = ";".join(layer_noset)
  for i in range(0, length-1):
    image = "checked1.gif"
    img_value = "0"
    # If the layer doesn't contain sublayers
    if lstsub[i].find(",") == -1:
      # Add to the list of layers "set_layers" a given set of layer "lstsub[i]"
      nameid_tmp = "%s_%s"%(nameid, lstsub[i].strip())
      if layer_noset:
        if (nameid_tmp in layer_noset):
          image = "empty_check4.gif"
          img_value = "1"
          style = "style = \"color: #8B8682;\""
        else:
          image = "checked1.gif"
          img_value = "0"
          style = "style = \"color: #000000;\""
      else:
        image = "checked1.gif"
        img_value = "0"
        style = "style = \"color: #000000;\""
      str_disab = ""
      lst_nameid = nameid_tmp.split('_')
      len_lst = len(lst_nameid)
      if (len_lst > 2):
        str_tmp = lst_nameid[0] + '_' + lst_nameid[1]
        #print join_layernoset, str_tmp
        if (join_layernoset.find(str_tmp + ';') != -1):
          str_disab = "disabled = 1"#disabled
        else:
          try:
            kpos = layer_noset.index(nameid_tmp)
          except:
            kpos = 0
          if kpos != 0:
            prev_nameid = layer_noset[kpos-1]
            if ((prev_nameid.find(lst_nameid[0] + '_') != -1) and (prev_nameid.find('_%s'%lst_nameid[1]) != -1)):
              str_disab = "disabled = 1"
      if (len_lst == 2):
        #print join_layernoset, lst_nameid[0]
        fl = join_layernoset.find(lst_nameid[0]+';')
        if((fl != -1) and (fl == 0)):
          str_disab = "disabled = 1"
        else:
          fl = join_layernoset.find(";%s;"%lst_nameid[0])
          if(fl != -1):
            str_disab = "disabled = 1"
      if evens%2 == 0:
        class_style = "class = \"dd_even\""
      else:
        class_style = "class = \"dd_odd\""
      
      evens += 1
      #style = "height: 19,9px;" 
      set_layers = set_layers + """<dd id = "ddsetsub%s">
                                    <p id = "setsub_%s" %s %s>
                                      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                """%(nameid_tmp, nameid_tmp, class_style, style)

      set_layers, strhelp = list_Set(cur, lstsub[i], nameid, set_layers)
      set_layers = set_layers + "</p></dd>"

      set_checkdel = set_checkdel + """<dd id = "checkdel%s" style = "margin: 0;">
                                        <a class = "tooltip" href = "#">
                                          <p style = "height: 19px;" %s>
                                            <img src = "/icons/stress1.png" name = "subSet" class = "smallcheck_r"
                                              id = "subSet%s" value = "0" onClick = "click_delete(this.id);"/>
                                           </p>
                                          <spany id = "spany%s" class = "classic">%s</spany>
                                        </a>
                                      </dd>
                                    """%(nameid_tmp, class_style, nameid_tmp, nameid_tmp, strhelp)
      set_checkincl = set_checkincl + """<dd id = "checkincl%s" style = "margin: 0;">
                                          <a class = "tooltip" href = "#">
                                            <p style = "height: 19px;" %s>
                                              <input type=hidden id = "subSet%si" value = "%s" %s>
                                              <img src = "/icons/%s" name = "subSet" class = "smallcheck_r"
                                                id = "subSet%si" %s
                                               onClick = "click_incl(this.id, this);" />
                                            </p>
                                            <spany class = "classic">%s</spany>
                                          </a>
                                      </dd>
                                    """%(nameid_tmp, class_style, nameid_tmp, img_value, str_disab, \
                                          image, nameid_tmp, str_disab, strhelp)
      # Close list
    else:
      # Splitting a string into a list of sublayers
      lst1sub = lstsub[i].split(",")
      lens = len(lst1sub)
      k = []
      for j in range(0, lens):
        # If the sublayer contains no other sub-layer
        if lst1sub[j].find("=") == -1:
          nameid_tmp = "%s_%s"%(nameid, lst1sub[j].strip())
#          print nameid_tmp
          if layer_noset:
            if (nameid_tmp in layer_noset):
              image = "empty_check4.gif"
              img_value = "1"
              style = "style = \"color: #8B8682;\""
            else:
              image = "checked1.gif"
              img_value = "0"
              style = "style = \"color: #000000;\""
          else:
            image = "checked1.gif"
            img_value = "0"
            style = "style = \"color: #000000;\""
          str_disab = ""
          lst_nameid = nameid_tmp.split('_')
          len_lst = len(lst_nameid)
          if (len_lst > 2):
            str_tmp = lst_nameid[0] + '_' + lst_nameid[1]
            #print join_layernoset, str_tmp
            if (join_layernoset.find(str_tmp + ';') != -1):
              str_disab = "disabled = 1"#disabled
            else:
              try:
                kpos = layer_noset.index(nameid_tmp)
              except:
                kpos = 0
              if kpos != 0:
                prev_nameid = layer_noset[kpos-1]
                if ((prev_nameid.find(lst_nameid[0] + '_') != -1) and (prev_nameid.find('_%s'%lst_nameid[1]) != -1)):
                  str_disab = "disabled = 1"
          if (len_lst == 2):
            #print join_layernoset, lst_nameid[0]
            fl = join_layernoset.find(lst_nameid[0]+';')
            if((fl != -1) and (fl == 0)):
              str_disab = "disabled = 1"
            else:
              fl = join_layernoset.find(";%s;"%lst_nameid[0])
              if(fl != -1):
                str_disab = "disabled = 1"
                if(join_layernoset.find(lst_nameid[0]+';') != -1):
                  str_disab = "disabled = 1"
          if evens%2 == 0:
            class_style = "class = \"dd_even\""
          else:
            class_style = "class = \"dd_odd\""
          evens += 1
          #style = "height: 19,9px;" 
          set_layers = set_layers + """<dd id = "ddsetsub%s">
                                        <p id = "setsub_%s" %s %s>
                                        <img src = "/icons/plus.gif" name = "butt%s" 
                                          id = "butt%s" value = "+" class = "small_button"
                                          onClick = "JS('menuset%s', 'butt%s');
                                          JS_check('span_checkdel%s');
                                          JS_check('span_checkincl%s');" />
                                    """%(nameid_tmp,\
                                         nameid_tmp, class_style, style, nameid_tmp,\
                                         nameid_tmp,\
                                         nameid_tmp, nameid_tmp, nameid_tmp,\
                                         nameid_tmp\
                                        )
          set_checkdel = set_checkdel + """<dd id = "checkdel%s" style = "margin: 0;">
                                            <a class = "tooltip" href = "#">
                                              <p style = "height: 19px;" %s>
                                                <img src = "/icons/stress1.png" name = "subSet" class = "smallcheck_r"
                                                 id = "subSet%s" value = "0" onClick = "click_delete(this.id);" />
                                              </p>
                                        """%(nameid_tmp, class_style, nameid_tmp)
          set_checkincl = set_checkincl + """<dd id = "checkincl%s" style = "margin: 0;">
                                              <a class = "tooltip" href = "#">
                                                <p style = "height: 19px;" %s>
                                                  <input type=hidden id = "subSet%si" value = "%s" %s>
                                                  <img src = "/icons/%s" name = "subSet" class = "smallcheck_r"
                                                    id = "subSet%si" %s
                                                   onClick = "click_incl(this.id, this);" />
                                                </p>
                                        """%(nameid_tmp, class_style, nameid_tmp, img_value, str_disab, \
                                              image, nameid_tmp, str_disab)

          set_layers, strhelp = list_Set(cur, lst1sub[j], nameid, set_layers)
          
          set_checkdel = set_checkdel + """<spany id = "spany%s" class = "classic">%s</spany>
                                            </a>
                                        """%(nameid_tmp, strhelp)
          set_checkincl = set_checkincl + """<spany class = "classic">%s</spany>
                                            </a>
                                        """%strhelp
          set_layers = set_layers + """<span id = "menuset%s" style = "display: none;">
                                        <dl>
                                    """%(nameid_tmp)
          set_checkdel = set_checkdel + """<span_check id = "span_checkdel%s" style = "display: none;">
                                            <dl>
                                        """%(nameid_tmp)
          set_checkincl = set_checkincl + """<span_check id = "span_checkincl%s" style = "display: none;">
                                            <dl>
                                        """%(nameid_tmp)
#                                    """%nameid + "_%s"%lst1sub[j]
          # Add to the list of nested layer
          k.append(lst1sub[j])
        else:
          # equal[0] is a layer in which there is a layer equal[1]
          equal = lst1sub[j].split("=") 
          # Search the layer which owns equal[1]
          mmm = len(k)
          while (mmm > 0):
            if (k[mmm-1].strip() == equal[0].strip()):
              break
            # Close previous lists
            set_layers = set_layers + "</span></dl>"
            set_checkdel = set_checkdel + """</span_check></dl>"""
            set_checkincl = set_checkincl + """</span_check></dl>"""
            del k[mmm-1]
            mmm = mmm - 1
          nameid_t = "%s_%s"%(nameid, equal[0].strip())
#          set_layers = set_layers + """<span id = "menuset%s" style = "display: block;">
#                                    """%nameid_t
          tmp = lstsub[i].find(lst1sub[j], 0)
          tmp_t = lstsub[i].find(",", tmp + 1)
          tmp2 = lstsub[i].find("= %s"%equal[1], tmp_t)
          tmp3 = lstsub[i].find("%s ="%equal[1], tmp_t)
          nameid_tmp = "%s_%s"%(nameid_t, equal[1].strip())
#          print nameid_tmp, "eq%s"%equal[1], nameid_t
          if layer_noset:
            if (nameid_tmp in layer_noset):
              image = "empty_check4.gif"
              img_value = "1"
              style = "style = \"color: #8B8682;\""
            else:
              image = "checked1.gif"
              img_value = "0"
              style = "style = \"color: #000000;\""
          else:
            image = "checked1.gif"
            img_value = "0"
            style = "style = \"color: #000000;\""
          str_disab = ""
          lst_nameid = nameid_tmp.split('_')
          len_lst = len(lst_nameid)
          if (len_lst > 2):
            str_tmp = lst_nameid[0] + '_' + lst_nameid[1]
            #print join_layernoset, str_tmp
            if (join_layernoset.find(str_tmp + ';') != -1):
              str_disab = "disabled = 1"#disabled
            else:
              try:
                kpos = layer_noset.index(nameid_tmp)
              except:
                kpos = 0
              if kpos != 0:
                prev_nameid = layer_noset[kpos-1]
                if ((prev_nameid.find(lst_nameid[0] + '_') != -1) and (prev_nameid.find('_%s'%lst_nameid[1]) != -1)):
                  str_disab = "disabled = 1"
          if (len_lst == 2):
            #print join_layernoset, lst_nameid[0]
            fl = join_layernoset.find(lst_nameid[0]+';')
            if((fl != -1) and (fl == 0)):
              str_disab = "disabled = 1"
            else:
              fl = join_layernoset.find(";%s;"%lst_nameid[0])
              if(fl != -1):
                str_disab = "disabled = 1"
          if evens%2 == 0:
            class_style = "class = \"dd_even\""
          else:
            class_style = "class = \"dd_odd\""
          evens += 1
          if ((tmp2 != -1) and (tmp2 > tmp3)) or ((tmp2 == -1) and (tmp3 != -1)):
          # style = "height: 19,9px;"
            set_layers = set_layers + """<dd id = "ddsetsub%s">
                                          <p id = "setsub_%s" %s %s>
                                            <img src = "/icons/plus.gif" name = "butt%s" 
                                              id = "butt%s" value = "+" class = "small_button"
                                              onClick = "JS('menuset%s', 'butt%s');
                                              JS_check('span_checkdel%s');
                                              JS_check('span_checkincl%s');" />
                         """%(nameid_tmp,\
                              nameid_tmp, class_style, style, nameid_tmp,\
                              nameid_tmp,\
                              nameid_tmp, nameid_tmp, nameid_tmp, \
                              nameid_tmp\
                             )
            set_checkdel = set_checkdel + """<dd id = "checkdel%s" style = "margin: 0;">
                                              <a class = "tooltip" href = "#">
                                                <p style = "height: 19px;" %s>
                                                  <img src = "/icons/stress1.png" name = "subSet" class = "smallcheck_r"
                                                   id = "subSet%s" value = "0" onClick = "click_delete(this.id);" />
                                                </p>
                                          """%(nameid_tmp, class_style, nameid_tmp)
            set_checkincl = set_checkincl + """<dd id = "checkincl%s" style = "margin: 0;">
                                                <a class = "tooltip" href = "#">
                                                  <p style = "height: 19px;" %s>
                                                    <input type=hidden id = "subSet%si" value = "%s" %s>
                                                    <img src = "/icons/%s" name = "subSet" class = "smallcheck_r"
                                                      id = "subSet%si" %s
                                                     onClick = "click_incl(this.id, this);" />
                                                  </p>
                                          """%(nameid_tmp, class_style, nameid_tmp, img_value, str_disab, \
                                                image, nameid_tmp, str_disab)
          else:
          #style= "height:19,9px;" 
            set_layers = set_layers + """<dd id = "ddsetsub%s">
                                          <p id = "setsub_%s" %s %s>
                                            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                      """%(nameid_tmp, nameid_tmp, class_style, style)
            set_checkdel = set_checkdel + """<dd id = "checkdel%s" style = "margin: 0;">
                                              <a class = "tooltip" href = "#">
                                                <p style = "height: 19px;" %s>
                                                  <img src = "/icons/stress1.png" name = "subSet" class = "smallcheck_r"
                                                    id = "subSet%s" value = "0" onClick = "click_delete(this.id);" />
                                                </p>
                                          """%(nameid_tmp, class_style, nameid_tmp)
            set_checkincl = set_checkincl + """<dd id = "checkincl%s" style = "margin: 0;">
                                                <a class = "tooltip" href = "#">
                                                  <p style = "height: 19px;" %s>
                                                    <input type=hidden id = "subSet%si" value = "%s" %s>
                                                    <img src = "/icons/%s" name = "subSet" class = "smallcheck_r"
                                                      id = "subSet%si" %s
                                                      onClick = "click_incl(this.id, this);" />
                                                  </p>
                                          """%(nameid_tmp, class_style, nameid_tmp, img_value, str_disab, \
                                                image, nameid_tmp, str_disab)
          set_layers, strhelp = list_Set(cur, equal[1], nameid_t, set_layers)
          
          set_checkdel = set_checkdel + """<spany id = "spany%s" class = "classic">%s</spany>
                                            </a>
                                        """%(nameid_tmp, strhelp)
          set_checkincl = set_checkincl + """<spany class = "classic">%s</spany>
                                            </a>
                                        """%strhelp
          
          if ((tmp2 != -1) and (tmp2 > tmp3)) or ((tmp2 == -1) and (tmp3 != -1)):
            set_layers = set_layers + """<span id = "menuset%s" style = "display: none;">
                                         <dl>
                                      """%(nameid_tmp)
            set_checkdel = set_checkdel + """<span_check id = "span_checkdel%s"  style = "display: none;">
                                              <dl>
                                          """%(nameid_tmp)
            set_checkincl = set_checkincl + """<span_check id = "span_checkincl%s"  style = "display: none;">
                                              <dl>
                                          """%(nameid_tmp)
            k.append(equal[1])
          else:
            set_layers = set_layers + "</dd>"
            set_checkdel = set_checkdel + """</dd>"""
            set_checkincl = set_checkincl + """</dd>"""
#          set_layers = set_layers + """<span id = "menuset%s" style = "display: none;">
#                                    """%nameid_t + "_%s"%equal[1]

      # Close  all lists
      mmm = len(k)
      while mmm > 0:
        set_layers = set_layers + "</span></dl>"
        set_checkdel = set_checkdel + """</span_check></dl>"""
        set_checkincl = set_checkincl + """</span_check></dl>"""
      #  set_layers = set_layers + "</ul>"
        mmm = mmm - 1
  return set_layers, set_checkdel, set_checkincl, evens
  
#
# MenuSet: Forms the menu of the list of layers added by the user in a set 
#          nameset. Cur and conn - cursor of database, nameset - name set 
#          defined user, set_layers - html list. Return html list.
def MenuSet(cur, conn, nameset, Nset):
  set_layers = ""
  set_checkdel = ""
  set_checkincl = ""
  listSet = {}
  # If not name set that return NULL list
  if not nameset:
    set_layers = "<dl><dd></dd></dl>"
    set_checkdel = "<dl><dd></dd></dl>"
    set_checkincl = "<dl><dd></dd></dl>"
    return set_layers, set_checkdel, set_checkincl 
  # Get list of layers added by the users in a set

  if not Nset:
    vals = {}
    vals["Name"] = "\'%s\'"%nameset
    res = BD.ifselect_table(cur, "AuthorsSets", "Nset", vals, "layer_noset")
    for Nl, lst_noset in res:
      Nset = Nl
      layer_noset = lst_noset
  else:
    vals = {}
    vals["Nset"] = "\'%d\'"%Nset
    res = BD.ifselect_table(cur, "AuthorsSets", "Nset", vals, "layer_noset")
    #print res
    for Nl, lst_noset in res:
      layer_noset = lst_noset
  if layer_noset:
    layer_noset = layer_noset.split(";")
    #print layer_noset
    if ("" in layer_noset):
      layer_noset.remove("")
    #print layer_noset
  
  vals = {}
  tables = []
  vals["SetLayer.Nlayer"] = "KnownLayers.Nlayer"
  vals["KnownLayers.Nwms"] = "WMSresources.Nwms"
  for Nl, title in res:
    vals["Nset"] = Nset
  tables.append("KnownLayers.Nlayer")
  tables.append("KnownLayers.Name")
  tables.append("KnownLayers.Title")
  tables.append("KnownLayers.access_mode")
  tables.append("WMSresources.Nwms")
  tables.append("WMSresources.Name")
  tables.append("SetLayer.sub_group")
  res = BD.ifsome_tables(cur, tables, vals, "SetLayer", "KnownLayers", "WMSresources")
  # Froms the list of layers, all to mark as selected
  evens = 0
  for Nl, name, title, access, Nwms, wmsname, sub_group in res:
    image = "checked1.gif"
    img_value = "0"
    if layer_noset:
      #print "layer_noset", Nl
      #print (Nl in layer_noset)
      #print "xe"
      strs = "%d"%Nl
      if (strs in layer_noset):
        image = "empty_check4.gif"
        img_value = "1"
        style = "style = \"color: #8B8682;\""
      else:
        image = "checked1.gif"
        img_value = "0"
        style = "style = \"color: #000000;\""
    else:
      image = "checked1.gif"
      img_value = "0"
      style = "style = \"color: #000000;\""
    #print "image"
    if name:
      strhelp = name;
    else:
      strhelp = title;
    if evens%2 == 0:
      class_style = "class = \"dd_even\""
    else:
      class_style = "class = \"dd_odd\""
    if sub_group:
    #style = "height: 19,9 px;" 
      set_layers = set_layers + """<dl><dd id = "ddset%d">
                                    <p id = "set_%d" %s %s>
                                      <img src = "/icons/plus.gif" name = "butt%d" 
                                        id = "butt%d" value = "+" class = "small_button"
                                        onClick = "JS('menuset%d', 'butt%d');
                                        JS_check('span_checkdel%d');
                                        JS_check('span_checkincl%d');" />
                                """%(Nl, Nl, class_style, style, Nl, Nl, Nl, Nl, Nl, Nl)
                      #empty_check4.gif
      set_checkdel = set_checkdel + """<dl>
                                        <dd id = "checkdel%d" style = "margin: 0;">
                                          <a class = "tooltip" href = "#">
                                            <p style = "height: 19px;" %s>
                                              <img src = "/icons/stress1.png" name = "Set" class = "smallcheck_r"
                                               id = "Set%d" value = "0" onClick = "click_delete(this.id);" />
                                            </p>
                                            <spany id = "spany%d" class = "classic">%s</spany>
                                          </a>
                                          <span_check id = "span_checkdel%d" style = "display: none;">
                                            <dl style = "margin-left: 0; margin-right: 0;">
                                    """%(Nl, class_style, Nl, Nl, strhelp, Nl)
      set_checkincl =  set_checkincl + """<dl>
                                        <dd id = "checkincl%d" style = "margin: 0;">
                                          <a class = "tooltip" href = "#">
                                            <p style = "height: 19px;" %s>
                                              <input type=hidden id = "Set%di" value = "%s">
                                              <img src = "/icons/%s" name = "Set" class = "smallcheck_r"
                                              id = "Set%di"
                                               onClick = "click_incl(this.id, this);" />
                                            </p>
                                            <spany class = "classic">%s</spany>
                                          </a>
                                          <span_check id = "span_checkincl%d" style = "display: none;">
                                            <dl style = "margin-left: 0; margin-right: 0;">
                                    """%(Nl, class_style, Nl, img_value, image, Nl, strhelp, Nl)
    else:
    # style = "height: 19,9px;"
      set_layers = set_layers + """<dl>
                                    <dd id = "ddset%d">
                                      <p id = "set_%d" %s %s>
                                        &nbsp;&nbsp;&nbsp;&nbsp;
                                """%(Nl, Nl, class_style, style)
      set_checkdel = set_checkdel + """<dl>
                                          <dd id = "checkdel%d" style = "margin: 0;">
                                            <a class = "tooltip" href = "#">
                                              <p style = "height: 19px;" %s>
                                                <img src = "/icons/stress1.png" name = "Set" class = "smallcheck_r"
                                                 id = "Set%d" value = "0" onClick = "click_delete(this.id);" />
                                              </p>
                                              <spany id = "spany%d" class = "classic">%s</spany>
                                          </a>
                                    """%(Nl, class_style, Nl, Nl, strhelp)
      set_checkincl =  set_checkincl + """<dl>
                                          <dd id = "checkincl%d" style = "margin: 0;">
                                            <a class = "tooltip" href = "#">
                                              <p style = "height: 19px;" %s>
                                                <input type=hidden id = "Set%di" value = "%s">
                                                <img src = "/icons/%s" name = "Set" class = "smallcheck_r"
                                                 id = "Set%di"
                                                 onClick = "click_incl(this.id, this);" />
                                              </p>
                                              <spany class = "classic">%s</spany>
                                          </a>
                                    """%(Nl, class_style, Nl, img_value, image, Nl, strhelp)
    evens += 1
    if name:
      if access == "notWMS":
      #hcode.hcheckbox()%("Set", "%d"%Nl, "id = %d"%Nl),class="errdisable"
        set_layers = set_layers + """
                                    %s</p>
                                  """ % (name)
      else:
      #hcode.hcheckbox()%("Set", "%d"%Nl, "id = %d"%Nl), 
        listSet[Nl] = Nwms
        set_layers = set_layers + """
                                     %s</p>
                                  """ % (name)
    else:
      if access == "notWMS": 
      #hcode.hcheckbox()%("Set", "%d"%Nl, "id = %d"%Nl), 
        set_layers = set_layers + """
                                      %s</p>
                                  """ % (title)
      else:
      #hcode.hcheckbox()%("Set", "%d"%Nl, "id = %d"%Nl), wmsname
        listSet[Nl] = Nwms
        set_layers = set_layers + """
                                      %s</p>
                                  """ % (title)
    if sub_group and (sub_group != ""):
#      print "sub_group%dNl "%Nl, sub_group
      set_layers = set_layers + """<span id = "menuset%d" style = "display: none;"><dl>
                                """%Nl
    #print "get_sublayer"
    set_layers, set_checkdel, set_checkincl, evens = get_sublayer(cur, Nl, set_layers,\
                                                                 set_checkdel, set_checkincl,\
                                                                 "%d"%Nl, sub_group, evens,\
                                                                  layer_noset)
    if sub_group:
      set_layers = set_layers + "</span></dl></dd></dl>"
      set_checkdel = set_checkdel + """</span_check></dl></dd></dl>"""
      set_checkincl =  set_checkincl + """</span_check></dl></dd></dl>"""
    else:
      set_layers = set_layers + "</dd></dl>"
      set_checkdel = set_checkdel + """</dd></dl>"""
      set_checkincl =  set_checkincl + """</dd></dl>"""
  if not res:
    set_layers = "<dl><dd></dd></dl>"
    set_checkdel = "<dl><dd></dd></dl>"
    set_checkincl = "<dl><dd></dd></dl>"

  return set_layers, set_checkdel, set_checkincl

#
# get_newlayers: Displays a list the layer groups have creates a user "pkey" and
#                menus to control them.
def get_newlayers(cur, conn, Nwms, oldNwms, Nl_def, pkey, namefile):
  if pkey == 0:
    html = """<SELECT id = "select_style" name = "newgroup" onChange = "this.form.submit();>
              </SELECT>
           """
    return html
  html = """<SELECT id = "select_style" name="newgroup" onChange = "this.form.submit();">
         """
  
  Nwm = 0
  if Nwms == 0:
    tables = []
    tables.append("Nwms")
    value = {}
    value["author"] = "\'%d\'"%pkey
    Nwm = BD.ifsome_tables(cur, tables, value, "WMSresources")
  if Nwm:
    Nwms = Nwm[0][0]
  if Nwms:
    tables = []
    tables.append("Nlayer")
    tables.append("Name")
    tables.append("Title")
    value = {}
    value["Nwms"] = "%s"%Nwms
    res = BD.ifsome_tables(cur, tables, value, "KnownLayers")
    if Nl_def:
      Nl_def = int(Nl_def)

    for Nl, name, title in res:
      if (Nl == Nl_def):
        html = html + """<OPTION selected id = "select_def" value = %d>%s(%s)
                    """ % (Nl, name, title)
      else:
        html = html + """<OPTION value = %d>%s(%s)
                      """ % (Nl, name, title)
  html = html + """ </SELECT>"""

  return html

#
# get_SLD: Displays a list of added style SLD in set "ppkey" and menus to 
#          control them.
def get_SLD(cur, conn, ppkey, default):
  listSLD = """<SELECT id = "select_style" name="SLD" 
                onChange = "this.form.submit();">
            """
  if not ppkey:
    listSLD = listSLD + """</SELECT>"""
    return listSLD
  val = {}
  val["SLDset.Nset"] = "%s"%ppkey
  val["SLDset.Nsld"] = "SLD.Nsld"
  tables = []
  tables.append("SLD.name")
  tables.append("SLD.Nsld")
  res = BD.ifsome_tables(cur, tables, val, "SLDset", "SLD")
  if res:
    if default:
      Nsld_def = int(default)
    else:
      Nsld_def = 0
    for name, Nsld in res:
      if Nsld == Nsld_def:
        listSLD = listSLD + """<OPTION selected id = "select_def" value = %d> %s """ % (Nsld, name)
      else:
        listSLD = listSLD + """<OPTION value = %d> %s """ % (Nsld, name)
  listSLD = listSLD + """</SELECT>"""

  return listSLD
