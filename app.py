import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import time
from datetime import datetime

from theme import COLORS, FONT_MONO, FONT_MONO_S, FONT_TITLE
from widgets import GaugeWidget, BarGraph, MiniGraph
from connection import OBDManager


class MercedesOBD2App:

    def __init__(self, root: tk.Tk):
        self.root    = root
        self.manager = OBDManager(
            on_data   = self._on_data,
            on_log    = self._log_console,
            on_status = self._set_status,
        )
        self.start_time = None

        root.title("Mercedes W204 · OBD2 Diagnostics")
        root.configure(bg=COLORS["bg"])
        root.geometry("1100x780")
        root.minsize(900, 650)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_ui()
        self._set_status("Niepołączony", "danger")

    def _build_ui(self):
        self._build_header()
        self._build_notebook()

    def _build_header(self):
        hdr = tk.Frame(self.root, bg=COLORS["panel"], height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(hdr, text="◈  MERCEDES W204 · OBD2 LIVE",
                 bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Consolas", 14, "bold")).pack(side="left", padx=18, pady=12)
        tk.Label(hdr, text="1.8 CGI · 2011",
                 bg=COLORS["panel"], fg=COLORS["text_dim"],
                 font=("Consolas", 10)).pack(side="left", padx=4)

        right = tk.Frame(hdr, bg=COLORS["panel"])
        right.pack(side="right", padx=10)

        self.lbl_status = tk.Label(right, text="● OFFLINE",
                                   bg=COLORS["panel"], fg=COLORS["danger"],
                                   font=("Consolas", 9, "bold"))
        self.lbl_status.pack(side="right", padx=10)

        buttons = [
            ("POŁĄCZ",      self._btn_connect),
            ("DEMO",        self._btn_demo),
            ("BŁĘDY",       self._btn_read_dtc),
            ("KASUJ BŁĘDY", self._btn_clear_dtc),
            ("ZAPISZ LOG",  self._btn_save_log),
        ]
        for txt, cmd in reversed(buttons):
            tk.Button(right, text=txt, command=cmd,
                      bg=COLORS["panel_light"], fg=COLORS["accent"],
                      activebackground=COLORS["border"],
                      activeforeground=COLORS["text_bright"],
                      relief="flat", font=("Consolas", 8, "bold"),
                      padx=8, pady=4, cursor="hand2").pack(side="right", padx=2, pady=8)

    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook",
                         background=COLORS["bg"], borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                         background=COLORS["panel"],
                         foreground=COLORS["text_dim"],
                         padding=[16, 6],
                         font=("Consolas", 9, "bold"),
                         borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", COLORS["panel_light"])],
                  foreground=[("selected", COLORS["accent"])])

        self.nb = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.nb.pack(fill="both", expand=True)

        self._tab_gauges()
        self._tab_bars()
        self._tab_graphs()
        self._tab_dtc()
        self._tab_console()

    def _tab_gauges(self):
        frm = tk.Frame(self.nb, bg=COLORS["bg"])
        self.nb.add(frm, text="  WSKAŹNIKI  ")

        row1 = tk.Frame(frm, bg=COLORS["bg"])
        row1.pack(fill="x", padx=20, pady=(20, 10))

        self.gauge_rpm  = GaugeWidget(row1, "OBROTY",    "RPM",  0, 7000, 5500, 6500, size=190)
        self.gauge_spd  = GaugeWidget(row1, "PRĘDKOŚĆ",  "km/h", 0, 260,  180,  220,  size=190)
        self.gauge_rpm.pack(side="left", padx=10)
        self.gauge_spd.pack(side="left", padx=10)

        info = tk.Frame(row1, bg=COLORS["panel"], padx=14, pady=12)
        info.pack(side="left", padx=10, fill="y")

        tk.Label(info, text="PARAMETRY DODATKOWE",
                 bg=COLORS["panel"], fg=COLORS["accent"],
                 font=FONT_TITLE).pack(anchor="w", pady=(0, 8))

        def make_row(parent, label_txt, attr_name, unit_txt):
            f = tk.Frame(parent, bg=COLORS["panel"])
            f.pack(fill="x", pady=3)
            tk.Label(f, text=label_txt, bg=COLORS["panel"],
                     fg=COLORS["text_dim"], font=FONT_MONO_S,
                     width=20, anchor="w").pack(side="left")
            lbl = tk.Label(f, text="–", bg=COLORS["panel"],
                           fg=COLORS["text_bright"], font=FONT_MONO,
                           width=7, anchor="e")
            lbl.pack(side="left")
            tk.Label(f, text=unit_txt, bg=COLORS["panel"],
                     fg=COLORS["accent"], font=FONT_MONO_S,
                     width=5, anchor="w").pack(side="left")
            setattr(self, attr_name, lbl)

        make_row(info, "Napięcie akumulatora", "lbl_volt",   "V")
        make_row(info, "MAF (przepływ pow.)",  "lbl_maf",    "g/s")
        make_row(info, "Temp. zasysania",      "lbl_intake", "°C")
        make_row(info, "Kąt zapłonu",          "lbl_timing", "°")
        make_row(info, "Korekta paliwa ST",    "lbl_stft",   "%")
        make_row(info, "Korekta paliwa LT",    "lbl_ltft",   "%")
        make_row(info, "Poziom paliwa",        "lbl_fuel",   "%")

        tk.Label(info, text=" ", bg=COLORS["panel"]).pack()
        self.lbl_uptime = tk.Label(info, text="Czas sesji: –",
                                   bg=COLORS["panel"], fg=COLORS["text_dim"],
                                   font=FONT_MONO_S)
        self.lbl_uptime.pack(anchor="w")
        self.lbl_clock = tk.Label(info, text="–",
                                  bg=COLORS["panel"], fg=COLORS["text_dim"],
                                  font=FONT_MONO_S)
        self.lbl_clock.pack(anchor="w")

        row2 = tk.Frame(frm, bg=COLORS["bg"])
        row2.pack(fill="x", padx=20, pady=5)

        self.gauge_cool  = GaugeWidget(row2, "CHŁODNICA",    "°C", 40, 130, 100, 115, size=160)
        self.gauge_load  = GaugeWidget(row2, "OBCIĄŻENIE",   "%",  0,  100, 80,  95,  size=160)
        self.gauge_throt = GaugeWidget(row2, "PRZEPUSTNICA", "%",  0,  100, 85,  95,  size=160)
        self.gauge_cool.pack(side="left", padx=10)
        self.gauge_load.pack(side="left", padx=10)
        self.gauge_throt.pack(side="left", padx=10)

    def _tab_bars(self):
        frm = tk.Frame(self.nb, bg=COLORS["bg"])
        self.nb.add(frm, text="  PASKI  ")

        specs = [
            ("rpm",    "Obroty silnika",          "RPM",  0,   7000, 5500, 6500),
            ("speed",  "Prędkość",                "km/h", 0,   260,  180,  220),
            ("cool",   "Temp. płynu chłodzącego", "°C",   40,  130,  100,  115),
            ("load",   "Obciążenie silnika",      "%",    0,   100,  80,   95),
            ("throt",  "Pozycja przepustnicy",    "%",    0,   100,  85,   95),
            ("volt",   "Napięcie akumulatora",    "V",    10,  16,   14.5, 15.2),
            ("maf",    "Przepływ powietrza MAF",  "g/s",  0,   200,  150,  180),
            ("intake", "Temp. zasysanego pow.",   "°C",   -20, 80,   60,   70),
            ("timing", "Kąt wyprzedzenia zapł.",  "°",    -20, 50,   None, None),
            ("stft",   "Korekta paliwa ST1",      "%",    -30, 30,   20,   25),
            ("ltft",   "Korekta paliwa LT1",      "%",    -30, 30,   15,   20),
            ("fuel",   "Poziom paliwa",           "%",    0,   100,  None, None),
        ]

        self.bars = {}
        for key, lbl, unit, mn, mx, w, d in specs:
            wrap = tk.Frame(frm, bg=COLORS["panel_light"], pady=2, padx=4)
            wrap.pack(fill="x", padx=18, pady=3)
            bar = BarGraph(wrap, lbl, unit, mn, mx, w, d, height=34)
            bar.pack(fill="x")
            self.bars[key] = bar

    def _tab_graphs(self):
        frm = tk.Frame(self.nb, bg=COLORS["bg"])
        self.nb.add(frm, text="  WYKRESY  ")

        specs = [
            ("rpm",   "Obroty [RPM]"),
            ("speed", "Prędkość [km/h]"),
            ("cool",  "Temp. chłodnicy [°C]"),
            ("load",  "Obciążenie [%]"),
            ("maf",   "MAF [g/s]"),
            ("volt",  "Napięcie [V]"),
        ]

        self.graphs = {}
        for i, (key, lbl) in enumerate(specs):
            row, col = divmod(i, 2)
            cell = tk.Frame(frm, bg=COLORS["panel"], padx=6, pady=4)
            cell.grid(row=row, column=col, sticky="nsew", padx=8, pady=4)
            g = MiniGraph(cell, lbl, height=110)
            g.pack(fill="both", expand=True)
            self.graphs[key] = g

        frm.columnconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)
        for r in range(3):
            frm.rowconfigure(r, weight=1)

    def _tab_dtc(self):
        frm = tk.Frame(self.nb, bg=COLORS["bg"])
        self.nb.add(frm, text="  BŁĘDY DTC  ")

        hdr = tk.Frame(frm, bg=COLORS["panel"], pady=8, padx=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="KODY BŁĘDÓW OBD2",
                 bg=COLORS["panel"], fg=COLORS["accent"],
                 font=("Consolas", 11, "bold")).pack(side="left")
        tk.Button(hdr, text="ODCZYTAJ", command=self._btn_read_dtc,
                  bg=COLORS["accent2"], fg="white", relief="flat",
                  font=FONT_TITLE, padx=10, pady=3).pack(side="right", padx=4)
        tk.Button(hdr, text="KASUJ BŁĘDY", command=self._btn_clear_dtc,
                  bg=COLORS["danger"], fg="white", relief="flat",
                  font=FONT_TITLE, padx=10, pady=3).pack(side="right", padx=4)

        style = ttk.Style()
        style.configure("Treeview",
                         background=COLORS["panel"],
                         fieldbackground=COLORS["panel"],
                         foreground=COLORS["text"],
                         rowheight=26, font=FONT_MONO_S)
        style.configure("Treeview.Heading",
                         background=COLORS["panel_light"],
                         foreground=COLORS["accent"],
                         font=FONT_TITLE)
        style.map("Treeview",
                  background=[("selected", COLORS["border"])])

        cols = ("Kod", "Opis", "Status", "Odczytano o")
        self.dtc_tree = ttk.Treeview(frm, columns=cols, show="headings", height=22)
        for col, w in zip(cols, [90, 500, 90, 130]):
            self.dtc_tree.heading(col, text=col)
            self.dtc_tree.column(col, width=w, anchor="w")

        sb = ttk.Scrollbar(frm, orient="vertical",
                           command=self.dtc_tree.yview)
        self.dtc_tree.configure(yscrollcommand=sb.set)
        self.dtc_tree.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        sb.pack(side="right", fill="y", pady=8)

    def _tab_console(self):
        frm = tk.Frame(self.nb, bg=COLORS["bg"])
        self.nb.add(frm, text="  KONSOLA  ")

        self.console = tk.Text(
            frm, bg=COLORS["gauge_bg"], fg=COLORS["text"],
            font=FONT_MONO_S, insertbackground=COLORS["accent"],
            relief="flat", wrap="word", state="disabled")
        sb = ttk.Scrollbar(frm, orient="vertical",
                           command=self.console.yview)
        self.console.configure(yscrollcommand=sb.set)
        self.console.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        sb.pack(side="right", fill="y", pady=8)

    def _btn_connect(self):
        if self.manager.is_connected():
            self.manager.disconnect()
            self.start_time = None
        else:
            self.start_time = time.time()
            import threading
            threading.Thread(target=self.manager.connect, daemon=True).start()

    def _btn_demo(self):
        if self.manager.is_connected():
            self.manager.disconnect()
        self.start_time = time.time()
        self.manager.connect_demo()

    def _btn_read_dtc(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Brak połączenia",
                                   "Najpierw połącz adapter OBD2 lub uruchom tryb DEMO.")
            return
        self._log_console("► Odczytuję kody błędów DTC...")
        import threading
        threading.Thread(target=self._do_read_dtc, daemon=True).start()

    def _do_read_dtc(self):
        self.dtc_tree.delete(*self.dtc_tree.get_children())
        codes = self.manager.read_dtc()
        ts    = datetime.now().strftime("%H:%M:%S")

        if codes is None:
            self._log_console("✗ Nie udało się odczytać błędów")
            return
        if not codes:
            self._log_console("✓ Brak aktywnych kodów błędów – auto jest czyste!")
            return

        for code, desc in codes:
            self.root.after(0, lambda c=code, d=desc, t=ts:
                self.dtc_tree.insert("", "end",
                                     values=(c, d, "Aktywny", t)))
        self._log_console(f"✓ Znaleziono {len(codes)} kod(ów) błędów")

    def _btn_clear_dtc(self):
        if not self.manager.is_connected():
            messagebox.showwarning("Brak połączenia", "Brak aktywnego połączenia.")
            return
        if not messagebox.askyesno(
                "Kasowanie błędów",
                "Czy na pewno chcesz skasować wszystkie kody błędów DTC?\n\n"
                "⚠ Upewnij się, że znasz PRZYCZYNĘ błędów przed ich skasowaniem!"):
            return
        ok = self.manager.clear_dtc()
        if ok:
            self.dtc_tree.delete(*self.dtc_tree.get_children())
            self._log_console("✓ Kody DTC skasowane")
        else:
            self._log_console("✗ Kasowanie nie powiodło się")

    def _btn_save_log(self):
        entries = self.manager.log_entries
        if not entries:
            messagebox.showinfo("Log", "Brak danych do zapisania.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Wszystkie", "*.*")],
            initialfile=f"obd_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            self._log_console(f"✓ Zapisano {len(entries)} rekordów → {path}")

    def _on_data(self, data: dict):
        """Callback wywoływany przez OBDManager z nowym pomiarem."""
        self.root.after(0, self._update_widgets, data)

    def _update_widgets(self, data: dict):
        g = lambda k: data.get(k) or 0

        rpm    = g("rpm")
        spd    = g("speed")
        cool   = g("cool")
        load   = g("load")
        throt  = g("throt")
        volt   = g("volt")
        maf    = g("maf")
        intake = g("intake")
        timing = g("timing")
        stft   = g("stft")
        ltft   = g("ltft")
        fuel   = g("fuel")

        self.gauge_rpm.set_value(rpm)
        self.gauge_spd.set_value(spd)
        self.gauge_cool.set_value(cool)
        self.gauge_load.set_value(load)
        self.gauge_throt.set_value(throt)

        self.lbl_volt.config(text=f"{volt:.2f}")
        self.lbl_maf.config(text=f"{maf:.1f}")
        self.lbl_intake.config(text=f"{intake:.1f}")
        self.lbl_timing.config(text=f"{timing:.1f}")
        self.lbl_stft.config(text=f"{stft:+.1f}")
        self.lbl_ltft.config(text=f"{ltft:+.1f}")
        self.lbl_fuel.config(text=f"{fuel:.0f}")

        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            h, rem  = divmod(elapsed, 3600)
            m, s    = divmod(rem, 60)
            self.lbl_uptime.config(text=f"Czas sesji: {h:02d}:{m:02d}:{s:02d}")
        self.lbl_clock.config(text=datetime.now().strftime("%H:%M:%S"))

        vals = dict(rpm=rpm, speed=spd, cool=cool, load=load, throt=throt,
                    volt=volt, maf=maf, intake=intake, timing=timing,
                    stft=stft, ltft=ltft, fuel=fuel)
        for key, bar in self.bars.items():
            bar.set_value(vals.get(key, 0))

        for key in ("rpm", "speed", "cool", "load", "maf", "volt"):
            if key in self.graphs and key in vals:
                self.graphs[key].push(vals[key])

    def _set_status(self, text: str, color_key: str):
        color  = COLORS.get(color_key, COLORS["text_dim"])
        prefix = {
            "accent3": "● ",
            "warn":    "◉ ",
        }.get(color_key, "○ ")
        self.root.after(0, lambda: self.lbl_status.config(
            text=f"{prefix}{text.upper()}", fg=color))

    def _log_console(self, msg: str):
        ts  = datetime.now().strftime("%H:%M:%S")
        txt = f"[{ts}] {msg}\n"

        def _do():
            self.console.config(state="normal")
            self.console.insert("end", txt)
            self.console.see("end")
            self.console.config(state="disabled")

        self.root.after(0, _do)

    def _on_close(self):
        self.manager.disconnect()
        self.root.destroy()
