#
# input_error:
def input_error(error):
  error = "<p>" + error + "</p>"
  print error

#
# exit_error:
def exit_error(Nerr, error):
  input_error(error)
  exit(Nerr)

#
# transact:
def transact(cur, req):
  cur.execute(req)

#
# save_transact:
def save_transact(cur, conn, req):
  transact(cur, req)
  conn.commit()

#
# err_transact:
def err_transact(conn, error):
  input_error(error)
  conn.commit()
