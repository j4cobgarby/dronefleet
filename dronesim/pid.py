import time

class PidController:
    def __init__(self, kp, ki, kd, setpoint, freq, minval, maxval):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.minval = minval
        self.maxval = maxval
        self.setpoint = setpoint # Target value
        self.timeperiod = 1/freq
        self.err_i = 0 # Error integral (sum of previous errors)
        self.errprev = 0 # Previous error
        self.timeprev = time.time()
        self.output = 0

    # Performs the PID algorithm with the 'value' parameter as the input
    # reading.
    def compute(self, value):
        t = time.time()
        if t - self.timeprev >= self.timeperiod:
            dt = t - self.timeprev
            self.timeprev = t

            err_p = self.setpoint - value
            self.err_i += dt * err_p
            err_d = err_p - self.errprev

            self.errprev = err_p

            self.output = self.kp * err_p + self.ki * self.err_i + self.kd * err_d
            self.output = max(min(self.output, self.maxval), self.minval)

        return self.output
