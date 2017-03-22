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
import RPi.GPIO as GPIO
import time
import sys

CLOCK = 21
ROW = [26, 16, 20]
COL = [19, 13]

GPIO.setmode(GPIO.BCM)

app = Flask(__name__)

@app.route('/vend', methods=['POST'])
def hello_world():
    if 'item' not in request.args:
        abort(400)
    item = request.args['item']
    vend(item[0], item[1])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

def setup():
    GPIO.setup(CLOCK, GPIO.OUT, initial=GPIO.LOW)
    for row in ROW:
        GPIO.setup(row, GPIO.OUT, initial=GPIO.LOW)
    for col in COL:
        GPIO.setup(col, GPIO.OUT, initial=GPIO.LOW)

def LOW():
    GPIO.output(CLOCK, GPIO.LOW)

    for row in ROW:
        GPIO.output(row, GPIO.LOW)
    for col in COL:
        GPIO.output(col, GPIO.LOW)

def commit():
    GPIO.output(CLOCK, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(CLOCK, GPIO.LOW)
    LOW()

def vend(letter, number):
    # Set the letter
    binary = ord(letter) - ord('A')
    if(binary & 0b100):
        GPIO.output(ROW[0], GPIO.HIGH)
    if(binary & 0b010):
        GPIO.output(ROW[1], GPIO.HIGH)
    if(binary & 0b001):
        GPIO.output(ROW[2], GPIO.HIGH)

    GPIO.output(COL[0], GPIO.HIGH)
    GPIO.output(COL[1], GPIO.HIGH)

    commit()


    # Set the number
    row = (number-1) / 2
    col = (number+1) % 2+1

    if(col & 0b01):
        GPIO.output(COL[1], GPIO.HIGH)
    if(col & 0b10):
        GPIO.output(COL[0], GPIO.HIGH)

    if(row & 0x100):
        GPIO.output(ROW[0], GPIO.HIGH)
    if(row & 0b010):
        GPIO.output(ROW[1], GPIO.HIGH)
    if(row & 0b001):
        GPIO.output(ROW[2], GPIO.HIGH)

    commit()
    commit()

def reject(bad_position):
    print("%s is not a valid character" % bad_position)

if __name__ == '__main__':
    setup()
    LOW()
    commit()
    app.run(debug=True)