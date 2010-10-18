#
# Service.py: Contains the functions forming header and service part of the xml
#             document.

import create_bd as BD

#
# contact_info: Create informations part of th document. Dom - xml tree, 
#               service - subtree dom.
def contact_info(dom, service):

  contact_inform = dom.createElement("ContactInformation")
  service.appendChild(contact_inform)
  
  contact_iperson = dom.createElement("ContactPersonPrimary")
  contact_inform.appendChild(contact_iperson)
  
  name = dom.createElement("ContactPerson")
  name.appendChild(dom.createTextNode("Nick Dobretsov Jr."))
  contact_iperson.appendChild(name)
  
  organization = dom.createElement("ContactOrganization")
  organization.appendChild(dom.createTextNode\
                          ("IGM SB RAS"))
  contact_iperson.appendChild(organization)
  
  contact_position = dom.createElement("ContactPosition")
  contact_inform.appendChild(contact_position)
  
  contact_address = dom.createElement("ContactAddress")
  contact_inform.appendChild(contact_address)
  
  address_type = dom.createElement("AddressType")
  address_type.appendChild(dom.createTextNode("Work"))
  contact_address.appendChild(address_type)
  
  address = dom.createElement("Address")
  #address.appendChild(dom.createTextNode(""))
  contact_address.appendChild(address)
  
  city = dom.createElement("City")
  city.appendChild(dom.createTextNode("Novosibirsk"))
  contact_address.appendChild(city)

  state = dom.createElement("StateOrProvince")
  #state.appendChild(dom.createTextNode(""))
  contact_address.appendChild(state)
  
  code = dom.createElement("PostCode")
  #code.appendChild(dom.createTextNode("636000"))
  contact_address.appendChild(code)
  
  country = dom.createElement("Country")
  country.appendChild(dom.createTextNode("Russia"))
  contact_address.appendChild(country)
  
  telephone = dom.createElement("ContactVoiceTelephone")
  contact_inform.appendChild(telephone)
  
  facs = dom.createElement("ContactFacsimileTelephone")
  contact_inform.appendChild(facs)
  
  email = dom.createElement("ContactElectronicMailAddress")
  email.appendChild(dom.createTextNode("dnn@uiggm.nsc.ru"))
  contact_inform.appendChild(email)

#
# get_tag: Create header and service part of the document. Return subtree Service.
#          Infile - name xmlfile, dom -xml tree. 
def get_tag(dom, server_URL, filename, Nwms_dtd):
  
  # write heer part in xml file 
  print "Content-Disposition: attachment; charset=utf-8; filename=\"%s.xml\"\r\n\n"%(filename),\
          dom.toprettyxml(indent='\t', newl='\n', encoding='UTF-8'),\
        '<!DOCTYPE WMT_MS_Capabilities SYSTEM \"%s?schema=%d\">\n'%(server_URLL, Nwms_dtd)
  # create subtree WMT_Capability
  wmt = dom.createElement("WMT_MS_Capabilities")
  wmt.setAttribute('version', '1.1.1')
  wmt.setAttribute('updateSequence', '226')
  dom.appendChild(wmt)
  
  # create service tag: name, title and abstract
  service = dom.createElement("Service")
  wmt.appendChild(service)
    
  name = dom.createElement("Name")
  name.appendChild(dom.createTextNode("WMS_RM"))
  service.appendChild(name)
  
  title = dom.createElement("Title")
  title.appendChild(dom.createTextNode("WMS Resource Manager of SB RAS"))
  service.appendChild(title)
      
  abstract = dom.createElement("Abstract")
  abstract.appendChild(dom.createTextNode(\
          "System of WMS layers management of SB RAS"))
  service.appendChild(abstract)
  
  # create service tag KeywordList
  keylist = dom.createElement("KeywordList")
  service.appendChild(keylist)
  keyword = dom.createElement("Keyword")
  keyword.appendChild(dom.createTextNode("SB RAS"))
  keylist.appendChild(keyword)
  keyword = dom.createElement("Keyword")
  keyword.appendChild(dom.createTextNode("WMS"))
  keylist.appendChild(keyword)
  keyword = dom.createElement("Keyword")
  keyword.appendChild(dom.createTextNode("IGM"))
  keylist.appendChild(keyword)
  keyword = dom.createElement("Keyword")
  keyword.appendChild(dom.createTextNode("ICT"))
  keylist.appendChild(keyword)
  # create service tag OnlineResource
  OnlineResources = dom.createElement("OnlineResource")
  OnlineResources.setAttribute('xlink:href', '%s?Set=%s'%(server_URL, filename))
  OnlineResources.setAttribute('xlink:type', 'simple')
  OnlineResources.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
  service.appendChild(OnlineResources)
  # adding contact information in subtree Service
  contact_info(dom, service)

  # create service tag Fees
  feeds = dom.createElement("Fees")
  feeds.appendChild(dom.createTextNode("NONE"))
  service.appendChild(feeds)

  # create service tag AccessConstraints
  access = dom.createElement("AccessConstraints")
  access.appendChild(dom.createTextNode("NONE"))
  service.appendChild(access)
  
  return wmt

#
# get_tagRequest: Fromated in a tag Request tags with formats used by list_WMSservers.
#              Nametag may be: GetCapabilities, GetMap, GetFeatureInfo, 
#                              DescribeLayer, GetLegendGraphic.
def get_tagRequest(dom, nametag, request_dom, server_URL, cur, list_WMSservers, nameset, needPost):
  # Create a sub tree with name "nametag"
  getdom = dom.createElement("%s"%nametag)
  request_dom.appendChild(getdom)
  
  Nwms_used = -1
  oldlist_formats = []
  count_servers = 0
  for server_id in list_WMSservers:
  # Enumerates all used servers
    # Check their recurrence
    if Nwms_used == server_id:
      continue
    Nwms_used = server_id
    # Requested format of the tag with the name "nametag" of the server server_id
    # SELECT xpath_nodeset(Capabilities, '"//Capability/Request/%s/Format"%nametag')
    # FROM WMSresources WHERE Nwms = server_id;
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                            "//Capability/Request/%s/Format"%nametag, "Nwms", server_id)
    # Stores intersection lists formats
    result = []
    if res:
    # If there is a format
      for tag_Format in res:
        strformat = tag_Format.replace("</Format>", "</Format>\n")
        if count_servers:
        # If this is not the first list of formats
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
        # If this is the first list of formats
          # The string format is divided into a list
          list_formats = strformat.split("\n")
          count_servers += 1
  # Formed a string from the list of formats
  strformat = " "
  for k in list_formats:
    strformat = strformat + "%s\n\t"%k
  # Create tag "Format"
  format = dom.createTextNode("%s" % strformat)
  getdom.appendChild(format)  
  
  DCP = dom.createElement("DCPType")
  getdom.appendChild(DCP)

  HTTP = dom.createElement("HTTP")
  DCP.appendChild(HTTP)

  Gettag = dom.createElement("Get")
  HTTP.appendChild(Gettag)

  Resource = dom.createElement("OnlineResource")
  Resource.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
  Resource.setAttribute('xlink:type', 'simple')
  Resource.setAttribute('xlink:href', "%s?Set=%s" % (server_URL, nameset))
  Gettag.appendChild(Resource)
  
  if needPost:
    Post = dom.createElement("Post")
    HTTP.appendChild(Post)

    Resource = dom.createElement("OnlineResource")
    Resource.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    Resource.setAttribute('xlink:type', 'simple')
    Resource.setAttribute('xlink:href', "%s?Set=%s&SERVICE=WMS&" % (server_URL, nameset))
    Post.appendChild(Resource)

  return request_dom
