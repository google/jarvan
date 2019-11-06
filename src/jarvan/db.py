"""Mysql DB helper.
"""
import os
import pymysql
import time
from flask import request
import pymysql.cursors
from jarvan import kms_helper
from jarvan import j
import json
from flask import g

def get_sql_history():
  h=[]
  for sql in g.sql_history:
    if "select email from main_sessions where hash=" not in sql:
      h.append(" ".join(sql.split())) 
  return h


def open_connection(credentials):
  """Opens connection.
  """
  g.sql_history = []

  try:
    cred = json.loads(kms_helper.decrypt(credentials))
  except json.decoder.JSONDecodeError:
    return None

  if "local" in request.host:
    cred["CLOUD_SQL_CONNECTION_NAME"] = None
  else:
    cred["CLOUD_SQL_DATABASE_HOST"] = None
    

  g.db_connection = pymysql.connect(
      user=cred["CLOUD_SQL_USERNAME"],
      password=cred["CLOUD_SQL_PASSWORD"],
      unix_socket=cred["CLOUD_SQL_CONNECTION_NAME"],
      db=cred["CLOUD_SQL_DATABASE_NAME"],
      host=cred["CLOUD_SQL_DATABASE_HOST"],
      cursorclass=pymysql.cursors.DictCursor)

  g.db_cursor = g.db_connection.cursor()



def full_res(sql, params=None, count=0):
  """Returns full dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    Array of records
  """
  out = []
  sql = parse(sql, params)
  g.db_cursor.execute(sql)
  data = g.db_cursor.fetchall()
  for row in data:
    out.append(row)

  g.sql_history.append(g.db_cursor._last_executed)  

  return out


def first_row(sql, params=None, count=0):
  """Returns first row of dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    First record
  """
  out = None
  sql = parse(sql, params)
  g.db_cursor.execute(sql)
  data = g.db_cursor.fetchone()
  if data:
    out = data

  g.sql_history.append(g.db_cursor._last_executed)  

  return out


def insert(sql, params=None):
  query(sql, params)
  return res("SELECT LAST_INSERT_ID()")

def query(sql, params=None):
  """Executes a query, i.e UPDATE or INSERT.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    Int, number of affected records
  """
  out = 0
  sql = parse(sql, params)
  g.db_cursor.execute(sql)
  out = g.db_cursor.rowcount
  g.sql_history.append(g.db_cursor._last_executed)  

  g.db_connection.commit()
   
  return out


def res(sql, params=None, count=0):
  """Returns first field of first record of dataset.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    string with result
  """
  sql = parse(sql, params)
  g.db_cursor.execute(sql)
  result = ""
  row = g.db_cursor.fetchone()

  g.sql_history.append(g.db_cursor._last_executed)  

  if row:
    for field in row:
      return str(row[field])

  return ""


def res_int(sql, params=None):
  """Returns first field of first record of dataset as int.

  Args:
    sql: SELECT string
    params: params to update the query

  Returns:
    int with result
  """
  out = 0
  try:
    out = int(res(sql, params))
  except ValueError:
    pass

  return out

import re
from decimal import Decimal, DecimalException



def parse(q, method_params={}):
  params = {}

  for v in request.values:
    params[v] = j.get_param(v)
  
  # iterate method params
  try:
    for p in method_params:
      params[p] = method_params[p]
  except TypeError:
    pass


  # replace dict as a list of strings
  m = (re.findall(r"\{list:([\[\]\ A-Za-z0-9\_]*)\}", q))
  replaced = ""
  for p in m:
    if p in method_params:
      params[p] = method_params[p]
    else:
      params[p] = j.get_list_param(p)


    # found, replace
    for value in params[p]:
      if replaced:
        replaced = replaced + ", "
      v = str(value)
      v = escape(v)
      replaced = replaced + "'" + v + "'" 
    q = q.replace("{list:"+p+"}", replaced)


  # replace as decimal 
  m = (re.findall(r"\{decimal\:([\ A-Za-z0-9\_]*)\}", q))
  for p in m:
    v = 0.0
    if p in params:
      try:
        v = Decimal(str(params[p]))
      except DecimalException:
        pass 
      except ValueError:
        pass 
    q = q.replace("{decimal:"+p+"}", str(v))

  # replace as integer 
  m = (re.findall(r"\{int\:([\ A-Za-z0-9\_]*)\}", q))
  for p in m:
    v = 0
    if p in params:
      try:
        v = int(str(params[p]).split('.')[0])
      except ValueError:
        pass 
    q = q.replace("{int:"+p+"}", str(v))

  # replace as plain text without qoutes and without escaping. 
  # WARNING: use it only with controlled parameters, as it will
  # not protect against sql injection. 
  m = (re.findall(r"\{text\:([\ A-Za-z0-9\_]*)\}", q))
  for p in m:
    v = ""
    if p in params:
      v = params[p]
    q = q.replace("{text:"+p+"}", str(v))

  # replace as string 
  m = (re.findall(r"\{([\ A-Za-z0-9\_]*)\}", q))
  for p in m:
    v = ""
    if p in params:
      v = str(params[p])
    v = escape(v)
    q = q.replace("{"+p+"}", "'" + v + "'")

  if method_params and "print" in method_params:
    print(q)

  return q

def escape(v):
  return g.db_connection.escape(v)[1:][:-1]
