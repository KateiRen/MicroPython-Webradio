from machine import Pin

STATE_LOCKED = 0
STATE_TURN_RIGHT_START = 1
STATE_TURN_RIGHT_MIDDLE = 2
STATE_TURN_RIGHT_END = 3
STATE_TURN_LEFT_START = 4
STATE_TURN_LEFT_MIDDLE = 5
STATE_TURN_LEFT_END = 6
STATE_UNDECIDED = 7


class RotaryEncoder():
    def __init__(self, pin_btn, pin_s1, pin_s2):
        self.s1 = Pin(pin_s1, Pin.IN)
        self.s2 = Pin(pin_s2, Pin.IN)
        self.btn = Pin(pin_btn, Pin.IN)
        # self.name = name
        self.state = STATE_LOCKED

    def read(self):
        return (self.s1.value(), self.s2.value(), self.btn.value())

    def buttonIsPressed(self):
        return not self.btn.value()  # geht beim Drücken auf GND

    def evalState(self, cbIncrease, cbDecrease, cbButtonPress):
        # Prinzip des endlichen Automaten übernommen aus c't 18/2020 "Arduino als Media-Tastatur" von Pina Merkert https://github.com/pinae
        s1, s2, s = self.read()
        if self.state == STATE_LOCKED:
            if s2 and s1:
                self.state = STATE_UNDECIDED
            elif not s2 and s1:
                self.state = STATE_TURN_LEFT_START
            elif s2 and not s1:
                self.state = STATE_TURN_RIGHT_START
            else:
                self.state = STATE_LOCKED
        elif self.state == STATE_TURN_RIGHT_START:
            if s2 and s1:
                self.state = STATE_TURN_RIGHT_MIDDLE
            elif not s2 and s1:
                self.state = STATE_TURN_RIGHT_END
            elif s2 and not s1:
                self.state = STATE_TURN_RIGHT_START
            else:
                self.state = STATE_LOCKED
        elif self.state == STATE_TURN_RIGHT_MIDDLE or self.state == STATE_TURN_RIGHT_END:
            if s2 and s1:
                self.state = STATE_TURN_RIGHT_MIDDLE
            elif not s2 and s1:
                self.state = STATE_TURN_RIGHT_END
            elif s2 and not s1:
                self.state = STATE_TURN_RIGHT_START
            else:
                self.state = STATE_LOCKED
                cbIncrease()
        elif self.state == STATE_TURN_LEFT_START:
            if s2 and s1:
                self.state = STATE_TURN_LEFT_MIDDLE
            elif not s2 and s1:
                self.state = STATE_TURN_LEFT_START
            elif s2 and not s1:
                self.state = STATE_TURN_LEFT_END
            else:
                self.state = STATE_LOCKED
        elif self.state == STATE_TURN_LEFT_MIDDLE or self.state == STATE_TURN_LEFT_END:
            if s2 and s1:
                self.state = STATE_TURN_LEFT_MIDDLE
            elif not s2 and s1:
                self.state = STATE_TURN_LEFT_START
            elif s2 and not s1:
                self.state = STATE_TURN_LEFT_END
            else:
                self.state = STATE_LOCKED
                cbDecrease()
        elif self.state == STATE_UNDECIDED:
            if s2 and s1:
                self.state = STATE_UNDECIDED
            elif not s2 and s1:
                self.state = STATE_TURN_RIGHT_END
            elif s2 and not s1:
                self.state = STATE_TURN_LEFT_END
            else:
                self.state = STATE_LOCKED
        # Wenn cb übergeben, dann machen wir das natürlich...
        if callable(cbButtonPress) and not s:
            while not self.btn.value():
                continue
            cbButtonPress()
