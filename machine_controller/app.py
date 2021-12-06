# University of Illinois/NCSA Open Source License
#
# Copyright (c) 2017 ACM@UIUC
# All rights reserved.
#
# Developed by:	    SIGBot
#                   ACM@UIUC
#                   https://acm.illinois.edu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# with the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimers.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimers in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the names of the SIGBot, ACM@UIUC, nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this Software without specific prior written permission.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH
# THE SOFTWARE.
from flask import Flask, request, abort, jsonify
import json
from vend import Merch
import signal
import sys
import requests
import configparser
import db

config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('DEFAULT', 'TOKEN', fallback=None)
coinmarketcap_key = config.get('DEFAULT', 'COINMARKETCAP_KEY', fallback=None)

app = Flask(__name__)
merch = Merch(debug=True)

def authenticate(route):
  def authenticator():
    auth_token = request.headers.get('Authorization')
    if not auth_token:
      abort(401)
    if auth_token[:8] != 'Bearer: ':
      abort(401)
    if auth_token[8:] != token:
      abort(401)
    return route()
  authenticator.__name__ = route.__name__
  return authenticator

@app.route('/api', methods=['GET'])
def api():
  return 'MERCH API RUNNING'

@app.route('/api/vend', methods=['POST'])
@authenticate
def vend():
  if 'item' not in request.args:
    abort(400)
  item = request.args['item']
  success = merch.vend(item[0], int(item[1]))
  return (json.dumps({'success': success}), 200,
          {'ContentType': 'application/json'})

@app.route('/api/new_item', methods=['POST'])
@authenticate
def new_item():
  '''Adds an item to the inventory.

  Query Args:
    name: The name of the item to add. Required.
    image_url: The image url of the item to add. Required.
    price: The price in USD cents of the item to add. Integer. Required.
    calories: The number of calories in the item. Integer.
    fat: Grams of fat in the item. Integer.
    carbs: Grams of carbs in the item. Integer.
    fiber: Grams of fiber in the item. Integer.
    sugar: Grams of sugar in the item. Integer.
    protein: Grams of protein in the item. Integer.
  '''
  status = db.insert_item(request.args)
  if status[0]:
    return (json.dumps({'success': True}), 200,
            {'ContentType': 'application/json'})
  else:
    return (json.dumps({'error': status[1]}), 400,
            {'ContentType': 'application/json'})

def json_find(json_data, *args):
  current_layer = json_data
  for arg in args:
    if arg in current_layer:
      current_layer = current_layer[arg]
    else:
      return None
  return current_layer

def current_sol_price():
  url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
  parameters = { 'id': '5426' }
  headers = { 'X-CMC_PRO_API_KEY': coinmarketcap_key }
  raw_response = requests.get(url, params = parameters, headers = headers)
  try:
    json_response = raw_response.json()
    price = json_find(json_response, 'data', '5426', 'quote', 'USD', 'price')
    return price
  except:
    return None

def signal_handler(signal, frame):
  #merch.cleanup()
  sys.exit(0)

if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)
  db.init_db()
  app.run(debug=True, host='0.0.0.0')
