# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

