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
# get_tag: Create header and service part of the document. Return subtree wmt.
#          Infile - name xmlfile, dom -xml tree. 
def get_tag(dom, Nset, wayURL, filename, Nwms_dtd):
  
  # write heer part in xml file 
#  print "Content-Type: text/html\n\n"

  print "Content-Disposition: attachment; charset=utf-8; filename=\"%s.xml\"\r\n\n"%(filename),\
          dom.toprettyxml(indent='\t', newl='\n', encoding='UTF-8'),\
        '<!DOCTYPE WMT_MS_Capabilities SYSTEM \"%s?schema=%d\">\n'%(wayURL, Nwms_dtd)
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
  OnlineResources = dom.createElement("OnlineResource")
  OnlineResources.setAttribute('xlink:href', '%s?Set=%s'%(wayURL, filename))
  OnlineResources.setAttribute('xlink:type', 'simple')
  OnlineResources.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
  service.appendChild(OnlineResources)
  # adding contact information in subtree Service
  contact_info(dom, service)

  feeds = dom.createElement("Fees")
  feeds.appendChild(dom.createTextNode("NONE"))
  service.appendChild(feeds)
  
  access = dom.createElement("AccessConstraints")
  access.appendChild(dom.createTextNode("NONE"))
  service.appendChild(access)
  
  return wmt

#
# Get_Request:
def Get_Request(dom, nametag, request, wayURL, cur, WMSlist, nameset, flPost):
  Getdom = dom.createElement("%s"%nametag)
  request.appendChild(Getdom)
  
  Ntmp = -1
  spis_pred = []
  i = 0
  for v in WMSlist:
    if Ntmp == v:
      continue
    Ntmp = v
    result = []
    res = BD.interset_request(cur, "WMSresources", "Capabilites",\
                            "//Capability/Request/%s/Format"%nametag, "Nwms", v)
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
  format = dom.createTextNode("%s" % strformat)
  Getdom.appendChild(format)  
  
  DCP = dom.createElement("DCPType")
  Getdom.appendChild(DCP)

  HTTP = dom.createElement("HTTP")
  DCP.appendChild(HTTP)

  Gettag = dom.createElement("Get")
  HTTP.appendChild(Gettag)

  Resource = dom.createElement("OnlineResource")
  Resource.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
  Resource.setAttribute('xlink:type', 'simple')
  Resource.setAttribute('xlink:href', "%s?Set=%s" % (wayURL, nameset))
  Gettag.appendChild(Resource)
  
  if flPost:
    Post = dom.createElement("Post")
    HTTP.appendChild(Post)

    Resource = dom.createElement("OnlineResource")
    Resource.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink')
    Resource.setAttribute('xlink:type', 'simple')
    Resource.setAttribute('xlink:href', "%s?Set=%s&SERVICE=WMS&" % (wayURL, nameset))
    Post.appendChild(Resource)

  return request
