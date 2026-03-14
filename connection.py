import threading
import time
from datetime import datetime

try:
    import obd
    OBD_AVAILABLE = True
except ImportError:
    OBD_AVAILABLE = False


OBD_COMMANDS = [
    ("RPM",                    "rpm"),
    ("SPEED",                  "speed"),
    ("COOLANT_TEMP",           "cool"),
    ("ENGINE_LOAD",            "load"),
    ("THROTTLE_POS",           "throt"),
    ("CONTROL_MODULE_VOLTAGE", "volt"),
    ("MAF",                    "maf"),
    ("INTAKE_TEMP",            "intake"),
    ("TIMING_ADVANCE",         "timing"),
    ("SHORT_FUEL_TRIM_1",      "stft"),
    ("LONG_FUEL_TRIM_1",       "ltft"),
    ("FUEL_LEVEL",             "fuel"),
]

POLL_INTERVAL = 0.25


class OBDManager:

    def __init__(self, on_data=None, on_log=None, on_status=None):
        self._conn      = None
        self._thread    = None
        self._running   = False
        self._demo_mode = False

        self.on_data   = on_data
        self.on_log    = on_log
        self.on_status = on_status

        self.log_entries = []


    def connect(self):
        if not OBD_AVAILABLE:
            self._log("✗ Brak biblioteki 'obd'. Zainstaluj: pip install obd pyserial")
            self._status("Brak biblioteki", "danger")
            return False

        self._log("► Skanuję porty w poszukiwaniu adaptera ELM327...")

        ports = obd.scan_serial()
        if ports:
            self._log(f"  Znalezione porty: {', '.join(ports)}")
        else:
            self._log("  ⚠ Nie znaleziono żadnych portów szeregowych.")
            self._log("    Sprawdź czy adapter jest podłączony i czy zapłon jest włączony.")

        try:
            conn = obd.OBD(fast=False, timeout=10)

            if conn.is_connected():
                self._conn      = conn
                self._demo_mode = False
                proto = conn.protocol_name()
                port  = conn.port_name()
                self._log(f"✓ Połączono!")
                self._log(f"  Port:     {port}")
                self._log(f"  Protokół: {proto}")
                self._log(f"  (Mercedes W204 używa ISO 15765-4 CAN)")
                self._status("POŁĄCZONY", "accent3")
                self._start_polling()
                return True
            else:
                self._log("✗ Nie udało się połączyć.")
                self._log("  Upewnij się że:")
                self._log("  1. Adapter jest w gnieździe OBD2 (pod kierownicą)")
                self._log("  2. Zapłon jest włączony (pozycja II lub odpalony silnik)")
                self._log("  3. Adapter ELM327 jest poprawnie zainstalowany")
                self._status("Błąd połączenia", "danger")
                return False

        except Exception as e:
            self._log(f"✗ Wyjątek podczas łączenia: {e}")
            self._status("Błąd", "danger")
            return False

    def connect_demo(self):
        from demo import DemoConnection
        self._conn      = DemoConnection()
        self._demo_mode = True
        self._log("► Uruchomiono tryb DEMO (dane symulowane)")
        self._log("  Możesz testować GUI bez adaptera OBD2.")
        self._status("DEMO", "warn")
        self._start_polling()

    def disconnect(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self._conn and not self._demo_mode and hasattr(self._conn, "close"):
            try:
                self._conn.close()
            except Exception:
                pass
        self._conn = None
        self._log("■ Rozłączono")
        self._status("Niepołączony", "danger")

    def is_connected(self):
        return self._conn is not None and self._running

    def read_dtc(self):
        if self._demo_mode:
            return [
                ("P0300", "Przypadkowe chybienie zapłonu (random misfire)"),
                ("P0171", "Mieszanka uboga – bank 1 (system too lean)"),
                ("P0507", "Obroty biegu jałowego zbyt wysokie"),
                ("C1000", "ABS – błąd czujnika koła przedniego lewego"),
            ]
        if not OBD_AVAILABLE or not self._conn:
            return None
        try:
            resp = self._conn.query(obd.commands.GET_DTC)
            if resp and not resp.is_null():
                return list(resp.value)
            return []
        except Exception as e:
            self._log(f"✗ Błąd odczytu DTC: {e}")
            return None

    def clear_dtc(self):
        if self._demo_mode:
            return True
        if not OBD_AVAILABLE or not self._conn:
            return False
        try:
            self._conn.query(obd.commands.CLEAR_DTC)
            return True
        except Exception as e:
            self._log(f"✗ Błąd kasowania DTC: {e}")
            return False

    def _start_polling(self):
        self._running = True
        self._thread  = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        while self._running:
            try:
                if self._demo_mode:
                    self._conn.simulate_drive()

                data = {}
                for cmd_name, key in OBD_COMMANDS:
                    try:
                        if self._demo_mode:
                            resp = self._conn.query(cmd_name)
                        else:
                            cmd  = getattr(obd.commands, cmd_name, None)
                            resp = self._conn.query(cmd) if cmd else None

                        if resp and not resp.is_null():
                            data[key] = resp.value.magnitude
                    except Exception:
                        pass

                if data and self.on_data:
                    self.on_data(data)

                entry = {"ts": datetime.now().isoformat(), **data}
                self.log_entries.append(entry)

                time.sleep(POLL_INTERVAL)

            except Exception as e:
                self._log(f"✗ Błąd w pętli odczytu: {e}")
                time.sleep(1)

    def _log(self, msg):
        if self.on_log:
            self.on_log(msg)

    def _status(self, text, color_key):
        if self.on_status:
            self.on_status(text, color_key)
