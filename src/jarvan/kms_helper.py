from flask import request
from google.cloud import kms_v1
import base64
import os
import json
import glob

def decrypt(c):
  print(c)
  print("-------------------")
  client = kms_v1.KeyManagementServiceClient()
  name = client.crypto_key_path_path(
    c["project_id"], c["location_id"], c["key_ring_id"], c["crypto_key_id"])

  enable_file_cache = True

  if enable_file_cache:

    from datetime import datetime
    cache_time =  datetime.now().strftime("%Y%m%d_%H")

    filename = "/tmp/"+c["project_id"]+"_"+c["location_id"]+"_"+c["key_ring_id"]+"_"+c["crypto_key_id"]
    data = {}
    # try to find file content cached in /tmp

    ## delete old cache files
    fileList = glob.glob(filename+"_*")
    for file_path in fileList:
      try:
        if file_path!=(filename + "_"+cache_time):
          os.remove(file_path)
      except:
        pass

    try:
      content=open(filename + "_"+cache_time, "r").read()

      data = json.loads(content)
      if c["secret"] in data:
        return data[c["secret"]]
    except json.decoder.JSONDecodeError:
      os.remove(filename + "_"+cache_time)
    except FileNotFoundError:
      pass

    out = client.decrypt(name, base64.b64decode(c["secret"])).plaintext.decode("utf-8")

    file = open(filename + "_"+cache_time, 'w')
    data[c["secret"]] = out
    file.write(json.dumps(data))
    file.close()

  else:
    out = client.decrypt(name, base64.b64decode(c["secret"])).plaintext.decode("utf-8")
  
  return out


def encrypt(c):
  client = kms_v1.KeyManagementServiceClient()
  name = client.crypto_key_path_path(
    c["project_id"], c["location_id"], c["key_ring_id"], c["crypto_key_id"])
  encr = client.encrypt(name, c["secret"].encode("utf-8")).ciphertext
  return base64.b64encode(encr).decode("utf-8")


def test(action, data):
  global project_id, location_id, key_ring_id, crypto_key_id, client, name

  out = ""
  if action == "encrypt":
    out = encrypt(data)

  elif action == "decrypt":
    out = decrypt(data)

  else:
    out = """
  Source (Secret or encoded base64):
<FORM name=form1 method=POST target='out' action='/kms'>
  <INPUT NAME='action' TYPE='HIDDEN'>
  <TEXTAREA name='data' style='width:800px;height:300px'></TEXTAREA>
  <BR/>
  <INPUT VALUE='Encode' type=button onclick='encrypt()'>
  <INPUT VALUE='Decode' type=button onclick='decrypt()'>
</FORM>
<BR/>
Encoded base64
<BR/>
<IFRAME name='out' style='width:800px;height:300px'></IFRAME>
<script>
function encrypt() {
  document.form1.action.value='encrypt';
  document.form1.submit();
}
function decrypt(){
  document.form1.action.value='decrypt';
  document.form1.submit();
}
</script>
  """

  return out 
