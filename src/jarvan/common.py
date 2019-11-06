"""Get builder form, depending on format.
"""
import os
import random
import time
import zipfile
from jarvan import db
from flask import request


def get_user_id(req):
  """get current user id.

  Args:
    req: flask request

  Returns:
    String user id
  """
  h = req.values.get("hash")

  user_id = db.res(
      "SELECT user_id from sessions where enabled=1 and hash=%s", (h))
  if not user_id:
    user_id = None
  user_id = "57"
  return user_id


def file_put_contents(file_name, content):
  """save content to file.

  Args:
    file_name: local file name
    content: text content to save
  """
  # create dir of not exists
  try:
    os.mkdir(os.path.dirname(file_name))
  except FileExistsError:
    pass

  # write to file. create new or replace
  fh = open(file_name, "w+")
  fh.write(content)
  fh.close()


def file_get_contents(filename):
  """Return the content of a file relative to current dir.

  Args:
    filename: url relative to current file

  Returns:
    File content as String. Empty string if file not found
  """
  try:
    txt = open(filename).read()
  except OSError:
    txt = ""

  return txt


def create_zip(path, zip_filename):
  """save content to file.

  Args:
    path: directory to zip
    zip_filename: full path to new created zip file.

  """
  try:
    ziph = zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(path):
      for file2 in files:
        ziph.write(os.path.join(root, file2),
                   os.path.join(root, file2)[len(path):])

    ziph.close()
    return True
  except zipfile.BadZipFile:
    return False


def get_tmp_file_name():
  """get a random-ish number. used to create temp folders.

  Returns:
    random string of numbers
  """
  out = (str(round(time.time() * 100000)) +
         str(random.randint(10000000, 99999999)))
  return out



def save_file(file, location):
  """Saves a file to a specific location.

  Args:
    file: file to save
    location: destination

  """
  try:
    os.mkdir(os.path.dirname(location))
  except FileExistsError:
    pass
  file.save(location)


def extract_zip(zfile, dir2):
  """Extracts a zipfile into a new dir.

  Args:
    zfile: file to unzip
    dir2: destination

  """
  try:
    delete(dir2)
    os.mkdir(dir2)

    zfile.save(dir2 + "-1.zip")
    zip_ref = zipfile.ZipFile(dir2 + "-1.zip", "r")
    zip_ref.extractall(dir2)
    zip_ref.close()
    os.remove(dir2 + "-1.zip")
    return True
  except zipfile.BadZipFile:
    return False


def delete(top):
  """Deletes a subdir.

  Args:
    top: top level dir to delete
  """
  for root, dirs, files in os.walk(top, topdown=False):
    for name in files:
      os.remove(os.path.join(root, name))
    for name in dirs:
      os.rmdir(os.path.join(root, name))
  if os.path.exists(top):
    os.rmdir(top)


def clean_tmp(dir2):
  """Deletes temp files after a build process.

  Args:
    dir2: top level dir to delete
  """
  delete(dir2)
  try: 
    os.remove(dir2 + "-1.zip")
  except FileNotFoundError:
    pass


def get_int_param(n):
  """Returns payload, post or get parameter value as int.

  Args:
    n: parameter name
  """
  return to_int(get_param(n))


def get_list_param(n):
  """Returns payload, post or get parameter value as String.

  Args:
    n: parameter name
  """
  out = ""
  try:
    out = request.values.getlist(n)
  except KeyError:
    out = ['']
  return out


def get_param(n):
  """Returns payload, post or get parameter value as String.

  Args:
    n: parameter name
  """
  out = ""
  try:
    out = str(request.values[n])
  except KeyError:
    out = ""
  return out


def to_int(s):
  """Converts safely to int. On invalid output, returns 0.

  Args:
    s: String to convert
  """
  i = 0
  try:
    i=int(s)
  except ValueError:
    i = 0
  except TypeError:
    i = 0
  return i


def get_ext(s):
  """Returns extension in lowercase 

  Args:
    s: Filename String
  """
  ext = ""
  try:
    f = s.split(".")
    out = f[len(f)-1].lower()
  except AttributeError:
    out = ""
  return out


def strtoken(st,pos,sep):
  """Splits string and returns splitted substring. Returns "" if None


  Args:
    st: String to split
    pos: Position to return. Can be negative 
    sep: Separator
  """
  out = ""
  s = st.split(sep)
  if len(s) >= abs(pos) and pos != 0:
    if pos > 0:
      out = s[pos-1]
    else:
      out = s[len(s)+pos]
  return out


def get_email():
  email = db.res("select email from main_sessions where hash=%s", (get_param("x-token")))
  return email
