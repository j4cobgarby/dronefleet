class PidController:
    def __init__(self, kp, ki, kd, setpoint, freq):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint # Target value
        self.timeperiod = 1/freq
        self.err_i = 0 # Error integral (sum of previous errors)
        self.errprev = 0 # Previous error
        self.timeprev = time.time()

    # Performs the PID algorithm with the 'value' parameter as the input
    # reading.
    def compute(self, value):
        t = time.time()
        if t - self.timeprev >= self.timeperiod:
            dt = t - self.timeprev
            self.timeprev = t

            err_p = self.setpoint
            self.err_i += dt * err_p
            err_d = err_p - self.errprev

            self.errprev = err_p

        return self.kp * err_p + self.ki * err_i + self.kd * err_d
