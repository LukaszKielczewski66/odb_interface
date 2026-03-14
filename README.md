# 🚗 Mercedes W204 OBD2 Diagnostics

Aplikacja diagnostyczna w Pythonie inspirowana Torque Pro — live dane silnika, wykresy, odczyt i kasowanie kodów błędów DTC.

Stworzona z myślą o **Mercedes W204 1.8 CGI (2011)**, działa z każdym autem z gniazdem OBD2.

---

![odb.png](..%2F..%2Fodb.png)

---

## Funkcje

- **Wskaźniki** — okrągłe gauge'e RPM, prędkość, temperatura, obciążenie silnika
- **Paski** — 12 parametrów z live wartościami i kolorowymi progami ostrzeżeń
- **Wykresy** — historia ostatnich ~30 sekund dla 6 kluczowych parametrów
- **Błędy DTC** — odczyt i kasowanie kodów błędów OBD2
- **Zapis logów** — eksport sesji do pliku JSON
- **Tryb DEMO** — symulacja jazdy bez adaptera (do testowania)

## Wymagania

- Python 3.8+
- Adapter ELM327 (USB lub Bluetooth) — ~30–80 zł na Allegro

## Instalacja

```bash
git clone https://github.com/twoj-login/mercedes-obd2
cd mercedes-obd2
pip install -r requirements.txt
python main.py
```

## Struktura projektu

```
mercedes_obd2/
├── main.py          # punkt startowy
├── app.py           # GUI, zakładki, obsługa przycisków
├── connection.py    # logika OBD2, auto-detekcja portu, DTC
├── widgets.py       # Gauge, BarGraph, MiniGraph
├── demo.py          # symulacja danych bez adaptera
├── theme.py         # kolory i czcionki
└── requirements.txt
```

## Jak podłączyć

1. Włóż adapter ELM327 do gniazda OBD2 (pod kierownicą, lewa strona)
2. Włącz zapłon (pozycja II) lub odpal silnik
3. Podłącz USB do laptopa
4. Uruchom aplikację i kliknij **POŁĄCZ** — port wykryje się automatycznie

> **Bluetooth:** sparuj adapter z laptopem raz przez ustawienia Windows, potem działa tak samo jak USB.

## Licencja

MIT
