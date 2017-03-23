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
import unittest

from vend import Merch


keys_map = {
    0b000: {0b11: 'A', 0b01: '1', 0b10: '2'},
    0b001: {0b11: 'B', 0b01: '3', 0b10: '4'},
    0b010: {0b11: 'C', 0b01: '5', 0b10: '6'},
    0b011: {0b11: 'D', 0b01: '7', 0b10: '8'},
    0b100: {0b11: 'E', 0b01: '9', 0b10: '0'},
    0b101: {0b11: 'F', 0b01: '*', 0b10: 'CLR'},
}

def stateToKey(state):
    '''Convert a state to a key press'''

    row_binary = ((0b100 * state[Merch.Instance().ROW[0]]) +
                  (0b010 * state[Merch.Instance().ROW[1]]) +
                  (0b001 * state[Merch.Instance().ROW[2]]))
    col_binary = ((0b01 * state[Merch.Instance().COL[1]]) +
                  (0b10 * state[Merch.Instance().COL[0]]))

    if not state[Merch.Instance().GATE]:
        return None

    try:
        key = keys_map[row_binary][col_binary]
    except:
        key = None

    return key

def zeroed(state):
    for pin in Merch.Instance().ROW + Merch.Instance().COL:
        if state[pin] != 0:
            return False
    return True



class MerchTestCase(unittest.TestCase):
    def setUp(self):
        self.merch = Merch.Instance()
        self.merch.testing = True

    def tearDown(self):
        self.app.merch.queue.shutdown()

    def test_vend(self):
        self.merch.vend('F', 4)
        self.merch.wait()

        new_states = []
        for state in self.merch.GPIO.states:
            if state[self.merch.GATE]:
                new_states.append(state)

        # Validate vend sequence
        # 1. Zero everything
        self.assertTrue(zeroed(new_states[0]))

        # 2. Press 'F'
        self.assertEqual(stateToKey(new_states[1]), 'F')

        # 3. Press '4'
        self.assertEqual(stateToKey(new_states[2]), '4')

    def test_vend_bad_char(self):
        with self.assertRaises(ValueError):
            self.merch.vend(chr(ord('a') - 1), 0)

        with self.assertRaises(ValueError):
            self.merch.vend(chr(ord(Merch.Instance().MAX_LETTER) + 1), 0)

        with self.assertRaises(ValueError):
            self.merch.vend(chr(ord('A') - 1), 0)

        with self.assertRaises(TypeError):
            self.merch.vend('50', 0)

        with self.assertRaises(TypeError):
            self.merch.vend(50, 0)

    def test_vend_bad_digit(self):
        with self.assertRaises(ValueError):
            self.merch.vend('A', -1)

        with self.assertRaises(ValueError):
            self.merch.vend('A', 'this is not an integer')

        with self.assertRaises(ValueError):
            self.merch.vend('A', Merch.Instance().MAX_NUMBER + 1)

if __name__ == '__main__':
    unittest.main()
