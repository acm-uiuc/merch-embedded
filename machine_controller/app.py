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
token_attr, token_value = open('.env', 'r').read().split("=")
token_value = token_value[:-1]

app = Flask(__name__)
merch = Merch()

@app.route('/vend', methods=['POST'])
def vend():
    if request.headers.get('Authorization', '') != token_value:
        abort(401)
    data = request.json
    items = data['items']
    transaction_id = data['transaction_id']


    statuses = []
    merch.acquire()
    for i, item in enumerate(items):
        try:
            merch.vend(item[0], int(item[1]))
            statuses.append({'error': None, 'location': item})

        except Exception as e:
            # Some error occurred while vending
            # I'd prefer to catch Merch.VendError's only, but if something else
            # goes wrong, we still need to let the client know instead of
            # throwing a 500
            statuses.append({'error': str(e), 'location': item})
    merch.release()

    return jsonify(transaction_id=transaction_id, items=statuses)

@app.route('/status', methods=['GET'])
def status():
    if request.headers.get('Authorization', '') != token_value:
        abort(401)

    notready = merch.inUse()

    if(notready):
        return ('', 503)
    else:
        # 200 to indicate success
        return ('', 200)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', threaded=True)
