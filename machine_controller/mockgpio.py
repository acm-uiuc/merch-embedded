import copy



class MockGPIO:
    # From https://github.com/TCAllen07/raspi-device-mocks
    # Map format is <BCM-#>: <BOARD-#>
    bcm_board_map = { 2: 3,
            3: 5,   4: 7,   14: 8,  15: 10, 17: 11,
            18: 12, 27: 13,  22: 15, 23: 16, 24: 18,
            10: 19,  9: 21,  25: 22, 11: 23,  8: 24,
            7: 26,  5: 29,   6: 31, 12: 32, 13: 33,
            19: 35, 16: 36,  26: 37, 20: 38, 21: 40}

    # Map format is <BOARD-#>: <BCM-#>
    gpio_board_map = { 3: 2,
            5: 3,   7: 4,   8: 14,  10: 15, 11: 17,
            12: 18, 13: 27,  15: 22, 16: 23, 18: 24,
            19: 10,  21: 9,  22: 25, 23: 11,  24: 8,
            26: 7,  29: 5,   31: 6, 32: 12, 33: 13,
            35: 19, 36: 16,  37: 26, 38: 20, 40: 21}



    LOW = 0
    HIGH = 1

    BCM = 11
    BOARD = 10

    OUT = 0
    IN = 1

    PUD_OFF = 20
    PUD_DOWN = 21
    PUD_UP = 22

    # Indexed by board pin number
    gpio_direction = {k: 1 for k in bcm_board_map.values()}
    gpio_values = {}

    def __init__(self):
        self.mode = -1

        self.setmode_run = False
        self.setup_run = False

        self.states = []



    def setmode(self, mode):
        if mode not in (self.BCM, self.BOARD):
            raise ValueError("An invalid mode was passed to setmode()")
        self.mode = mode
        self.setmode_run = True

    def getmode(self):
        return self.mode


    def __pin_validate(self, pin):
        if self.mode == self.BCM:
            if pin not in self.bcm_board_map.keys():
                raise ValueError('Pin is invalid')
        elif self.mode == self.BOARD:
            if pin not in self.gpio_board_map.keys():
                raise ValueError('Pin is invalid')
        else:
            raise ValueError('Setup has not been called yet')




    def output(self, pins, value):
        if not hasattr(pins, '__iter__'):
            pins = [pins, ]
        for pin in pins:
            self.__pin_validate(pin)

        if value not in (self.HIGH, self.LOW):
            raise ValueError('An invalid value was passed to output()')

        if not self.setmode_run:
            raise RuntimeError('output() was called before setmode()')
        if not self.setup_run:
            raise RuntimeError('output() was called before setup()')

        for pin in pins:
            self.gpio_values[pin] = value
        self.states.append(copy.deepcopy(self.gpio_values))


    def input(self, pins):
        if not hasattr(pins, '__iter__'):
            pins = [pins, ]
        for pin in pins:
            self.__pin_validate(pin)

        if not self.setmode_run:
            raise RuntimeError('input() was called before setmode()')
        if not self.setup_run:
            raise RuntimeError('input() was called before setup()')

    def gpio_function(self, pin):
        self.__pin_validate(pin)
        if not self.setmode_run:
            raise RuntimeError('gpio_function() was called before setmode()')
        if self.mode == self.BCM:
            return self.gpio_direction[self.bcm_board_map[pin]]
        else:
            return self.gpio_direction[pin]

    def cleanup(self):
        self.setup_run = False
        self.setmode_run = False
        self.mode = -1

        for pin in self.gpio_direction:
            self.gpio_direction[pin] = self.IN

    def setup(self, pins, direction, pull_up_down=None, initial=None):
        if not hasattr(pins, '__iter__'):
            pins = [pins, ]

        for pin in pins:
            self.__pin_validate(pin)

        if direction not in (self.IN, self.OUT):
            raise ValueError('An invalid direction was passed to setup()')
        if (pull_up_down is not None and
                pull_up_down not in (self.PUD_OFF, self.PUD_DOWN, self.PUD_UP)):
            raise ValueError('Invalid Pull Up Down setting passed to setup()')
        self.setup_run = True
        if self.mode == self.BCM:
            self.gpio_direction[self.bcm_board_map[pin]] = direction
        else:
            self.gpio_direction[pin] = direction


    # Placeholders
    def add_event_callback(self, *args):
        pass

    def add_event_detect(self, *args):
        pass

    def setwarnings(self, *args):
        pass

    def wait_for_edge(self, *args):
        pass

    def event_detected(self, *args):
        pass

    def remove_event_detect(self, *args):
        pass


GPIO = MockGPIO()
