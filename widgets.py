import math
import tkinter as tk
from collections import deque
from theme import COLORS, FONT_MONO, FONT_MONO_S, FONT_TITLE


class GaugeWidget(tk.Canvas):

    def __init__(self, parent, label, unit, min_val, max_val,
                 warn_val=None, danger_val=None, size=160, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=COLORS["bg"], highlightthickness=0, **kwargs)
        self.label      = label
        self.unit       = unit
        self.min_val    = min_val
        self.max_val    = max_val
        self.warn_val   = warn_val
        self.danger_val = danger_val
        self.size       = size
        self.value      = min_val
        self._draw(min_val)

    def _frac(self, val):
        return (val - self.min_val) / (self.max_val - self.min_val)

    def _needle_angle(self, val):
        return 225 - self._frac(val) * 270

    def _color_for(self, val):
        if self.danger_val and val >= self.danger_val:
            return COLORS["danger"]
        if self.warn_val and val >= self.warn_val:
            return COLORS["warn"]
        return COLORS["accent"]

    def _draw(self, val):
        self.delete("all")
        s   = self.size
        cx  = s / 2
        cy  = s / 2
        r   = s * 0.40
        r2  = r * 0.82
        pad = s * 0.06


        self.create_oval(pad, pad, s - pad, s - pad,
                         fill=COLORS["gauge_bg"],
                         outline=COLORS["border"], width=2)

        for i in range(11):
            pct  = i / 10
            ang  = math.radians(225 - pct * 270)
            x1   = cx + (r + 4) * math.cos(ang)
            y1   = cy - (r + 4) * math.sin(ang)
            x2   = cx + (r - 6) * math.cos(ang)
            y2   = cy - (r - 6) * math.sin(ang)
            col  = COLORS["text_dim"]
            tv   = self.min_val + pct * (self.max_val - self.min_val)
            if self.danger_val and tv >= self.danger_val:
                col = COLORS["danger"]
            elif self.warn_val and tv >= self.warn_val:
                col = COLORS["warn"]
            self.create_line(x1, y1, x2, y2, fill=col, width=2)

        self.create_arc(pad + 4, pad + 4, s - pad - 4, s - pad - 4,
                        start=-45, extent=270,
                        style="arc", outline=COLORS["grid"], width=6)

        frac  = self._frac(val)
        ext   = frac * 270
        color = self._color_for(val)
        if ext > 0:
            self.create_arc(pad + 4, pad + 4, s - pad - 4, s - pad - 4,
                            start=225 - ext, extent=ext,
                            style="arc", outline=color, width=6)

        ang2 = math.radians(self._needle_angle(val))
        nx   = cx + r2 * math.cos(ang2)
        ny   = cy - r2 * math.sin(ang2)
        self.create_line(cx, cy, nx, ny,
                         fill=color, width=3, capstyle="round")
        self.create_oval(cx - 5, cy - 5, cx + 5, cy + 5,
                         fill=COLORS["panel"], outline=color, width=2)

        self.create_text(cx, cy + r * 0.38,
                         text=f"{val:.0f}",
                         fill=COLORS["text_bright"],
                         font=("Consolas", int(s * 0.12), "bold"))
        self.create_text(cx, cy + r * 0.58,
                         text=self.unit,
                         fill=COLORS["accent"],
                         font=("Consolas", int(s * 0.07)))
        self.create_text(cx, s - pad * 1.6,
                         text=self.label,
                         fill=COLORS["text_dim"],
                         font=("Consolas", int(s * 0.07), "bold"))


    def set_value(self, val):
        val = max(self.min_val, min(self.max_val, val))
        self.value = val
        self._draw(val)

class BarGraph(tk.Canvas):

    def __init__(self, parent, label, unit, min_val, max_val,
                 warn_val=None, danger_val=None, height=36, **kwargs):
        super().__init__(parent, height=height, bg=COLORS["bg"],
                         highlightthickness=0, **kwargs)
        self.label      = label
        self.unit       = unit
        self.min_val    = min_val
        self.max_val    = max_val
        self.warn_val   = warn_val
        self.danger_val = danger_val
        self.value      = min_val
        self.bind("<Configure>", lambda e: self._draw(self.value))

    def _color_for(self, val):
        if self.danger_val and val >= self.danger_val:
            return COLORS["danger"]
        if self.warn_val and val >= self.warn_val:
            return COLORS["warn"]
        return COLORS["accent3"]

    def _draw(self, val):
        self.delete("all")
        w  = self.winfo_width()
        h  = self.winfo_height()
        if w < 2:
            return

        lw = 110
        bx = lw + 6
        bw = w - bx - 70
        by = 6
        bh = h - 12

        self.create_text(4, h // 2, anchor="w",
                         text=self.label, fill=COLORS["text_dim"],
                         font=FONT_TITLE)

        self.create_rectangle(bx, by, bx + bw, by + bh,
                               fill=COLORS["gauge_bg"],
                               outline=COLORS["border"])

        rng  = max(1, self.max_val - self.min_val)
        frac = max(0.0, min(1.0, (val - self.min_val) / rng))
        if frac > 0:
            self.create_rectangle(bx + 1, by + 1,
                                   bx + int(bw * frac) - 1, by + bh - 1,
                                   fill=self._color_for(val), outline="")

        self.create_text(bx + bw + 6, h // 2, anchor="w",
                         text=f"{val:.1f} {self.unit}",
                         fill=COLORS["text_bright"], font=FONT_MONO)

    def set_value(self, val):
        val = max(self.min_val, min(self.max_val, val))
        self.value = val
        self._draw(val)

class MiniGraph(tk.Canvas):
    def __init__(self, parent, label, max_points=120, height=80, **kwargs):
        super().__init__(parent, height=height, bg=COLORS["bg"],
                         highlightthickness=0, **kwargs)
        self.label      = label
        self.max_points = max_points
        self.data       = deque(maxlen=max_points)
        self.bind("<Configure>", lambda e: self._draw())

    def push(self, val):
        self.data.append(val)
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or len(self.data) < 2:
            return

        vals = list(self.data)
        mn   = min(vals)
        mx   = max(vals)
        rng  = mx - mn or 1
        pad  = 4

        def px(i):
            return pad + i * (w - 2 * pad) / (len(vals) - 1)

        def py(v):
            return h - pad - (v - mn) / rng * (h - 2 * pad)

        for i in range(3):
            yy = pad + i * (h - 2 * pad) // 2
            self.create_line(pad, yy, w - pad, yy,
                             fill=COLORS["grid"], dash=(2, 4))

        pts = [(px(i), py(v)) for i, v in enumerate(vals)]
        for i in range(len(pts) - 1):
            self.create_line(*pts[i], *pts[i + 1],
                             fill=COLORS["accent"], width=1.5, smooth=True)

        self.create_text(6, 4, anchor="nw",
                         text=self.label,
                         fill=COLORS["text_dim"], font=FONT_MONO_S)
        self.create_text(w - 4, 4, anchor="ne",
                         text=f"{vals[-1]:.1f}",
                         fill=COLORS["accent"], font=FONT_MONO_S)
