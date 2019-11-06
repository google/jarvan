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
