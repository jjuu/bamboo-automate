from lxml import html
import json
import logging
import re
import urllib
import urllib2

logging.basicConfig(level=logging.DEBUG)

class Connection:
  def __init__(self, hostname, baseurl, opener, auth_cookies):
    self.host = hostname
    self.opener = opener
    self.auth_cookies = auth_cookies
    self.baseurl = baseurl

def get_ui_return_html(conn, path, params):
  res, _, _ = request(conn, "GET", path, params, [], urllib.urlencode, html.parse)
  return res

def get_ui_return_json(conn, path, params):
  headers = [('Accept', 'application/json')]
  res, _, _ = request(conn, "GET", path, params, headers, urllib.urlencode, json.load)
  return res

def post_ui_no_return(conn, path, params):
  res,_ , _ = request(conn, "POST", path, params, [], urllib.urlencode, id)

def post_ui_return_html(conn, path, params):
  res, _, _ = request(conn, "POST", path, params, [], urllib.urlencode, html.parse)
  return res

def post_ui_return_json(conn, path, params):
  headers = [('Accept', 'application/json')]
  res, _, _ = request(conn, "POST", path, params, headers, urllib.urlencode, json.load)
  return res

def request(conn, method, path, params, headers, param_parse_func, response_parse_func):
  path_and_params = None
  if method == "GET":
    path_and_params = path+'?'+urllib.urlencode(params) if params else path
  else:
    path_and_params = path

  req = urllib2.Request(conn.host+path_and_params)
  logging.debug('%s', req.get_method())
  for key, value in headers:
    req.add_header(key, value)

  cookies = []
  for c in conn.auth_cookies:
    cookies.append(c.name+'='+c.value.strip())

  cookies = '; '.join(cookies)
  if len(cookies) > 0:
    req.add_header('Cookie', cookies)

  if method == "POST":
    response = conn.opener.open(req, param_parse_func(params))
  elif method == "GET":
    response = conn.opener.open(req)

  logging.debug('%s %s', response.geturl(), response.getcode())
  res = response_parse_func(response)

  return res, response.geturl(), response.getcode()
