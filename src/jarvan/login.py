"""Login helper.
"""
import json
import random
import string
from flask import jsonify
from flask import request
from jarvan import db
import requests


def run(req, action):
  """frontend for login module.

  Args:
    req: flask request
    action: action to run

  Returns:
    details from each function
  """
  if action == "register_token":
    out = register_token(req)
  elif action == "signout":
    out = do_signout(req)
  elif action == "validate_token":
    out = validate_token(req)

  return jsonify(out)


def validate_token(req):
  """Register new login token.

  Args:
    req: flask request

  Returns:
    object with logged user data
  """
  user_id = db.res(
    "select user_id "
    "from main_sessions "
    "where hash = {hash} and user_ip = {user_ip} and enabled = 1",
    {"hash": req.values.get("t"), "user_ip": request.remote_addr } )

  roles = []
  
  return { "user": { "id":user_id, "roles":roles }} 

def register_token(req):
  """Register new login token.

  Args:
    req: flask request

  Returns:
    object with logged user data
  """
  user = do_login(req.args.get("token"))
  if user["logged"]:
    # save to DB
    n = 256
    found = 1
    while found==1:
      user["hash"] = "".join(random.choices(string.ascii_uppercase +
                                          string.digits, k=n))
      found = db.res_int("select 1 from main_sessions where hash={hash}", { "hash": user["hash"] })

    user_id = "0"
    # get user id
    db.query("UPDATE main_users set status=3 "
             "where email={email} "
             "and status=1 " 
             "and valid_until_date<curdate() ",
             {"email": user["email"] } )

    user_id = db.res("SELECT id from main_users where email={email} and status=1", { "email" :user["email"] })

    auto_create = True

    if (not user_id) and auto_create:
      if user["email"].split("@")[1]!="google.com":
        return {"user": False} 
      #error
      #return {"user": False}
      # creeate new user if needed
      db.query("INSERT into main_users set email={email}, short_name={short_name}, full_name={full_name},"
               "status=1, valid_until_date='2100-01-01'",
              { "email": user["email"], "short_name": user["name"], "full_name": user["full"] })
      user_id = db.res("SELECT id from main_users where email={email}", { "email": user["email"] })

    roles = []
    # save session
    if user_id:
      db.query("INSERT into main_sessions set user_ip={user_ip}, email={email}, name={name}, full_name={full_name}, "
             "created_date=now(), enabled=1, hash={hash}, user_id={user_id}",
             { "user_ip": request.remote_addr, "email": user["email"], "name": user["name"], "full_name": user["full"], "hash": user["hash"],
              "user_id": user_id } )

    user["id"] = user_id

  return {"user": user}


def do_signout(req):
  """Validates login token with oauth server.

  Args:
    token: login sent from frontend

  Returns:
    object with logged user data
  """
  db.query("UPDATE main_sessions set enabled=0 where hash={hash}")
  return "signout"


def do_login(token):
  """Validates login token with oauth server.

  Args:
    token: login sent from frontend

  Returns:
    object with logged user data
  """
  r = requests.get("https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + token)
  jdata = r.content
  user = {}

  user["email"] = json.loads(jdata)["email"]
  user["name"] = json.loads(jdata)["given_name"]
  user["full"] = json.loads(jdata)["name"]
  user["logged"] = True

  # except:
  #  user["logged"] = False
  return user
