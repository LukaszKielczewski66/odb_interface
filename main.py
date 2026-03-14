import tkinter as tk
from app import MercedesOBD2App

try:
    import obd
    OBD_AVAILABLE = True
except ImportError:
    OBD_AVAILABLE = False


def main():
    root = tk.Tk()
    app  = MercedesOBD2App(root)

    app._log_console("=" * 54)
    app._log_console("  Mercedes W204 · 1.8 CGI · OBD2 Diagnostics")
    app._log_console("=" * 54)

    if not OBD_AVAILABLE:
        app._log_console("")
        app._log_console("⚠  BRAK BIBLIOTEKI 'obd'!")
        app._log_console("   Zainstaluj ją poleceniem:")
        app._log_console("     pip install obd pyserial")
        app._log_console("")
        app._log_console("   Możesz już teraz korzystać z trybu DEMO.")
    else:
        app._log_console("✓ Biblioteka python-obd gotowa")
        app._log_console("")
        app._log_console("Jak połączyć adapter ELM327:")
        app._log_console("  1. Włóż adapter do gniazda OBD2 (pod kierownicą)")
        app._log_console("  2. Włącz zapłon (pozycja II) lub odpal silnik")
        app._log_console("  3. Podłącz USB do laptopa")
        app._log_console("  4. Kliknij POŁĄCZ – port wykryje się automatycznie")

    app._log_console("")
    app._log_console("Kliknij DEMO aby przetestować bez adaptera.")
    app._log_console("")

    root.mainloop()


if __name__ == "__main__":
    main()
