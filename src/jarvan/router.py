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
import os
from jarvan import j
from jarvan import login


def run(file, request, _obj, _met=""):
  #j.set_up(request)
  
  if not _met:
    _met = request.method.lower() 

  #print("len(_url):"+str(len(_url)))
  #print("_obj:"+_obj)
  #print("_met:"+_met)

 # return os.path.dirname(os.path.realpath(file))+"/api/"+_obj+".py"
  if(os.path.isfile(os.path.dirname(os.path.realpath(file))+"/api/"+_obj+".py")): 
    m = __import__ ("api."+_obj, fromlist=["api"])
    
#    try:
    func = getattr(m, _met)
    
    func()
    out = j.out_get()
#    except AttributeError:
#      out = "METHOD NOT FOUND: " + _met

  elif _obj == "login":
    out = login.run(request, _met)  

  else:
    out = "OBJECT NOT FOUND:" + _obj + "." + _met

  return out
