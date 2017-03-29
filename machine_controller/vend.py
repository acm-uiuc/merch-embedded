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


class Merch:
    '''Merch Hardware Controller'''
    CLOCK = 26
    ROW = [21, 20, 16]
    COL = [19, 13]
    MAX_LETTER = 'F'
    MAX_NUMBER = '0'

    def __init__(self, debug=False):
        self.debug = debug

        self.__setup()
        self.__low()
        self.__commit()

    def __del__(self):
        self.__cleanup()

    def __cleanup(self):
        ''' Clean up all of the GPIO pins '''
        GPIO.cleanup()

    def __setup(self):
        ''' Setup all of the GPIO pins '''
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.CLOCK, GPIO.OUT, initial=GPIO.LOW)
        for row in self.ROW:
            GPIO.setup(row, GPIO.OUT, initial=GPIO.LOW)
        for col in self.COL:
            GPIO.setup(col, GPIO.OUT, initial=GPIO.LOW)

    def __low(self):
        ''' Writes all outputs to low. Does not commit them '''
        GPIO.output(self.CLOCK, GPIO.LOW)

        for row in self.ROW:
            GPIO.output(row, GPIO.LOW)
        for col in self.COL:
            GPIO.output(col, GPIO.LOW)

    def __commit(self):
        '''
        Clocks the flip flop that gates the output
        '''
        GPIO.output(self.CLOCK, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.CLOCK, GPIO.LOW)
        self.__low()

    # Wrap the base _vend function, which doesn't check arguments
    def vend(self, letter, number):
        ''' Presses the keypad with letter, number'''
        char = 0
        try:
            char = ord(letter)
        except TypeError:
            raise TypeError('Letter %s does not represent a character' %
                            str(letter))

        # Maybe we should use the actual keypad value?
        if char < ord('A') or char > ord('Z'):
            raise ValueError('Invalid Letter: %s' % str(letter))

        num = 0
        try:
            num = int(number)
        except TypeError:
            raise TypeError('Number %s is not convertible to an integer' %
                            str(num))

        if num < 0 or num > 10:
            raise ValueError('Number %d is not in the range 1-10' % num)

        self.__vend(letter, str(number))

    def __vend(self, letter, number):
        ''' Base vending function that handles GPIO's

        Arguments:
        letter -- the letter as a length 1 string
        number -- the digit as a string between 0-10
        '''
        self.__sendKey(letter)
        self.__sendKey(number)
        self.__commit()

    def __sendKey(self, key):
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

        keys = {
                'A':   (0b000, 0b011),
                'B':   (0b001, 0b011),
                'C':   (0b010, 0b011),
                'D':   (0b011, 0b011),
                'E':   (0b100, 0b011),
                'F':   (0b101, 0b011),

                '1':   (0b000, 0b001),
                '2':   (0b000, 0b010),
                '3':   (0b001, 0b001),
                '4':   (0b001, 0b010),
                '5':   (0b010, 0b001),
                '6':   (0b010, 0b010),
                '7':   (0b011, 0b001),
                '8':   (0b011, 0b010),
                '9':   (0b100, 0b001),
                '0':   (0b100, 0b010),
                '*':   (0b100, 0b001),
                'CLR': (0b100, 0b010),
        }

        letter_key = keys[key]
        if letter_key[0] & 0b100:
            GPIO.output(self.ROW[0], GPIO.HIGH)
        if letter_key[0] & 0b010:
            GPIO.output(self.ROW[1], GPIO.HIGH)
        if letter_key[0] & 0b001:
            GPIO.output(self.ROW[2], GPIO.HIGH)

        if letter_key[1] & 0b10:
            GPIO.output(self.COL[0], GPIO.HIGH)
        if letter_key[1] & 0b01:
            GPIO.output(self.COL[1], GPIO.HIGH)

        if self.debug:
            print('Vending', letter_key[0], letter_key[1])

        self.__commit()


