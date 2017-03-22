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
# of this software and associated documentation files (the 'Software'), to deal
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
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH
# THE SOFTWARE.
import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)

CLOCK = 26
ROW = [21, 20, 16]
COL = [19, 13]

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


def reject(bad_position):
    print("%s is not a valid character" % bad_position)

def main():
    char = sys.argv[1][0]
    num = sys.argv[1][1]
    
    setup()
    LOW()
    commit()

    vend(char, int(num))
    GPIO.cleanup()

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
    row = int((number-1) / 2)
    col = (number+1) % 2+1

    if(col & 0b01):
        GPIO.output(COL[1], GPIO.HIGH)
    if(col & 0b10):
        GPIO.output(COL[0], GPIO.HIGH)

    print(row, col)

    if(row & 0x100):
        GPIO.output(ROW[0], GPIO.HIGH)
    if(row & 0b010):
        GPIO.output(ROW[1], GPIO.HIGH)
    if(row & 0b001):
        GPIO.output(ROW[2], GPIO.HIGH)

    commit()
    commit()


# TABLE OF OUTPUTS
# ROW = {ROW[0],ROW[1],ROW[2]}
# COL = {COL[0], COL[1]}
# ROW   COL    OUTPUT
# 000   11     A
# 000   01     1
# 000   10     2
# 001   11     B
# 001   01     3
# 001   10     4
# 010   11     C
# 010   01     5
# 010   10     6
# 011   11     D
# 011   01     7
# 011   10     8
# 100   11     E
# 100   01     9
# 100   10     0
# 101   11     F
# 101   01     *
# 101   10     CLR

if __name__ == "__main__":
    main()