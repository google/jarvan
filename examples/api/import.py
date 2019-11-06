"""Example Service. Access with /api/service.
"""
from jarvan import j
from flask import g


def get():
  g.static = 123
  j.out_json({"some_value": g.static})
