#
# html_code.py:

#
# hlist_newSLD: 
def hlist_newSLD():
  html = """<HTML>
              <HEAD>
                <TITLE>Control system WMS resources</TITLE>
                <meta http-equiv="Content-Type" content="text/html" charset="utf-8" />
                <script language="javascript">
                function local_fl(namecheck, nametext, othercheck) {
                  if (document.getElementById(namecheck).checked){
                    document.getElementById(nametext).disabled=false;
                    document.getElementById(othercheck).disabled=true;
                  }else{
                    document.getElementById(nametext).disabled=true;
                    document.getElementById(othercheck).disabled=false;
                  }
                }
                </script>
              </HEAD>
              <BODY>
                <H1>Get SLD in set</H1>
                <TABLE>
                <form enctype = "multipart/form-data" action = "WM.cgi" method = "POST">
                  <TR><TD>
                        <INPUT type=checkbox name="fileSLD" id ="flSLD" onclick="local_fl('flSLD', 'filelocal', 'http')">
                        Loading of the a file from the local computer
                      </TD>
                  </TR>
                  <TR><TD>
                        <INPUT disabled TYPE="file" name="file_local" id="filelocal">
                      </TD>
                  </TR>
                  <TR><TD><INPUT type=checkbox name="httpSLD" id="http" onclick="local_fl('http', 'filehttp', 'flSLD')">
                        Loading of the a file from the Internet
                      </TD>
                  </TR>
                  <TR><TD>
                        <INPUT disabled TYPE=text name="file_http" id = "filehttp" size = 20 maxlen = 20>
                      </TD>
                  </TR>
                  <TR>
                      <TD>
                        <INPUT TYPE=hidden name="filename" value = %s>
                        <INPUT TYPE=hidden name="wmslists" value = %s>
                        <INPUT TYPE=hidden name="newgroup" value = %s>
                      </TD>
                  </TR>
                  <TR><TD>
                        <INPUT TYPE=SUBMIT value = "Ok" name="OK_SLD">
                      </TD>
                  </TR>
                </form>
                </TABLE>
              </BODY>
            </HTML>
          """
  return html


#print "Content-type: text/html; charset = utf-8\n"


#
# hmain_list:
def hmain_list():
#
  html = """
        <HTML>
          <HEAD>
            <TITLE>
              WMS-layers managment system
            </TITLE>
            <meta http-equiv="Content-Type" content="text/html"; charset="utf-8" />
            <script type="text/javascript">
              var namelayer = "";
              var strCookie = "";
              var elem_prev = 0;
              var prev_color = "#000000";
              var list_click = "";
              alert("open");
              function test(id) {
                alert(id.options[id.selectedIndex].value);
              }
              function getrequest(forma) {
                var src = window.prompt("Get URL new resource:");
                if (src){
                  forma.elements["resources"].value = src;
                  setCookie("display", strCookie);
                  forma.submit();
                }
              }
              function getset(forma) {
                var src = window.prompt("Get name new set:");
                if (src){
                  forma.elements["filename"].value = src;
                  setCookie("display", strCookie);
                  forma.submit();
                }
              }
              function edit_nameset(forma) {
                old_name = forma.elements["oldname"].value;
                if (old_name != ""){
                  var src = window.prompt("Get new name set:", old_name);
                  if (src != ""){
                    forma.elements["editname"].value = src;
                    setCookie("display", strCookie);
                    forma.submit();
                  }
                }
              }
              function save_public(forma) {
                mess = forma.elements["message"].value;
                if (mess) {
                  alert(mess);
                }
              }
              function Delete_Set(forma) {
                //alert("DeleteSet");
                nameset = forma.elements["oldname"].value;
                if (nameset != ""){
                  query = "Are you sure you want to delete a set of \'"+ nameset+"\'?";
                  var src = window.confirm(query);
                  if (src){
                    forma.submit();
                  }
                  else{
                    forma.elements["DeleteSet"].value = "";
                    forma.submit();
                  }
                }
              }
              function drag_object(evt, obj1, layerId){
                //alert("drag");
                lrst = layerId.indexOf("lr_");
                lrend = layerId.length;
                namelayer = layerId.substring(lrst + 3, lrend);
                elemtabl = document.getElementById('tabl6_col1');
                pos = positon_tab(elemtabl);
                evt = evt || window.event;
                obj1.mousePosX = evt.pageX || evt.x;//evt.clientX;
                obj1.mousePosY = evt.pageY || evt.y;//evt.clientY;
                if (obj1.mousePosX == null) {
                  d = (document.documentElement && document.documentElement.scrollLeft != null)?document.documentElement:document.body;
                  obj1.mousePosX = evt.clientX + d.scrollLeft;
                  obj1.mousePosY = evt.clientY + d.scrollTop;
                }
                if ((obj1.mousePosX < pos.x) || (obj1.mousePosX > (pos.x + pos.width)) || (obj1.mousePosY < pos.y) || (obj1.mousePosY > (pos.y + pos.height))){
                  obj = clone(obj1);
                  obj.style.left = obj1.mousePosX;
                  obj.style.top = obj1.mousePosY + 4;
                  obj.style.position = 'absolute';
                  obj.style.cursor = 'pointer';
                  document.body.appendChild(obj);
                  obj.clicked = true;
                  if( evt.preventDefault ) evt.preventDefault();
                  else evt.returnValue = false;
                }
                document.onmouseup = function(evt){ 
                  elemtabl = document.getElementById('tabl6_col1');
                  pos = positon_tab(elemtabl);
                  mousePosX = evt.pageX || evt.x;
                  mousePosY = evt.pageY || evt.y;
                  if (mousePosX == null) {
                    d = (document.documentElement && document.documentElement.scrollLeft != null)?document.documentElement:document.body;
                    mousePosX = evt.clientX + d.scrollLeft;
                    mousePosY = evt.clientY + d.scrollTop;
                  }
                  if (elem_prev) {
                    elem_prev.style.color = prev_color;//"#000000";
                    elem_prev.style.cursor = "pointer";
                    elem_prev = 0;
                    prev_color = "#000000";
                  }
                  document.getElementById("tabl6_col1").style.cursor = 'pointer';
                  document.getElementById("tdcaption_set").style.cursor = 'pointer';
                  if ((mousePosX < pos.x) || (mousePosX > (pos.x + pos.width)) || (mousePosY < pos.y) || (mousePosY > (pos.y + pos.height))){
                    //alert("not td1 in table!!");
                    tablhead = document.getElementById('tdcaption_set');
                    pos_head = positon_tab(tablhead);
                    if ((mousePosX > pos_head.x) && (mousePosX < (pos_head.x + pos_head.width)) && (mousePosY > pos_head.y) && (mousePosY < (pos_head.y + pos_head.height))){
                      obj.clicked = false;
                      obj.parentNode.removeChild(obj);
                      document.forms["myform1"].Layer.value = namelayer;
                      namelayer = "";
                      setCookie("display", strCookie);
                      document.forms["myform1"].submit();
                    }
                    else{
                      obj.clicked = false;
                      obj.parentNode.removeChild(obj);
                      namelayer = "";
                    }
                  } 
                  else {
                    //arrayelem = elemtabl.childNodes;children
                    //alert(namelayer);
                    obj.clicked = false;
                    obj.parentNode.removeChild(obj);
                    elem = document.elementFromPoint(mousePosX, mousePosY);
                    //alert(elem.id);
                    if (elem && elem.id) {
                      //alert(elem.id);
                      setst = elem.id.indexOf("set_");
                      setend = elem.id.length;
                      if (setst != -1) {
                        var str = elem.id.substring(setst + 4, setend);
                        //alert(str);
                        document.forms["myform1"].Layer.value = namelayer;
                        document.forms["myform1"].Set.value = str;
                        namelayer = "";
                        setCookie("display", strCookie);
                        document.forms["myform1"].submit();
                      }
                      setst = elem.id.indexOf("ddset");
                      if (setst != -1) {
                        var str = elem.id.substring(setst + 5, setend);
                        //alert(str);
                        document.forms["myform1"].Layer.value = namelayer;
                        document.forms["myform1"].Set.value = str;
                        namelayer = "";
                        setCookie("display", strCookie);
                        document.forms["myform1"].submit();
                      }
                      setst = elem.id.indexOf("setsub_");
                      if (setst != -1) {
                        var str = elem.id.substring(setst + 7, setend);
                        document.forms["myform1"].Layer.value = namelayer;
                        document.forms["myform1"].subSet.value = str;
                        namelayer = "";
                        setCookie("display", strCookie);
                        document.forms["myform1"].submit();
                      }
                      setst = elem.id.indexOf("ddsetsub");
                      if (setst != -1) {
                        var str = elem.id.substring(setst + 8, setend);
                        document.forms["myform1"].Layer.value = namelayer;
                        document.forms["myform1"].subSet.value = str;
                        namelayer = "";
                        setCookie("display", strCookie);
                        document.forms["myform1"].submit();
                      }
                      if (elem.id.indexOf("tabl6_col1") != -1) {
                        document.forms["myform1"].Layer.value = namelayer;
                        namelayer = "";
                        setCookie("display", strCookie);
                        document.forms["myform1"].submit();
                      }
                    }  //obj.clicked = false;
                  }
                }
                document.onmousemove = function(evt) {
                  evt = evt || window.event;
                  if( obj.clicked ) {
                    posLeft = !obj.style.left ? obj.offsetLeft : parseInt( obj.style.left );
                    posTop = !obj.style.top ? obj.offsetTop : parseInt( obj.style.top );
                    mousePosX = evt.pageX || evt.x;
                    mousePosY = evt.pageY || evt.y;
                    if (mousePosX == null) {
                      d = (document.documentElement && document.documentElement.scrollLeft != null)?document.documentElement:document.body;
                      mousePosX = evt.clientX + d.scrollLeft;
                      mousePosY = evt.clientY + d.scrollTop;
                    }
                    elem = document.elementFromPoint(mousePosX, mousePosY);
                    obj.style.left = posLeft + mousePosX - obj.mousePosX + 'px';
                    obj.style.top = posTop + mousePosY - obj.mousePosY + 'px';
                    obj.mousePosX = mousePosX;
                    obj.mousePosY = mousePosY;
                    elemtabl = document.getElementById('tabl6_col1');
                    pos = positon_tab(elemtabl);
                    if ((mousePosX > pos.x) && (mousePosX < (pos.x + pos.width)) && (mousePosY > pos.y) && (mousePosY < (pos.y + pos.height))) {
                      obj.style.cursor = "crosshair";
                      if (elem_prev != 0) {
                        if (elem) {
                          if(elem != elem_prev) {
                            //alert(elem_prev.style.color);
                            elem_prev.style.color = prev_color;
                            elem_prev.style.cursor = "pointer";
                          }
                        }
                        else{
                          elem_prev.style.color = prev_color;
                          elem_prev.style.cursor = "pointer";
                        }
                      }
                      if (elem && elem.tagName != "undefined") {
                        <!--alert(elem.id);-->
                        if (elem != elem_prev)
                          elem_prev = 0;
                        if (((elem.id.indexOf("set_")!= -1) || (elem.id.indexOf("setsub_")!= -1)) && (elem != elem_prev)) {
                          prev_color = elem.style.color;
                          elem.style.color = "#87CEEB";
                          elem.style.cursor = "crosshair";
                          elem_prev = elem;
                        }
                        if((elem.id.indexOf("tabl6_col1")!= -1) && (elem != elem_prev)){
                          //alert("table head");
                          elems = document.getElementById("caption_set");
                          prev_color = elems.style.color;
                          elems.style.color = "#87CEEB";
                          elem.style.cursor = "crosshair";
                          elem_prev = elems;
                        }
                        if ((elem.id.indexOf("ddsetsub")!= -1) && (elem != elem_prev)) {
                          lens = elem.id.length;
                          pos = elem.id.indexOf("ddsetsub");
                          idelem = "setsub_" + elem.id.substring(pos+8, lens);
                          elems = document.getElementById(idelem);
                          prev_color = elems.style.color;
                          elems.style.color = "#87CEEB";
                          elems.style.cursor = "crosshair";
                          elem_prev = elems;
                        }
                        else{
                          if ((elem.id.indexOf("ddset")!= -1) && (elem != elem_prev)) {
                            lens = elem.id.length;
                            pos = elem.id.indexOf("ddset");
                            idelem = "set_" + elem.id.substring(pos+5, lens);
                            elems = document.getElementById(idelem);
                            prev_color = elems.style.color;
                            elems.style.color = "#87CEEB";
                            elems.style.cursor = "crosshair";
                            elem_prev = elems;
                          }
                        }
                      }
                      else{
                        elem_prev = 0;
                        prev_color = "#000000";
                      }
                    }
                    else {
                      tabl_head = document.getElementById('tdcaption_set');
                      pos_head = positon_tab(tabl_head);
                      if ((mousePosX > pos_head.x) && (mousePosX < (pos_head.x + pos_head.width)) && (mousePosY > pos_head.y) && (mousePosY < (pos_head.y + pos_head.height))){
                        obj.style.cursor = "crosshair";
                        if (elem_prev != 0) {
                          elem_prev.style.color = prev_color;
                          elem_prev.style.cursor = "pointer";
                          elem_prev = 0;
                          prev_color = "#000000";
                        }
                        elems = document.getElementById("caption_set");
                        prev_color = elems.style.color;
                        elems.style.color = "#87CEEB";
                        tabl_head.style.cursor = "crosshair";
                        elem_prev = elems;
                      }
                      else{
                        obj.style.cursor = "pointer";
                        if (elem_prev != 0) {
                          elem_prev.style.color = prev_color;
                          elem_prev.style.cursor = "pointer";
                          elem_prev = 0;
                          prev_color = "#000000";
                        }
                      }
                    }
                  }
                }
              }
              function clone(obj) {
                var newObj = obj.cloneNode(true);
                newObj.id = "clone";
                return newObj;
              }
              function positon_tab(obj){
                var w = obj.offsetWidth;
                var h = obj.offsetHeight;
                var l = 0, t = 0;
                while(obj) {
                  l += obj.offsetLeft;
                  t += obj.offsetTop;
                  obj = obj.offsetParent;
                }
                return {x: l, y: t, width: w, height: h};
              }
              function JS(menu, button) {
                nameDiv = document.getElementById(menu);
                if (!nameDiv) {
                  return;
                }
                mybutton = document.getElementById(button);
                if (!mybutton) {
                  return;
                }
                //alert(button);
                if(nameDiv.style.display == 'none') {
                  nameDiv.style.display='block';
                  nameDiv.style.cursor = 'pointer';
                  mybutton.src = "/icons/minus.gif";
                  mybutton.value = "-";
                  //alert("before if");
                  if (strCookie == "") {
                    //alert("pusto");
                    strCookie = menu;
                  }
                  else{
                    //alert("ne pusto");
                    strCookie += "," + menu;
                  }
                }
                else {
                  nameDiv.style.display='none';
                  mybutton.src = "/icons/plus.gif";
                  mybutton.value = "+";
                  //alert(strCookie);
                  if (strCookie != "") {
                    pos = strCookie.indexOf(menu);
                    end = strCookie.length;
                    //alert(pos);
                    if ((pos != -1) && (pos != 0)) {
                      str_t = strCookie.substring(pos-1, pos);
                      if (str_t == ',') {
                        str_t = strCookie.substring(0, pos-1) + strCookie.substring(pos + menu.length, end);
                      }
                      else{
                        str_t = strCookie.substring(pos+1, pos+2);
                        if (str_t == ',') {
                          str_t = strCookie.substring(0, pos) + strCookie.substring(pos + menu.length+1, end);
                        }
                        else{
                          str_t = strCookie.substring(0, pos) + strCookie.substring(pos + menu.length, end);
                        }
                      }
                      strCookie = str_t;
                      //alert(strCookie);
                    }
                    if (pos == 0) {
                      end = strCookie.length;
                      if (menu.length == end) {
                        str_t = "";
                      }
                      else{
                        str_t = strCookie.substring(menu.length+1, end);
                      }
                      //alert(str_t);
                      strCookie = str_t;
                      //alert(strCookie);
                    }
                  }
                }
                setCookie("display", strCookie);
              }
              function JS_check(menu) {
                //alert("js_check");
                nameDiv = document.getElementById(menu);
                //alert(menu);
                if (!nameDiv) {
                  return;
                }
                if(nameDiv.style.display == 'none') {
                  nameDiv.style.display='block';
                }
                else {
                  nameDiv.style.display='none';
                }
              }
              
              function click_delete(elem){
                pos = elem.indexOf("subSet");
                var flag;
                if (pos == -1){
                  pos = elem.indexOf("Set") + 3;
                  flag = 1;
                }
                else{
                  pos += 6;
                  flag = 0;
                }
                rend = elem.length;
                str = elem.substring(pos, rend);
                
                if (document.getElementById(elem).value == 0 || !document.getElementById(elem).value) {
                  //document.getElementById(elem).src = "/icons/unchecked1.gif";
                  document.getElementById(elem).value = "1";
                  i = str;
                  elem_name = document.getElementById('spany' + i);
                  name = elem_name.innerHTML;
                  quest = 'Do you really want to remove layer \"'+ name + '\" of the set?';
                  var src = window.confirm(quest);
                  if (src){
                    //i = 0;
                    i = parseInt((document.forms["myform2"].deletes).value) + 1;
                    document.forms["myform2"].deletes.value = i;
                    //alert(document.forms["myform2"].deletes);
                    document.forms["myform2"].Add_inset.value = 0;
                    if (flag == 1) {
                      document.forms["myform2"].Set.value = str;
                    }
                    else{
                      document.forms["myform2"].subSet.value = str;
                    }
                    setCookie("display", strCookie);
                    document.forms["myform2"].submit();
                    
                  }
                  else{
                    //document.getElementById(elem).checked = 0;
                    document.getElementById(elem).value = "0";
                    //document.getElementById(elem).src = "/icons/empty_check4.gif";
                  }
                  
                }
                
              }
              
              
              function click_sublayer(str, elem_noset, image, in_ou){
                if (document.getElementById("setsub_"+str)){
                  str_begin = "setsub_";
                }
                else {
                  str_begin = "set_";
                }
                if (in_ou == 1) {
                  document.getElementById(str_begin+str).style.color = "#8B8682";
                }
                else {
                  document.getElementById(str_begin+str).style.color = "#000000";
                }
                span_elem = document.getElementById("span_checkincl"+str);
                if (span_elem) {
                  var array_str = str.split('_');
                  lens = array_str.length;
                  if (lens > 1){
                    str = "subSet"+ array_str[0]+'_'+array_str[lens-1];
                  }
                  else{
                    str  = "subSet"+str;
                  }
                  len_form2 = myform2.elements.length;
                  var j = 0;
                  for (j = 0; j < len_form2; j++) {
                    rend = myform2.elements[j].id.length;
                    if (myform2.elements[j].id.indexOf(str+"_") != -1) {
                      //alert(myform2.elements[j].id);
                      pos = myform2.elements[j].id.indexOf("subSet");
                      if (pos!= -1) {
                        pos += 6;
                        //rend = myform2.elements[j].id.length;
                        str_t = myform2.elements[j].id.substring(pos, rend-1);
                        //alert(str_t);
                        if (in_ou == 1){
                          elem_noset.value += str_t + ";";
                        }
                        else{
                          if (elem_noset.value) {
                            pos_t = elem_noset.value.indexOf(str_t+';');
                            if (pos_t != -1) {
                              len_noset = elem_noset.value.length;
                              len_str = str_t.length;
                              if ((pos_t == 0) && (len_str == len_noset)){
                                elem_noset.value = "";
                              }
                              else {
                                elem_noset.value = elem_noset.value.substring(0, pos_t) + elem_noset.value.substring(pos_t+len_str+1, len_noset);
                              }
                              //alert(elem_noset.value);
                            }
                          }
                          if ((!elem_noset.value) && (list_click != "")){
                            elem_noset.value = "-1";
                          }
                          if ((!elem_noset.value) && (list_click == "")){
                            elem_noset.value = "";
                          }
                        }
                        list_elems = document.getElementsByName("subSet");
                        flag = 0;
                        i = 0;
                        if (list_elems) {
                          len_list= list_elems.length;
                          while((flag == 0) && (i < len_list)) {
                            if (list_elems[i].id == myform2.elements[j].id){
                              list_elems[i].src = image;
                              //alert(in_ou);
                              if (in_ou == 1) {
                                list_elems[i].disabled = 1;
                                myform2.elements[j].disabled = 1;
                                myform2.elements[j].value = "1";
                                //alert(myform2.elements[j].disabled);
                              }
                              else {
                                list_elems[i].disabled = 0;
                                myform2.elements[j].disabled = 0;
                                myform2.elements[j].value = "0";
                                //alert(myform2.elements[j].disabled);
                              }
                              flag = 1;
                            }
                            i += 1;
                          }
                        }
                        pos_tt = myform2.elements[j].id.indexOf("subSet");
                        pos_tt += 6;
                        rend_tt = myform2.elements[j].id.length;
                        str_tt = myform2.elements[j].id.substring(pos_tt, rend_tt-1);
                        //alert(str_tt);
                        click_sublayer(str_tt, elem_noset, image, in_ou);
                      }
                    }
                  }
                }
              }
              function click_incl(idclick, elem){
                if (document.getElementById(idclick).disabled == true) {
                  return 0;
                }
                pos = idclick.indexOf("subSet");
                var flag;
                if (pos == -1){
                  pos = idclick.indexOf("Set") + 3;
                  flag = 1;
                }
                else{
                  pos += 6;
                  flag = 0;
                }
                rend = idclick.length;
                str = idclick.substring(pos, rend-1);
                //alert(idclick);
                //alert(document.getElementById(idclick).disabled);
                if ((document.getElementById(idclick).value == "0") || (!document.getElementById(idclick).value)) {
                  //alert(document.getElementById(idclick).value);
                  document.getElementById(idclick).value = "1";
                  elem.src = "/icons/empty_check4.gif";
                  elem_noset = document.forms["myform2"].list_noset;
                  if ((elem_noset.value) && (elem_noset.value != "-1")){
                    elem_noset.value += str + ";";
                  }
                  else{
                    elem_noset.value = str + ";";
                  }
                  //alert(elem_noset.value);
                  if (document.forms["myform2"].Add_inset.value){
                    i = parseInt(document.forms["myform2"].Add_inset.value) + 1;
                  }
                  else{
                    i = 1;
                  }
                  document.forms["myform2"].Add_inset.value = i;
                  //alert("span_checkincl"+str);
                  click_sublayer(str, elem_noset, "/icons/empty_check4.gif", 1);
                  //alert(elem_noset.value);
                }
                else {
                  //alert(document.getElementById(idclick).value);
                  document.getElementById(idclick).value = "0";
                  elem.src = "/icons/checked1.gif";
                  elem_noset = document.forms["myform2"].list_noset;
                  //alert(elem_noset.value);
                  if (elem_noset) {
                    if (elem_noset.value){
                      //alert(';'+str+';');
                      pos_t = elem_noset.value.indexOf(';' + str + ';');
                      //alert("pos_t");
                      //alert(elem_noset.value);
                      if (pos_t == -1){
                        pos_t = elem_noset.value.indexOf(str+';');
                      }
                      //alert(elem_noset.value);
                      //alert(pos_t);
                      len_noset = elem_noset.value.length;
                      len_str = str.length;
                      if (pos_t != -1) {
                        if ((pos_t == 0) && (len_str == len_noset)){
                          elem_noset.value = "";
                        }
                        else{
                          elem_noset.value = elem_noset.value.substring(0, pos_t) + elem_noset.value.substring(pos_t+len_str+1, len_noset);
                        }
                        //alert(elem_noset.value);
                      }
                    }
                    if ((!elem_noset.value) && (list_click != "")){
                      elem_noset.value = "-1";
                    }
                    if ((!elem_noset.value) && (list_click == "")){
                      elem_noset.value = "";
                    }
                    //alert(elem_noset.value);
                    if (document.forms["myform2"].Add_inset.value != "0"){
                      i = parseInt(document.forms["myform2"].Add_inset.value) - 1;
                    }
                    else{
                      i = 0;
                    }
                    document.forms["myform2"].Add_inset.value = i;
                    click_sublayer(str, elem_noset, "/icons/checked1.gif", 0);
                    //alert(elem_noset.value);
                  }
                }
              }
              function click_layer(elem, myform) {
                pos = elem.id.indexOf("checklayer");
                rend = elem.id.length;
                str = elem.id.substring(pos+10, rend);
                var newstr = str + ";";
                //alert(elem.value == 0);
                if (elem.value == "0" || !elem.value) {
                  //alert("checked");
                  elem.src = "/icons/checked1.gif";
                  elem.value = "1";
                  if (document.forms["formresource"].Layer.value == "") {
                    document.forms["formresource"].Layer.value = newstr;
                  }
                  else {
                    document.forms["formresource"].Layer.value += newstr;
                  }
                }
                else {
                  elem.src = "/icons/empty_check4.gif";
                  elem.value = "0";
                  posit = document.forms["formresource"].Layer.value.indexOf(newstr);
                  if (posit != -1) {
                    newstr_t = document.forms["formresource"].Layer.value.substring(0, posit - 1);
                    len = document.forms["formresource"].Layer.value.length;
                    newstr_t += document.forms["formresource"].Layer.value.substring(posit + newstr.length, len);
                    if (newstr_t == ";" || newstr_t == " " ) {
                      newstr_t = "";
                    }
                    document.forms["formresource"].Layer.value = newstr_t;
                  }
                }
              }
              function changeImg(elem) {
                elem.src = \"/icons/down.gif\";
              }
              function setCookie(name, value){
                document.cookie = name + "=" + escape(value);
              }
              function getCookie(name) {
                var cookie = " " + document.cookie;
                var search = " " + name + "=";
                var setStr = null;
                var end = 0;
                if (cookie.length > 0) {
                  offset = cookie.indexOf(search);
                  if (offset != -1) {
                    offset += search.length;
                    end = cookie.indexOf(";", offset);
                    if (end == -1) {
                      end = cookie.length;
                    }
                    setStr = unescape(cookie.substring(offset, end));
                  }
                  else {
                    return -1;
                  }
                  return (setStr);
                }
                else {
                  return -1;
                }
                
              }
              function cut_str(oldstr, substr){
                //alert("cut");
                var newstr = "";
                pos_t = oldstr.indexOf(substr);
                rend = substr.length;
                if ((pos_t != 0) && (pos_t != -1)){
                  str_e = oldstr.substring(pos_t-1, pos_t);
                  end_l = oldstr.length;
                  if (str_e == ',') {
                    newstr = oldstr.substring(0, pos_t-1) + oldstr.substring(pos_t + rend, end_l);
                  }
                  else{
                    str_e = oldstr.substring(pos_t, pos_t+1);
                    if (str_e == ',') {
                      newstr = oldstr.substring(0, pos_t) + oldstr.substring(pos_t + rend+1, end_l);
                    }
                    else{
                      newstr = oldstr.substring(0, pos_t) + oldstr.substring(pos_t + rend, end_l);
                    }
                  }
                  //alert(newstr);
                  return newstr;
                }
                if (pos_t == 0) {
                  end_l = oldstr.length;
                  if (rend == end_l){
                    newstr = "";
                  }
                  else{
                    newstr = oldstr.substring(pos_t + rend+1, end_l);
                  }
                  //alert(newstr);
                  return newstr;
                }
              }
              function open_display(names){
                alert('before');
                var str_t = getCookie(names);
                alert('after');
                //alert(str_t);
                if (str_t) {
                  alert(str_t);
                  array_menu = str_t.split(',');
                  end = array_menu.length;
                  strCookie = str_t;
                  for (i = 0; i < end; i++) {
                    pos = array_menu[i].indexOf("menuset");
                    rend = array_menu[i].length;
                    if (pos != -1) {
                      number = array_menu[i].substring(pos+7, rend);
                      elem = document.getElementById('butt' + number);
                      if (!elem) {
                        //alert(array_menu[i]);
                        //alert("before cut");
                        strCookie = cut_str(strCookie, array_menu[i]);
                        continue;
                      }
                      else {
                        //alert(elem.id);
                        elem.src = "/icons/minus.gif";
                        elem.value = "-";
                        elem = document.getElementById("span_checkdel" + number);
                        elem.style.display = "block";
                        elem = document.getElementById("span_checkincl" + number);
                        elem.style.display = "block";
                        //alert("ok");
                      }
                    }
                    else{
                      number = array_menu[i].substring(pos+5, rend);
                      //alert(number);
                      elem = document.getElementById("button" + number);
                      if (!elem) {
                        strCookie = cut_str(strCookie, array_menu[i]);
                        continue;
                      }
                      else {
                        //alert(elem.id);
                        elem.src = "/icons/minus.gif";
                        elem.value = "-";
                        elem = document.getElementById("span_checklayer" + number);
                        elem.style.display = "block";
                        //alert("okok");
                      }
                    }
                    elem = document.getElementById(array_menu[i]);
                    elem.style.display = "block";
                  }
                  setCookie("display", strCookie);
                  //setCookie("display", "");
                  elem_noset = document.forms["myform2"].list_noset;
                  list_click = elem_noset.value;
                }
              }
              
           </script>
           <style type = "text/css">
              caption {
                text-align: center;
                font-style: italic;
                font-family: 'Times New Roman', Times, Arial;
                font-size: 19px;
                font-weight: bold;
              }
              select {
                text-align: center;
                font-style: normal;
                font-family: 'Times New Roman', Times, Arial;
                font-size: 17px;
                font-weight: normal;
              }
              TD {
                vertical-align: top;
              }
              #thead {
                height: 5%%;
                text-align: center;
                font-style: italic;
                font-family: 'Times New Roman', Times, Arial;
                font-size: 17px;
                font-weight: normal;
              }
              #body {
                width: expression(((document.documentElement.clientWidth || documentbody.clientWidth)< 350)?"350px": "100%%");
              }
              .resource_layers {
                border-style: silid;
                overflow: auto;
                border-color: black;
                border-width: 1px;
                min-width: 350px;
                max-width: 750px;
                min-height: 480px;
                max-height: 520px;
                background: white;
              }
              .set_layers {
                border-style: silid;
                overflow: auto;
                border-color: black;
                border-width: 1px;
                min-width: 480px;
                max-width: 980px;
                min-height: 480px;
                max-height: 520px;
                background: white;
              }
              .luinput {
                color: black;
                background-color: black;
                background: #fffacd;
              }
              .dd_even {
                background: #F5DEB3;
              }
              .dd_odd {
                background: #F5F5DC;
              }
              .small_button {
                width: 13px;
                height: 13px;
                <!--text-align: center;-->
                <!--background-image: url(/icons/plus1_t.gif);-->
              }
              .smallright_button {
                width: 5px;
              }
              .smallcheck {
                width: 15px;
                height: 16px;
                border: 0;
              }
              .smallcheck_r {
                width: 19px;
                height: 19px;
                border: 0;
              }
              .errdisable {
                color: #717D7D;
                background-color: white;
              }
              p {
                font-size: 16px;
                font-style: normal;
                font-weight: 500;
                font-family: 'Times New Roman', Times, Arial, serif;
                margin: 0;
              }
              #tabl1 {
                width: 100%%;
                height: 92%%;
              }
              #tabl2 {
                width: 100%%;
                height: 100%%;
              }
              #tabl3 {
                width: 100%%;
                height: 95%%;
              }
              #tabl5 {
                width: 100%%;
                height: 100%%;
                background: #F5F5DC;
              }
              #tabl5_t {
                width: 100%%;
                height: 100%%;
                background: #F5F5DC;
              }
              #tabl6 {
                width: 100%%;
                height: 83%%;
              }

              #tabl1_col1 {
                width: 40%%;
              }
              #tabl1_col2 {
                width: 60%%;
              }
              #tabl1_strok1 {
                height = 50%%;
              }
              #tabl2_strok1 {
                height: 87%%;
              }
              #tabl2_strok2 {
                height: 13%%;
              }
              #tabl3_strok1 {
                height: 5%%;
              }
              #tabl3_strok2 {
                height: 85%%;
              }
              #tabl4_strok1 {
                height: 5%%;
              }
              #tabl4_strok2 {
                height: 85%%;
              }
              #tabl5_col1 { 
                width: 95%%;
              }
              #tabl5_col2 { 
                width: 5%%;
              }
              #tabl6_col1 {
                width: 96%%;
              }
              #tabl6_col2 { 
                width: 2%%;
              }
              #table7_strok1 {
                height: 95%%;
              }
              #select_style {
                width: 100%%;
                height: 100%%;
              }
              #button {
                tesx-align: center;
                width: 100%%;
                height: 100%%;
                font-size: 17px;
                font-style: normal;
                font-weight: 500;
                font-family: 'Times New Roman', Times, Arial, serif;
              }
              #select_def {
                background-color: #87CEEB;
              }
              span {
                margin: 0 0 1 2;<!-- inherit-->
              }
              span_check {
                margin: 0 0 0 0;<!-- inherit-->
              }
              .moves {
                cursor: pointer;
                margin: 0 0 1 2;
              }
              .classic { 
                background: #F2F2F2;<!--#FFFFAA; -->
                border: 1px ridge #EBEBEB; 
                padding: 0.8em 1em; 
              }
              .tooltip {
                color: #000000;
                outline: none;
                cursor: help; 
                text-decoration: none;
                position: relative;
              }
              .tooltip spany {
                margin-left: -999em;
                position: absolute;
              }

              .tooltip:hover spany {
                font-family: Calibri, Tahoma, Geneva, sans-serif;
                position: absolute;
                right: 4em;
                top: -1em;
                z-index: 99;
                margin-left: 0;
                width: 200px;
              }
            </style>
          </HEAD>
          <BODY>
            <TABLE id = "tabl1" border= "2" cellpadding = "0" cellspacing = "0">
              <caption><H1> WMS-layers managment system </H1></caption>
              <TR>
                <TD id = "tabl1_col1">
                  <TABLE id = "tabl2" border= "1" cellpadding = "2" cellspacing = "1">
                    <TR id = "tabl2_strok1">
                      <TD>
                        <TABLE id = "tabl3" border="0" cellpadding = "1" cellspacing = "1">
                          <caption> WMS Resources: </caption>
                          <form name = "myform" action = "WM.cgi" method = "GET">
                            <TR id = "tabl3_strok1">
                              <TD colspan = "4" align = "center">
                                %s
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                            </TR>
                          </form>
                          <TR id = "tabl3_strok1">
                            <TD>
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <INPUT TYPE = SUBMIT id = "button" value = "add new" name = "addresources"
                                  onClick = "getrequest(this.form);">
                                <INPUT type = hidden name = resources value = "">
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type=hidden name = wmslists value = %s>
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </form>
                            </TD>
                            <TD>
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <INPUT TYPE = SUBMIT id = "button"  value = "update" name = "Update">
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type=hidden name = wmslists value = %s>
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </form>
                            </TD>
                            <TD>
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <INPUT TYPE = SUBMIT id = "button"  value = "delete" name = "RSDelete">
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type=hidden name = wmslists value = %s>
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </form>
                            </TD>
                          </TR>
                          <TR id = "tabl3_strok2">
                            <TD colspan = "4">
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <div class = "resource_layers">
                                  %s
                                </div>
                              </form>
                            </TD>
                          </TR>
                          <TR id = "tabl3_strok1">
                            <form name = "formresource" action = "WM.cgi" method = "GET">
                              <TD colspan = "2">
                              </TD>
                              <TD align = "right">
                                <INPUT TYPE = SUBMIT id = "button" 
                                  value = "add selected items ->" name = "add_layer">
                                <INPUT type = hidden name = Layer value = "">
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type=hidden name = wmslists value = %s>
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                            </form>
                          </TR>
                        </TABLE>
                      </TD>
                    </TR>
                    <TR id = "tabl2_strok2">
                      <TD>
                        <TABLE id = "tabl6" border="0" cellpadding = "3" cellspacing = "1">
                          <caption> Custom layer groups: </caption>
                          <form name = "myform" action = "WM.cgi" method = "GET">
                            <TR id = "tabl1_strok1">
                              <TD colspan = "2" align = "center">
                                %s
                                <INPUT type=hidden name = setlists value = %s>
                                <INPUT type=hidden name = wmslists value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                              <TD colspan = "2" align = "center" 
                                  style = "
                                           background: #F5F5DC;
                                          ">
                                <p align = "center" style = "height: 17px;">
                                  %s
                                </p>
                              </TD>
                            </TR>
                          </form>
                          <TR id = "tabl1_strok1">
                            <form name = "form2" action = "new_group.cgi" method = "GET">
                              <TD align = "center">
                                <INPUT TYPE=SUBMIT id = "button" value = "create" name="group">
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = Nwms value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                            </form>
                            <form name = "myform" action = "new_group.cgi" method = "GET">
                              <TD align = "center">
                                <INPUT TYPE = SUBMIT id = "button"  value = "edit" name="editgr">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = Nwms value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                            </form>
                            <form name = "myform" action = "WM.cgi" method = "GET">
                              <TD align = "center">
                                <INPUT TYPE = SUBMIT id = "button"  value = "add ->" name="Add">
                              </TD>
                              <TD align = "center">
                                <INPUT TYPE = SUBMIT id = "button"  value = "delete" name="delgr">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                                <INPUT type = hidden name = SLD value = %s>
                              </TD>
                            </form>
                          </TR>
                        </TABLE>
                      </TD>
                    </TR>
                  </TABLE>
                </TD>
                <TD id = "tabl1_col2">
                  <TABLE id = "tabl2" border="1" cellpadding = "3" cellspacing = "1">
                    <TR id = "tabl2_strok1">
                      <TD>
                        <TABLE id = "tabl3" border="0" cellpadding = "1" cellspacing = "1">
                          <caption> User's layer set: </caption>
                          <form name = "myform" action = "WM.cgi" method = "GET">
                            <TR id = "tabl4_strok1">
                              <TD colspan = "3" align = "center">
                                %s
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                              </TD>
                            </TR>
                          </form> 
                          <TR id = "tabl4_strok1">
                            <form name = "myform" action = "WM.cgi" method = "GET">
                              <TD width = "33%%" align = "center">
                                <INPUT TYPE = SUBMIT id = "button" value = "create new" name = "newset"
                                  onClick = "getset(this.form);">
                                <INPUT type = hidden name = filename value = "">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                              </TD>
                            </form>
                            <form name = "myform" action = "WM.cgi" method = "GET">
                              <TD width = "33%%"  align = "center">
                                <INPUT TYPE = SUBMIT id = "button" value = "edit" name = "editSet"
                                  onClick = "edit_nameset(this.form);">
                                <INPUT type = hidden name = editname value = "">
                                <INPUT type = hidden name = oldname value = "%s">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                              </TD>
                            </form>
                            <form name = "myform" action = "WM.cgi" method = "GET">
                              <TD width = "33%%"  align = "center">
                                <INPUT TYPE = "SUBMIT" id = "button" value = "delete" name = "DeleteSet"
                                 onClick = "Delete_Set(this.form);">
                                <INPUT type = hidden name = oldname value = "%s">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                              </TD>
                            </form>
                          </TR>
                          <TR id = "tabl4_strok2">
                            <TD colspan = "3">
                              <div class = "set_layers">
                                <TABLE id = "tabl5" border="0" cellpadding = "0" cellspacing = "0">
                                  <TR id = "thead">
                                    <TD align = "center" id = "tdcaption_set" 
                                        style = "border-bottom: 1px solid black;
                                                 border-right: 1px solid black;
                                                 border-left: 1px solid black;
                                                 border-top: 1px solid black;">
                                      <p style = "height: 5%%; text-align: center; font-style: italic;
                                        font-family: 'Times New Roman', Times, Arial;
                                        font-size: 17px; font-weight: normal;"
                                        id = "caption_set">
                                        %s
                                      </p>
                                    </TD>
                                    <TD align = "center" 
                                        style = "border-bottom: 1px solid black;
                                                 border-right: 1px solid black;
                                                 border-top: 1px solid black;">
                                      &nbsp;active&nbsp;
                                    </TD>
                                    <TD align = "center" 
                                        style = "border-bottom: 1px solid black;
                                                 border-right: 1px solid black;
                                                 border-top: 1px solid black;">
                                      &nbsp;delete&nbsp;
                                    </TD>
                                  </TR>
                                  <TR id = "table7_strok1">
                                    <form name = "myform1" action = "WM.cgi" method = "GET">
                                      <TD id = "tabl6_col1">
                                        %s
                                        <INPUT type = hidden name = Layer value = "">
                                        <INPUT type = hidden name = Set value = "">
                                        <INPUT type = hidden name = subSet value = "">
                                        <INPUT type=hidden name = setlists value = %s>
                                        <INPUT type=hidden name = wmslists value = %s>
                                        <INPUT type = hidden name = newgroup value = %s>
                                        <INPUT type = hidden name = SLD value = %s>
                                      </TD>
                                    </form>
                                    <form name = "myform2" action = "WM.cgi" method = "GET">
                                      <TD id = "tabl6_col2" align = "center">
                                        %s
                                        <INPUT type = hidden name = "Add_inset" value = "%d">
                                        <INPUT type = hidden name = "list_noset" value = "%s">
                                      </TD>
                                      <TD id = "tabl6_col2" align = "center">
                                        %s
                                        <INPUT type = hidden name = "deletes" value = "0">
                                        <INPUT type = hidden name = "Set" value = "">
                                        <INPUT type = hidden name = "subSet" value = "">
                                      </TD>
                                    </TR>
                                  </TABLE>
                                </div>
                              </TD>
                            </TR>
                            <TR id = "tabl4_strok1">
                              <TD colspan = "2">
                              </TD>
                              <TD align = "center">
                                <INPUT TYPE = "SUBMIT" name="save" id = "button" value = "save&public"
                                  onClick = "save_public(this.form);">
                                <INPUT type = hidden name = message value = "%s">
                                <INPUT type = hidden name = Layer value = "">
                                <INPUT type = hidden name = newgroup value = %s>
                                <INPUT type = hidden name = setlists value = %s>
                                <INPUT type = hidden name = wmslists value = %s>
                              </TD>
                            </form>
                          </TR>
                        </TABLE>
                      </TD>
                    </TR>
                    <TR id = "tabl2_strok2">
                      <TD>
                        <TABLE id = "tabl6" border="0" cellpadding = "3" cellspacing = "1">
                          <caption> Custom SLD: </caption>
                            <TR id = "tabl1_strok1">
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <TD colspan = "3" align = "center">
                                  %s
                                  <INPUT type = hidden name = newgroup value = %s>
                                  <INPUT type = hidden name = setlists value = %s>
                                  <INPUT type = hidden name = wmslists value = %s>
                                </TD>
                              </form>
                            </TR>
                            <TR id = "tabl1_strok1">
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <TD align = "center">
                                  <INPUT TYPE=SUBMIT id = "button" value = "upload SLD" name = "addSLD">
                                  <INPUT type = hidden name = newgroup value = %s>
                                  <INPUT type = hidden name = setlists value = %s>
                                  <INPUT type = hidden name = wmslists value = %s>
                                </TD>
                              </form>
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <TD align = "center">
                                  <INPUT TYPE=SUBMIT id = "button"  value = "delete SLD" name = "deleteSLD">
                                  <INPUT type = hidden name = SLD value = %s>
                                  <INPUT type = hidden name = newgroup value = %s>
                                  <INPUT type = hidden name = setlists value = %s>
                                  <INPUT type = hidden name = wmslists value = %s>
                                </TD>
                              </form>
                              <form name = "myform" action = "WM.cgi" method = "GET">
                                <TD align = "center">
                                  <INPUT TYPE=SUBMIT id = "button"  value = "clear cache" name = "clearCache">
                                  <INPUT type = hidden name = SLD value = %s>
                                  <INPUT type = hidden name = newgroup value = %s>
                                  <INPUT type = hidden name = setlists value = %s>
                                  <INPUT type = hidden name = wmslists value = %s>
                                </TD>
                              </form>
                            </TR>
                          </TABLE>
                        </TD>
                      </TR>
                    </TABLE>
                  </TD>
                </TR>
              </TABLE>
          </BODY>
          <script>
            alert("ok");
            open_display("display");
            alert("gfr");
          </script>
        </HTML>
       """
  return html
 


