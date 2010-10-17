#
# create_bd.py: 
#
import psycopg2
import random
import errors
import platform

#
# open_bd: Open database. Return cur - cursor and conn - connected.
def open_BD():
  #bd
  try:
    infile = open('.dtbase', 'r')
  except:
    print "open_BD: Error open file dtbase"
    exit(1)
  try:
    directr = infile.readline()
  except:
    print "open_BD: Error read dtbase"
    exit(1)
  #print directr
  infile.close()
  if platform.system() == 'Linux':
    try:
      infile = open('%s'%directr.strip(), 'r')
    except:
      print "open_BD: Configs file not exists"
      exit(1)
  else:
    directr = directr.strip()
    try:
      infile = open('%s'%directr.replace("\\", "\\\\"), 'r')
    except:
      print "open_BD: Configs file not exists"
      exit(1)
  try:
    dbname = infile.readline()
    user = infile.readline()
    passwd = infile.readline()
    host = infile.readline()
    if host:
      port = infile.readline()
  except:
    print "open_BD: Error read config files"
    exit(1)
  infile.close()
  # connect with database
  db = 'dbname = %s' % dbname
  user_db = 'user = %s' % user
  if not host:
    try:
      passwd_db = 'passwd = %s'% passwd
      conn = psycopg2.connect(db, user_db, passwd_db)
    # create CURrent Set Of Records for operatoin with result of inquiry
    except:
      print "Error database open"
      exit(1) 
#    cur = conn.cursor()
  else:
    passwd_db = 'password = %s'% passwd
    host_db = 'host = %s'% host
    port_db = 'port = %s'% port
    strs = db + " " + user_db + " " + passwd_db + " " + host_db + " " + port_db
    try:
      conn = psycopg2.connect(strs)
    # create CURrent Set Of Records for operatoin with result of inquiry
    except:
      errors.exit_error(1, "open_BD: Error database open")
  
  cur = conn.cursor()
  directr = directr.replace(".database", "", 1)
  return conn, cur, directr


#
# create_table: Create value in table with name "name_table". Primary_name - 
#               column name primary key. Keywords - list (key - column name, 
#               value - values). Args - other arguments for find record in table.
#               Cur - cursor for database, conn - connection for database.
#               Return primary key records.
def create_table(cur, conn, name_table, primary_name, keywords, *args):

  # Find record in table with the enqual field "Title" and args 
  requere = "SELECT " + primary_name + " FROM " + name_table +\
            " tb WHERE tb.Title  = \'" + keywords["Title"] + "\'"
  for arg in args:
    #print "fgh", arg, keywords[arg]
    requere = requere  + " AND tb." + arg + " = \'%s\'" % keywords[arg] 
    req = """%s;""" % (requere)
  #print req
    
  try:
    errors.save_transact(cur, conn, req)
    result = cur.fetchone()
  except:
    errors.exit_error(1, "create_table:BD error create table %s" % name_table)

  if not result:
    # This record don't execsits
    # Create primary key
    primary_key = get_pkey(cur, conn, name_table, primary_name)
    #print "Primary key = ", primary_key
  
    insert_data(cur, conn, name_table, primary_name, primary_key, keywords)

    return primary_key
  else: 
    #print result[0]
    req = """UPDATE %s SET"""%(name_table)
    i = 0
    for k, v in keywords.items():
      if not i:
        req = req + " %s = \'%s\'"%(k, v)
        i = 1
      else:
        req = req + ", %s = \'%s\'"%(k, v)
    req = req + " WHERE %s = %s;"%(primary_name, result[0])
    try:
      errors.save_transact(cur, conn, req)
    except:
      errors.exit_error(1, "create_table: Error UPDATE BD in create table %s" % name_table)
  # If record already exectit return primary key
  return result[0]

#
# crtable: Create value in table with name "name_table". Primary_name - 
#          column name primary key. Keywords - list input data (key - column name, 
#          value - values). lstfind - other arguments for find record in table.
#          Cur - cursor for database, conn - connection for database.
#          Return primary key records.
def crtable(cur, conn, name_table, primary_name, keywords, lstfind):
  #print "crtable"
  # Find record in table with the enqual field "Title" and args 
  requere = "SELECT " + primary_name + " FROM " + name_table +\
            " tb WHERE "
  i = 0
  for k, v in lstfind.items():
    if i == 0:
      requere = requere + " tb.%s = %s"%(k, v)
      i = 1
    else:
      requere = requere + " AND tb.%s = %s"%(k, v)
  req = requere + ";"
  #print req
  
  try:
    errors.save_transact(cur, conn, req)
    result = cur.fetchone()
  except:
#    conn.rollback()
#    result = 0
    errors.exit_error(1, "crtable: Error BD error create table %s" % name_table)

  #print "in table ", result
  if not result:
    # This record don't execsits
    # Create primary key
    primary_key = get_pkey(cur, conn, name_table, primary_name)
    #print "Primary key = ", primary_key
    insert_data(cur, conn, name_table, primary_name, primary_key, keywords)

    return primary_key

  # If record already exectit return primary key
  return result[0]

#
# delete:
def delete(cur, conn, table, val):
  req = "DELETE FROM %s WHERE"%table
  i = 0
  for k, v in val.items():
    if i == 0:
      req = req + " %s = %s"%(k, v)
      i = 1
    else:
      req = req + " AND %s = %s"%(k, v)
  req = req + ";"
  #print req
  
  try:
    errors.save_transact(cur, conn, req)
  except:
    errors.err_transact(conn, "delete: Error BD error delete from table %s %s" % (table, req))
    errors.exit_error(1, "")

#
# updatebd_xmlfield: Refreshes database xml-fields.
def updatebd_xmlfield(cur, conn, name_table, xml_field, node, primary_name,\
                      primary_key):
  
  #print "update %s" % name_table
  req = """%s;""" % ("UPDATE %s SET %s = \'%s\' WHERE %s = %s" % (name_table,\
        xml_field, node.toxml("utf-8").replace("\'", "\'\'"), primary_name, primary_key))
  try:
    errors.save_transact(cur, conn, req)
  except:
    errors.err_transact(conn, "updatebd_xmlfield: Error UPDATE %s error" % name_table)

#
# select_table: Searches in the table for corresponding elements(words).
#               Cur - currsor on database, pname - name field has primary key,
#               words - list elements for find. Return required elements.
def select_table(cur, table, pname, *words):
  
  req = """SELECT %s""" % (pname)
  for k in words:
    req = req + ", %s" % k
  req = req + " FROM %s;" % table
#  print req
  try:
    errors.transact(cur, req)
  except:
    #errors.exit_error(1, "select_table: Error BD select table %s" %table)
    print "select_table: Error BD select table %s" %table
    return 0

  result = cur.fetchall()
  
  return result

#
# ifselect_table: Searches in the table for units on a condition.
#                 Cur - currsor on database, pname - name field has primary key,
#                 words - list elements for find, keywords - list (key, value) 
#                 elements for a condition. Return required elements,
def ifselect_table(cur, table, pname, keywords, *words):

  req = """SELECT %s""" % (pname)
  # create list need elements
  if words:
    for k in words:
      req = req + ", %s" % k
  req = req + " FROM %s WHERE " % table
  
  # create condition
  i = 0
  for k, v in keywords.items():
    if i == 0:
      req = req + "%s = %s" % (k, v)
      i = 1
    else:
      req = req + " AND %s = %s" % (k, v)
  req = req + ";"
#  print req
  
  try:
#    errors.transact(cur, req)
    cur.execute(req)
  except:
  #  print "select_table: Error BD select table %s" %table
  #  return 0
    errors.exit_error(1, "ifselect_table: Error BD if select table %s" %table)
  
  result = cur.fetchall()
  #print result
  return result

#
# ifsome_tables: Searches in the table for units on a condition.
#                Cur - currsor on database, tables - name field for find,
#                keywords - list (key, value) elements for a condition,
#                nametables - list name of a tables.
#                Return required elements.
def ifsome_tables(cur, tables, keywords, *nametables):
  req = "SELECT"
  i = 0
  for k in range(0, len(tables)):
    if i == 0:
      req = req + " %s"%(tables[k])
      i = 1
    else:
      req = req + ", %s" %(tables[k])
  req = req + " FROM"
  i = 0
  for k in nametables:
    if i == 0:
      req = req + " %s" %(k)
      i = 1
    else:
      req = req + ", %s" %(k)
  # create list need elements
  req = req + " WHERE "
  # create condition
  i = 0
  for k, v in keywords.items():
    if i == 0:
      req = req + "%s = %s" % (k, v)
      i = 1
    else:
      req = req + " AND %s = %s" % (k, v)
  req = req + ";"
#  print "req", req
  
  try:
    cur.execute(req)
#    errors.transact(cur, req)
  except:
#    errors.exit_error(1, "select_table: Error BD select table %s" %table)
    print "ifsome_tables: Error BD if select table %s" %table
#    result = cur.fetchone()
#    print "result", result
    return 0

  result = cur.fetchall()
  return result

#
# interset_request: Returns an in intersection of inquiries of the necessary
#                   field. table - name table, ffield - name field, which create
#                   request, strings - what string find in xml field "ffield",
#                   pkey - primary key of table, lists - list of conditions.
def interset_request(cur, table, ffield, strings, pkey, lists):

  # Create select data from ffield with tag "strings"
  req = "SELECT xpath_nodeset(%s, '%s') FROM %s WHERE"% (ffield,\
         strings, table)
  req = req + " %s = %s" % (pkey, lists)
  req = req + ";"
  #print req

  try:
    errors.transact(cur, req)
  except:
    errors.exit_error(1, "interset_request: Error BD interset")
  
  result = cur.fetchall()
  
  return result
  
#
# insert_data: Insert data "keywords" in table "name_table", with primary 
#              key "primary_name" and value "primary_key".
def insert_data(cur, conn, name_table, primary_name, primary_key,  keywords):
  # Insert record in table with taking parameters
  requere = "INSERT INTO "+ name_table + "(" + primary_name
  # Get column name
  for k in keywords.keys():
    requere = requere + ", " + k

  requere = requere + ") VALUES (%s" % primary_key
  # Get values
  for v in keywords.values():
    requere = requere + ", \'%s\'" % v 
  req = """%s);""" % (requere)
  #print req
  try:
    errors.save_transact(cur, conn, req)
  except:
    errors.err_transact(conn, "insert_data:BD error insert data %s %s" % (name_table, req))
    errors.exit_error(1, "")
#    conn.commit()

#
# get_pkey: Get value primary key for table "name_table" with primary key 
#           "primary_name".
def get_pkey(cur, conn, name_table, primary_name):
  # Create primary key
  primary_key = random.randrange(0, 1000)
  # Find record with the received primary key
  requere = "SELECT * FROM " + name_table + " tb WHERE tb." + primary_name + " = %s"\
            % primary_key
  req = """%s;""" % (requere)
  cur.execute(req)
  result = cur.fetchall()
  #print req
#  try:
#  errors.transact(cur, req)
  while result:
    # If this primary key exectit create its again
    primary_key = random.randrange(0, 1000)
    requere = "SELECT * FROM " + name_table + " tb WHERE tb." + primary_name + " = %s"\
            % primary_key
    req = """%s;""" % (requere)
#    errors.transact(cur, req)
    cur.execute(req)
    result = cur.fetchall()
    if not result:
      return primary_key
      #cur.execute(req)
#  except:
#    conn.rollback()
#    errors.exit_error(1, "get_pkey: BD error")
  return primary_key

#
# close_BD: Close database.
def close_BD(conn):
  try:
    conn.close()
  except:
    input_error("close_BD: Error: database not close")



