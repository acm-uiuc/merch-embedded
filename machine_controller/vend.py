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


on_rpi = False
try:
    import RPi.GPIO as GPIO
    import VL53L0X_rasp_python.python.VL53L0X as VL53L0X
    on_rpi = True
except Exception:
    print("Not running on an RPi, vending disabled!")
    on_rpi = False
import time
import numpy as np


class Merch:
    """Merch Hardware Controller"""

    CLOCK = 6
    ROW = [13, 19, 26]
    COL = [16, 5]
    MAX_LETTER = "F"
    MAX_NUMBER = "0"
    SENSOR_TIMING = 100
    SENSOR_TIMING_THRESHOLD = 2
    SENSOR_THRESHOLD = 100
    TIMEOUT_THRESHOLD = 15
    DOOR_PIN = 20
    LIMIT_X_PIN = 23
    LIMIT_Y_PIN = 24

    def __init__(self, debug=False):
        self.debug = debug
        self.__setup_gpio()
        self.__setup_sensor()
        self.__low()
        self.__commit()

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        """Clean up all of the GPIO pins"""
        GPIO.cleanup()

    def __setup_gpio(self):
        """Setup all of the GPIO pins"""
        if self.debug:
            print("Setting up PAD GPIO")
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.CLOCK, GPIO.OUT, initial=GPIO.LOW)
        for row in self.ROW:
            GPIO.setup(row, GPIO.OUT, initial=GPIO.LOW)
        for col in self.COL:
            GPIO.setup(col, GPIO.OUT, initial=GPIO.LOW)

        if self.debug:
            print("Setting up DOOR GPIO")
        GPIO.setup(self.DOOR_PIN, GPIO.OUT, initial=GPIO.HIGH)

        if self.debug:
            print("Setting up LIMIT GPIO")
        GPIO.setup(self.LIMIT_X_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.LIMIT_Y_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __setup_sensor(self):
        if self.debug:
            print("Setting up Range Finder")
        self.cup_sensor = VL53L0X.VL53L0X()
        self.cup_sensor.start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        self.cup_sensor_timing = self.cup_sensor.get_timing()
        if self.cup_sensor_timing < 20000:
            self.cup_sensor_timing = 20000

    def __low(self):
        """Writes all outputs to low. Does not commit them"""
        if self.debug:
            print("Set GPIO low")
        GPIO.output(self.CLOCK, GPIO.LOW)

        for row in self.ROW:
            GPIO.output(row, GPIO.LOW)
        for col in self.COL:
            GPIO.output(col, GPIO.LOW)

        GPIO.output(self.DOOR_PIN, GPIO.HIGH)

    def __commit(self):
        """
        Clocks the flip flop that gates the output
        """
        if self.debug:
            print("Setting up commit GPIO")
        GPIO.output(self.CLOCK, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.CLOCK, GPIO.LOW)
        self.__low()

    def __detect_in_cup(self, direction):
        count = 0
        for t in range(self.SENSOR_TIMING):
            dist = self.cup_sensor.get_distance()
            if self.debug:
                print(dist)
            if direction == "awaiting delivery":
                print("awaiting delivery")
                if dist < self.SENSOR_THRESHOLD:
                    count += 1
            elif direction == "awaiting removal":
                print("awaiting removal")
                if dist >= self.SENSOR_THRESHOLD:
                    count += 1
            if self.debug:
                print("count:" + str(count))
            if count > self.SENSOR_TIMING_THRESHOLD:
                return True
        return False

    def __is_home(self):
        if not GPIO.input(self.LIMIT_Y_PIN) and not GPIO.input(self.LIMIT_X_PIN):
            return True
        return False

    def notify_machine_is_empty(self):
        if self.debug:
            print("Notifying machine that the item is removed")
        GPIO.output(self.DOOR_PIN, GPIO.HIGH)

    def notify_machine_is_full(self):
        if self.debug:
            print("Notifying machine that a item is present")
        GPIO.output(self.DOOR_PIN, GPIO.LOW)

    # Wrap the base _vend function, which doesn't check arguments
    def vend(self, letter, number):
        """Presses the keypad with letter, number"""
        char = 0
        try:
            char = ord(letter)
        except TypeError:
            raise TypeError("Letter %s does not represent a character" % str(letter))

        # Maybe we should use the actual keypad value?
        if char < ord("A") or char > ord("Z"):
            raise ValueError("Invalid Letter: %s" % str(letter))

        num = 0
        try:
            num = int(number)
        except TypeError:
            raise TypeError("Number %s is not convertible to an integer" % str(num))

        if num < 0 or num > 10:
            raise ValueError("Number %d is not in the range 1-10" % num)

        if self.debug:
            print("Vending {},{}".format(letter, str(number)))

        self.__vend(letter, str(number))

        timeout = 0
        detected_transfer = False
        while not detected_transfer:
            detected_transfer = self.__detect_in_cup("awaiting delivery")
            print("Waiting for Cup")
            print(detected_transfer)
            if self.__vend_fail():
                self.__low()
                return False
            if timeout >= self.TIMEOUT_THRESHOLD:
                self.__low()
                return False
            timeout += 1

        if self.debug:
            print("Detected successful transfer")
        self.notify_machine_is_full()

        timeout = 0
        detected_removal = False
        while not detected_removal:
            detected_removal = self.__detect_in_cup("awaiting removal")
            if self.__vend_fail():
                self.__low()
                return False
            if timeout >= self.TIMEOUT_THRESHOLD:
                self.__low()
                return False

        if self.debug:
            print("Detected successful removal")

        self.notify_machine_is_empty()

        return True

    def __vend(self, letter, number):
        """Base vending function that handles GPIO's

        Arguments:
        letter -- the letter as a length 1 string
        number -- the digit as a string between 0-10
        """
        self.__sendKey(letter)
        self.__sendKey(number)
        self.__commit()

    def __vend_fail(self):
        return False

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
            "A": (0b000, 0b011),
            "B": (0b001, 0b011),
            "C": (0b010, 0b011),
            "D": (0b011, 0b011),
            "E": (0b100, 0b011),
            "F": (0b101, 0b011),
            "1": (0b000, 0b001),
            "2": (0b000, 0b010),
            "3": (0b001, 0b001),
            "4": (0b001, 0b010),
            "5": (0b010, 0b001),
            "6": (0b010, 0b010),
            "7": (0b011, 0b001),
            "8": (0b011, 0b010),
            "9": (0b100, 0b001),
            "0": (0b100, 0b010),
            "*": (0b100, 0b001),
            "CLR": (0b100, 0b010),
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

        self.__commit()