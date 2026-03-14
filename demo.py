import math
import time
import random


class FakeUnit:
    def __init__(self, v):
        self.magnitude = v

    def __str__(self):
        return str(round(self.magnitude, 1))


class FakeResponse:
    def __init__(self, val):
        self.value = FakeUnit(val)

    def is_null(self):
        return False


class DemoConnection:

    status = "demo"

    def __init__(self):
        self._rpm      = 800.0
        self._speed    = 0.0
        self._throttle = 0.0
        self._coolant  = 85.0
        self._intake   = 25.0
        self._load     = 20.0
        self._voltage  = 14.1
        self._maf      = 3.5

    def simulate_drive(self):
        t = time.time()
        self._rpm      = 850  + 400 * abs(math.sin(t * 0.30))
        self._speed    = 40   + 30  * abs(math.sin(t * 0.15))
        self._load     = 20   + 30  * abs(math.sin(t * 0.30))
        self._throttle = 10   + 20  * abs(math.sin(t * 0.30))
        self._maf      = 3.5  + 5   * abs(math.sin(t * 0.30))

    def query(self, cmd_name: str):
        noise = lambda n: random.uniform(-n, n)

        values = {
            "RPM":                    max(650, self._rpm + noise(50)),
            "SPEED":                  max(0,   self._speed + noise(2)),
            "THROTTLE_POS":           max(0,   min(100, self._throttle + noise(1))),
            "COOLANT_TEMP":           self._coolant + noise(0.5),
            "INTAKE_TEMP":            self._intake + noise(0.3),
            "ENGINE_LOAD":            max(0,   min(100, self._load + noise(2))),
            "CONTROL_MODULE_VOLTAGE": self._voltage + noise(0.05),
            "MAF":                    max(0,   self._maf + noise(0.2)),
            "FUEL_LEVEL":             65.0,
            "TIMING_ADVANCE":         12.5 + noise(0.5),
            "SHORT_FUEL_TRIM_1":      noise(2),
            "LONG_FUEL_TRIM_1":       noise(1),
        }

        if cmd_name in values:
            return FakeResponse(values[cmd_name])
        return None
