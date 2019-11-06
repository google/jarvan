"""Frontend for Smartsheet.

Updates gPS data through smartsheet API every 10 minutes
"""
import json
import logging
import os
from api import homepage
from flask import Flask
from flask import request
from jarvan import db
from jarvan import router

 
app = Flask(__name__)
app.debug = True


@app.before_request
def before_request():
  dir_path = os.path.dirname(os.path.realpath(__file__))
  credentials_json = open(dir_path + "/credentials.json").read()
  db.open_connection(json.loads(credentials_json))

  app.logger.addHandler(logging.StreamHandler())
  app.logger.setLevel(logging.INFO)


@app.route("/api/<module>", methods=["GET", "POST"])
@app.route("/api/<module>/<action>", methods=["GET", "POST"])
def api(module, action=None):
  return router.run(__file__, request, module, action)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
  """Get home page html.

  Returns:
    Home page HTML

  Args:
    path: catch-all path
  """
  out = homepage.run(path)
  return out

