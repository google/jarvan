"""Get builder form, depending on format.

Returns:
  Json containing an html

  Args:
    fmt: format name to return. i.e. "html5"
"""
from jarvan import j
import requests
import time
import os

def run(fmt):
  """Module entry point.

  Args:
    fmt: format to return

  Returns:
    Json containing an html
  """
  current_path = os.path.dirname(__file__)
  header = j.file_get_contents(current_path + "/../tpl/header.html")

  return header

