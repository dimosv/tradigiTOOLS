# tradigiTOOLS.py — PySide2/Qt UI-only (no Maya ops)
# Tangent icons updated for your build (autoTangent, splineTangent, stepTangent, etc.)
from __future__ import annotations
import os
import maya.cmds as cmds
from PySide2 import QtCore, QtGui, QtWidgets
try:
    from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
except Exception:
    class MayaQWidgetDockableMixin(object): pass

APP_ID = "tradigiTOOLS"
TITLE  = "tradigiTOOLS"
__ui_version__ = "v2025.08.29.b0001"

# ---------- Metrics ----------
W_CONTENT = 306
GUTTER    = 7
TOP_GAP   = 6
SPACING   = 4
BTN_H     = 20
BTN_H_LG  = 24
LBL_H     = 16

STRIP_WIDTHS   = [36,30,28,26,44,26,28,30,36]
STRIP_SPACING  = 1
STRIP_LRM      = 7
TRACK_W        = 256
TRACK_LEFT_PAD = 25
SLIDER_H       = 14

BIAS_LABEL_W   = 44
BIAS_FIELD_W   = 46
BIAS_GAP_W     = 14
BIAS_LABEL_PAD = 8
BIAS_SIDE_GAP  = 8
BIAS_TOTAL     = (BIAS_SIDE_GAP + BIAS_LABEL_W + BIAS_LABEL_PAD + BIAS_FIELD_W +
                  BIAS_GAP_W + BIAS_FIELD_W + BIAS_LABEL_PAD + BIAS_LABEL_W + BIAS_SIDE_GAP)
BIAS_LEFT      = TRACK_LEFT_PAD + (TRACK_W - BIAS_TOTAL)//2

MAKER_WIDTHS  = [60,40,88,40,60]
MAKER_SPACING = 1
MAKER_LRM     = 7

SET_W, SET_SPACING, SET_LRM = 40, 2, 7
NUD_W, NUD_SPACING, NUD_LRM = 35, 2, 6
INCR_BTN, INCR_SPACING, INCR_LRM = 24, 6, 7

QS_COL_GAP, QS_LRM = 2, 7
QS_COL_W = int((W_CONTENT - 2*QS_LRM - QS_COL_GAP) / 2)

# ---------- Icon helpers ----------
def _try_qicon(path_or_res: str) -> QtGui.QIcon | None:
    ic = QtGui.QIcon(path_or_res)
    return ic if not ic.isNull() else None

def _ensure_exts(name: str):
    base, ext = os.path.splitext(name)
    if ext: return [name]
    return [base + ".png", base + ".xpm", base + ".svg"]

def _maya_icon_roots():
    roots = []
    xbm = os.environ.get("XBMLANGPATH", "")
    if xbm:
        for p in xbm.split(os.pathsep):
            if p and os.path.isdir(p): roots.append(p)
    ml = os.environ.get("MAYA_LOCATION", "")
    if ml:
        ip = os.path.join(ml, "icons")
        if os.path.isdir(ip): roots.append(ip)
    return roots

def _iter_icons_recursive():
    for root in _maya_icon_roots():
        for d, _dirs, files in os.walk(root):
            for fn in files:
                yield d, fn

def _load_from_candidates(candidates):
    # Qt resources (:/name) then as-given, then filesystem
    for n in candidates:
        for v in _ensure_exts(n):
            res = v if v.startswith(":/") else (":/" + v)
            ic = _try_qicon(res)
            if ic: return ic
        ic = _try_qicon(n)
        if ic: return ic
    for n in candidates:
        for v in _ensure_exts(n):
            for root in _maya_icon_roots():
                p = os.path.join(root, v)
                if os.path.isfile(p):
                    ic = _try_qicon(p)
                    if ic: return ic
    return None

def _rm_list(pattern="*"):
    try:
        return cmds.resourceManager(nameFilter=pattern) or []
    except Exception:
        return []

def _best_res_icon(names):
    # Prefer png > svg > xpm; mildly prefer shorter names
    def score(nm):
        s = 0; ln = nm.lower()
        if ln.endswith(".png"): s += 30
        elif ln.endswith(".svg"): s += 20
        elif ln.endswith(".xpm"): s += 10
        s += max(0, 40 - len(nm))
        return s
    for nm in sorted(set(names), key=lambda n: -score(n)):
        ic = _try_qicon(":/"+nm)
        if ic: return ic
    return None

def _load_res_by_keywords(keywords, must=("tangent",)):
    pool = _rm_list("*tangent*") or _rm_list("*Tangent*") or _rm_list("*")
    kws  = [k.lower() for k in (keywords or [])]
    must = [m.lower() for m in (must or [])]
    cands = []
    for nm in pool:
        low = nm.lower()
        if all(m in low for m in must) and all(k in low for k in kws):
            cands.append(nm)
    return _best_res_icon(cands)

def _load_fs_by_keywords(keywords, must=("tangent",)):
    kws  = [k.lower() for k in (keywords or [])]
    must = [m.lower() for m in (must or [])]
    best = None
    for d, fn in _iter_icons_recursive():
        low = fn.lower()
        if all(m in low for m in must) and all(k in low for k in kws):
            # prefer png > svg > xpm
            if (best is None
                or (best.lower().endswith(".xpm") and low.endswith(".png"))
                or (best.lower().endswith(".svg") and low.endswith(".png"))
                or (best.lower().endswith(".xpm") and low.endswith(".svg"))):
                best = os.path.join(d, fn)
    if best:
        ic = _try_qicon(best)
        if ic: return ic
    return None

def load_icon_smart(candidates, keywords=None):
    ic = _load_from_candidates(candidates)
    if ic: return ic
    if keywords:
        ic = _load_res_by_keywords(keywords, must=("tangent",))
        if ic: return ic
        ic = _load_fs_by_keywords(keywords, must=("tangent",))
        if ic: return ic
    return None

def mirrored_icon(icon: QtGui.QIcon) -> QtGui.QIcon:
    if not icon or icon.isNull(): return QtGui.QIcon()
    pm = icon.pixmap(16, 16); img = pm.toImage().mirrored(True, False)
    return QtGui.QIcon(QtGui.QPixmap.fromImage(img))

# Tangent icons — prioritized with YOUR exact names
TANGENT_ICON_CANDIDATES = {
    "Auto":    ["autoTangent", "animTangentAuto","tangentAuto","GEiconTangentAuto","setTangentAuto",
                "menuIconGraphTangentAuto","menuIconGraphAutoTangent"],
    "Spline":  ["splineTangent", "animTangentSpline","tangentSpline","GEiconTangentSpline","setTangentSpline",
                "menuIconGraphTangentSpline"],
    "Linear":  ["linearTangent", "animTangentLinear","tangentLinear","GEiconTangentLinear","setTangentLinear",
                "menuIconGraphTangentLinear"],
    "Clamped": ["clampedTangent","animTangentClamped","tangentClamped","GEiconTangentClamped","setTangentClamped",
                "menuIconGraphTangentClamped"],
    "Flat":    ["flatTangent",   "animTangentFlat","tangentFlat","GEiconTangentFlat","setTangentFlat",
                "menuIconGraphTangentFlat"],
    "Plateau": ["plateauTangent","animTangentPlateau","tangentPlateau","GEiconTangentPlateau","setTangentPlateau",
                "menuIconGraphTangentPlateau"],
    "Stepped": ["stepTangent",   "animTangentStepped","tangentStepped","GEiconTangentStepped","setTangentStepped",
                "menuIconGraphTangentStepped"],
}
TANGENT_FUZZY = {
    "Auto":    ["auto"],
    "Spline":  ["spline"],
    "Linear":  ["linear"],
    "Clamped": ["clamp","clamped"],
    "Flat":    ["flat"],
    "Plateau": ["plateau"],
    "Stepped": ["step","stepped"],
}

DOCK_LEFT_CANDS  = ["perspBrowserLayout"]
DOCK_FLOAT_CANDS = ["menu_key"]

# ---------- Small widgets ----------
def push_btn(text, w, h=BTN_H, bg=None, fg=None):
    b = QtWidgets.QPushButton(text); b.setFixedSize(w, h)
    if bg or fg:
        ss = "QPushButton{"
        if bg: ss += "background: rgb(%d,%d,%d);"%(bg.red(),bg.green(),bg.blue())
        if fg: ss += f"color:{fg};"
        ss += "}"
        b.setStyleSheet(ss)
    return b

def label(text, w, h=LBL_H, align=QtCore.Qt.AlignCenter):
    L = QtWidgets.QLabel(text); L.setFixedSize(w,h); L.setAlignment(align|QtCore.Qt.AlignVCenter); return L

def line_edit(w, h=BTN_H, ph=None, bg=None, fg=None):
    e = QtWidgets.QLineEdit(); e.setFixedSize(w,h)
    if ph: e.setPlaceholderText(ph)
    if bg or fg:
        ss = "QLineEdit{"
        if bg: ss += "background: rgb(%d,%d,%d);"%(bg.red(),bg.green(),bg.blue())
        if fg: ss += f"color:{fg};"
        ss += "}"
        e.setStyleSheet(ss)
    return e

def hline():
    f = QtWidgets.QFrame(); f.setFrameShape(QtWidgets.QFrame.HLine); f.setFrameShadow(QtWidgets.QFrame.Sunken); return f

def glyph_tool(text, tip, clicked_slot=None):
    t = QtWidgets.QToolButton()
    t.setAutoRaise(True); t.setFocusPolicy(QtCore.Qt.NoFocus)
    t.setCursor(QtCore.Qt.PointingHandCursor)
    t.setFixedSize(18,18)
    t.setText(text); t.setToolTip(tip)
    t.setStyleSheet(
        "QToolButton{border:0;background:transparent;border-radius:3px;}"
        "QToolButton:hover{background:rgba(255,255,255,0.12);}"
        "QToolButton:pressed{background:rgba(255,255,255,0.20);}"
        "QToolButton::menu-indicator{image:none;width:0;height:0;}"
    )
    if clicked_slot: t.clicked.connect(clicked_slot)
    return t

def icon_tool(icon: QtGui.QIcon | None, fallback_text: str, tip: str, clicked_slot=None):
    t = QtWidgets.QToolButton()
    t.setAutoRaise(True); t.setFocusPolicy(QtCore.Qt.NoFocus)
    t.setCursor(QtCore.Qt.PointingHandCursor)
    t.setFixedSize(18,18)
    t.setToolTip(tip)
    t.setStyleSheet(
        "QToolButton{border:0;background:transparent;border-radius:3px;}"
        "QToolButton:hover{background:rgba(255,255,255,0.12);}"
        "QToolButton:pressed{background:rgba(255,255,255,0.20);}"
        "QToolButton::menu-indicator{image:none;width:0;height:0;}"
    )
    if icon and not icon.isNull():
        t.setIcon(icon); t.setIconSize(QtCore.QSize(16,16))
    else:
        t.setText(fallback_text)
    if clicked_slot: t.clicked.connect(clicked_slot)
    return t

# ---------- Collapsible ----------
class Collapsible(QtWidgets.QWidget):
    toggled = QtCore.Signal(bool)
    def __init__(self, title, content:QtWidgets.QWidget, start_open=True, top_gap=TOP_GAP, parent=None):
        super().__init__(parent)
        self.setFixedWidth(W_CONTENT)

        spacer = QtWidgets.QWidget(); spacer.setFixedHeight(top_gap)

        bar = QtWidgets.QFrame(); bar.setFixedWidth(W_CONTENT); bar.setFixedHeight(20)
        bar.setStyleSheet("QFrame{background:rgba(255,255,255,0.06);border:0;border-radius:2px;}")
        hb = QtWidgets.QHBoxLayout(bar); hb.setContentsMargins(6,0,6,0); hb.setSpacing(6)

        self.arrow = QtWidgets.QToolButton()
        self.arrow.setAutoRaise(True); self.arrow.setFixedSize(14,14)
        self.arrow.setArrowType(QtCore.Qt.DownArrow if start_open else QtCore.Qt.RightArrow)
        self.arrow.setStyleSheet("QToolButton{background:transparent;border:0;}QToolButton:hover{background:transparent;}")

        self.title = QtWidgets.QLabel(title)
        self.title.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.title.setStyleSheet("QLabel{font-weight:bold;background:transparent;}")

        hb.addWidget(self.arrow, 0)
        hb.addWidget(self.title, 1, QtCore.Qt.AlignLeft)

        self.body = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(0)
        v.addWidget(spacer); v.addWidget(bar); v.addWidget(self.body)

        inner = QtWidgets.QVBoxLayout(self.body)
        inner.setContentsMargins(0,SPACING,0,0); inner.setSpacing(SPACING)
        inner.addWidget(content)
        self.body.setVisible(start_open)

        bar.installEventFilter(self)
        self.arrow.clicked.connect(self._toggle)

    def eventFilter(self, obj, ev):
        if ev.type() == QtCore.QEvent.MouseButtonRelease:
            self._toggle(); return True
        return super().eventFilter(obj, ev)

    def _bubble_request_fit(self):
        w = self.window()
        if hasattr(w, "request_fit_to_contents"):
            w.request_fit_to_contents()

    def _toggle(self):
        st = not self.body.isVisible()
        self.body.setVisible(st)
        self.arrow.setArrowType(QtCore.Qt.DownArrow if st else QtCore.Qt.RightArrow)
        self.body.adjustSize(); self.adjustSize()
        p = self.parentWidget()
        if p: p.updateGeometry()
        self._bubble_request_fit()
        QtCore.QTimer.singleShot(0, self._bubble_request_fit)
        QtCore.QTimer.singleShot(50, self._bubble_request_fit)
        self.toggled.emit(st)

# ---------- keyCONTROL ----------
class KeyControl(QtWidgets.QWidget):
    MAP_VALS = [0,14,20,33,50,67,80,86,100]
    MAP_LABS = ["<<","1/7","1/5","1/3","<>","1/3","1/5","1/7",">>"]

    def __init__(self):
        super().__init__(); self.setFixedWidth(W_CONTENT)
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(SPACING)

        v.addLayout(self._track_banner("▼ KEYs ▼"))
        keys_row, self.keys_buttons = self._chip_row(color="red"); v.addLayout(keys_row)
        self.keys_slider = self._make_slider(); self.keys_slider.setValue(50); v.addLayout(self._wrap_slider(self.keys_slider))
        v.addLayout(self._bias_midline())
        self.brks_slider = self._make_slider(); self.brks_slider.setValue(50); v.addLayout(self._wrap_slider(self.brks_slider))
        brks_row, self.brks_buttons = self._chip_row(color="green"); v.addLayout(brks_row)
        v.addLayout(self._track_banner("▲ BRKs ▲"))
        v.addWidget(hline())

        maker = QtWidgets.QHBoxLayout(); maker.setContentsMargins(MAKER_LRM,0,MAKER_LRM,0); maker.setSpacing(MAKER_SPACING)
        cols=[QtGui.QColor(255,64,64),QtGui.QColor(255,64,64),QtGui.QColor(170,120,255),QtGui.QColor(64,255,64),QtGui.QColor(64,255,64)]
        for w,txt,bg in zip(MAKER_WIDTHS,["KEY","R","smartKEY","G","BRK"],cols):
            maker.addWidget(push_btn(txt,w,bg=bg,fg="#000000"))
        v.addLayout(maker)

        v.addSpacing(4); v.addWidget(label("▼ Modes ▼", W_CONTENT))
        m = QtWidgets.QHBoxLayout(); m.setSpacing(8)
        self.cb_ripple = QtWidgets.QCheckBox("Ripple")
        self.cb_selattr= QtWidgets.QCheckBox("Selected Attr."); self.cb_selattr.setChecked(True)
        self.cb_skip   = QtWidgets.QCheckBox("Skip Unkeyed")
        for w,cb in ((60,self.cb_ripple),(110,self.cb_selattr),(120,self.cb_skip)):
            cb.setFixedHeight(18); cb.setMinimumWidth(w); cb.setMaximumWidth(w); m.addWidget(cb)
        v.addLayout(m)

        for idx,b in enumerate(self.keys_buttons):
            b.clicked.connect(lambda _=False,i=idx:self.keys_slider.setValue(self.MAP_VALS[i]))
        for idx,b in enumerate(self.brks_buttons):
            b.clicked.connect(lambda _=False,i=idx:self.brks_slider.setValue(self.MAP_VALS[i]))
        self.keys_slider.valueChanged.connect(lambda val: self._set_bias(self.key_bias, val))
        self.brks_slider.valueChanged.connect(lambda val: self._set_bias(self.brk_bias, val))
        self.key_bias.editingFinished.connect(lambda: self.keys_slider.setValue(self._coerce(self.key_bias.text())))
        self.brk_bias.editingFinished.connect(lambda: self.brks_slider.setValue(self._coerce(self.brk_bias.text())))

    def _track_banner(self, text):
        h = QtWidgets.QHBoxLayout(); h.setContentsMargins(0,0,0,0); h.setSpacing(0)
        h.addSpacing(TRACK_LEFT_PAD); h.addWidget(label(text, TRACK_W)); h.addStretch(1); return h
    def _chip_row(self, color="red"):
        row = QtWidgets.QHBoxLayout(); row.setContentsMargins(STRIP_LRM,0,STRIP_LRM,0); row.setSpacing(STRIP_SPACING)
        bg = QtGui.QColor(255,64,64) if color=="red" else QtGui.QColor(64,255,64)
        buttons=[]
        for w,t in zip(STRIP_WIDTHS,self.MAP_LABS):
            b = push_btn(t,w,bg=bg,fg="#000000"); buttons.append(b); row.addWidget(b)
        return row, buttons
    def _make_slider(self):
        s = QtWidgets.QSlider(QtCore.Qt.Horizontal); s.setRange(0,100); s.setFixedSize(TRACK_W, SLIDER_H); return s
    def _wrap_slider(self, slider):
        sh = QtWidgets.QHBoxLayout(); sh.setContentsMargins(0,0,0,0); sh.setSpacing(0)
        sh.addSpacing(TRACK_LEFT_PAD); sh.addWidget(slider); sh.addStretch(1); return sh
    def _bias_midline(self):
        bh = QtWidgets.QHBoxLayout(); bh.setContentsMargins(0,0,0,0); bh.setSpacing(0)
        bh.addSpacing(BIAS_LEFT)
        bh.addSpacing(BIAS_SIDE_GAP)
        bh.addWidget(label("▲ KEYs", BIAS_LABEL_W, align=QtCore.Qt.AlignRight))
        bh.addSpacing(BIAS_LABEL_PAD)
        self.key_bias = line_edit(BIAS_FIELD_W, 14, bg=QtGui.QColor(255,190,190), fg="#000000"); self.key_bias.setText("50")
        bh.addWidget(self.key_bias)
        bh.addSpacing(BIAS_GAP_W)
        self.brk_bias = line_edit(BIAS_FIELD_W, 14, bg=QtGui.QColor(190,255,190), fg="#000000"); self.brk_bias.setText("50")
        bh.addWidget(self.brk_bias)
        bh.addSpacing(BIAS_LABEL_PAD)
        bh.addWidget(label("BRKs ▼", BIAS_LABEL_W, align=QtCore.Qt.AlignLeft))
        bh.addSpacing(BIAS_SIDE_GAP)
        bh.addStretch(1)
        return bh
    def _set_bias(self, line:QtWidgets.QLineEdit, v:int):
        line.blockSignals(True); line.setText(str(int(v))); line.blockSignals(False)
    def _coerce(self, txt:str)->int:
        try: v = int(round(float(txt)))
        except: v = 0
        return max(0,min(100,v))

# ---------- timeSHIFT ----------
class TimeShift(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.setFixedWidth(W_CONTENT)
    # (UI unchanged from your current good build)
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(SPACING)

        hdr = QtWidgets.QHBoxLayout(); hdr.setContentsMargins(SET_LRM,0,SET_LRM,0); hdr.setSpacing(6)
        hdr.addWidget(QtWidgets.QLabel("setTIME")); hdr.addStretch(1); v.addLayout(hdr)

        row = QtWidgets.QHBoxLayout(); row.setContentsMargins(SET_LRM,0,SET_LRM,0); row.setSpacing(SET_SPACING)
        for t in ("1s","2s","3s","4s","5s","6s","8s"): row.addWidget(push_btn(t, SET_W))
        v.addLayout(row)

        v.addSpacing(6)
        inc = QtWidgets.QHBoxLayout(); inc.setContentsMargins(INCR_LRM,0,INCR_LRM,0); inc.setSpacing(INCR_SPACING)
        self.cb_incr = QtWidgets.QCheckBox("Increments"); self.cb_incr.setChecked(False)
        self.cb_incr.setFixedHeight(BTN_H); self.cb_incr.setMinimumWidth(90); self.cb_incr.setMaximumWidth(120)
        self.le_incr = QtWidgets.QLineEdit(); self.le_incr.setFixedHeight(BTN_H)
        ap = push_btn("✔", INCR_BTN)
        inc.addWidget(self.cb_incr); inc.addWidget(self.le_incr, 1); inc.addWidget(ap); v.addLayout(inc)

        v.addSpacing(6)
        v.addWidget(QtWidgets.QLabel("nudgeTIME"))
        nud = QtWidgets.QHBoxLayout(); nud.setContentsMargins(NUD_LRM,0,NUD_LRM,0); nud.setSpacing(NUD_SPACING)
        for t in ("-8","-4","-2","-1","+1","+2","+4","+8"): nud.addWidget(push_btn(t, NUD_W))
        v.addLayout(nud)

        v.addSpacing(4)
        foot_wrap = QtWidgets.QWidget()
        fw = QtWidgets.QHBoxLayout(foot_wrap); fw.setContentsMargins(NUD_LRM,0,NUD_LRM,0); fw.setSpacing(0)

        footer = QtWidgets.QFrame()
        footer.setStyleSheet("QFrame{background:rgba(255,255,255,0.05);border:0;border-radius:2px;}")
        fh = QtWidgets.QHBoxLayout(footer); fh.setContentsMargins(8,1,8,1); fh.setSpacing(6)

        mono = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        def transparent(lbl:QtWidgets.QLabel):
            lbl.setStyleSheet("QLabel{background:transparent;}"); return lbl

        fh.addWidget(transparent(QtWidgets.QLabel("KEY:")))
        self.lbl_key = QtWidgets.QLabel("1001"); self.lbl_key.setFont(mono)
        key_w = QtGui.QFontMetrics(mono).width("00000")
        self.lbl_key.setFixedWidth(key_w); self.lbl_key.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        fh.addWidget(self.lbl_key)

        fh.addStretch(1)
        fh.addWidget(transparent(QtWidgets.QLabel("Timing:")))
        self.lbl_timing = QtWidgets.QLabel("12"); self.lbl_timing.setFont(mono)
        tm_w = QtGui.QFontMetrics(mono).width("00000")
        self.lbl_timing.setFixedWidth(tm_w); self.lbl_timing.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        fh.addWidget(self.lbl_timing)

        fw.addWidget(footer); v.addWidget(foot_wrap)

# ---------- viewSWITCH ----------
class ViewSwitch(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.setFixedWidth(W_CONTENT)
        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(SPACING)

        top = QtWidgets.QHBoxLayout(); top.setContentsMargins(GUTTER,0,GUTTER,0)
        top.addWidget(push_btn("setSWITCH", W_CONTENT - 2*GUTTER)); v.addLayout(top)

        info = QtWidgets.QHBoxLayout(); info.setContentsMargins(GUTTER,0,GUTTER,0); info.setSpacing(8)
        self.toggleBtn = push_btn("▸ options", 70)  # collapsed by default
        cur = QtWidgets.QLabel("Current: No Selected Camera")
        cur.setFixedHeight(BTN_H-2); cur.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        cur.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        info.addWidget(self.toggleBtn); info.addStretch(1); info.addWidget(cur); v.addLayout(info)

        self.details = QtWidgets.QWidget(); d = QtWidgets.QVBoxLayout(self.details); d.setContentsMargins(0,0,0,0); d.setSpacing(SPACING)

        cam = QtWidgets.QHBoxLayout(); cam.setContentsMargins(GUTTER,0,GUTTER,0); cam.setSpacing(6)
        cam.addWidget(QtWidgets.QLabel("CAM"))
        self.menu = QtWidgets.QComboBox(); self.menu.addItem("None"); self.menu.setFixedHeight(BTN_H-2); self.menu.setMinimumWidth(150)
        cam.addWidget(self.menu, 1)
        cam.addWidget(push_btn("↻", 22, BTN_H-2))
        cam.addWidget(QtWidgets.QCheckBox("Orthos"), 0, QtCore.Qt.AlignRight)
        d.addLayout(cam)

        mk = QtWidgets.QHBoxLayout(); mk.setContentsMargins(GUTTER,0,GUTTER,0); mk.setSpacing(6)
        lbl = QtWidgets.QLabel("makeCAM"); fixed_lbl_w = 60; lbl.setFixedWidth(fixed_lbl_w); mk.addWidget(lbl)

        total = W_CONTENT - 2*GUTTER; btn_w = 22
        input_w = total - fixed_lbl_w - btn_w - (6*2)
        if input_w < 60: input_w = 60
        self.make_input = line_edit(input_w, BTN_H-2, "input camera name here")
        mk.addWidget(self.make_input)
        mk.addWidget(push_btn("✔", btn_w, BTN_H-2))
        d.addLayout(mk)

        self.cb_persp = QtWidgets.QCheckBox("perspCOPY"); self.cb_persp.setChecked(True)
        d.addWidget(self.cb_persp)

        self.details.setVisible(False)
        v.addWidget(self.details)

        def toggle():
            vis = self.details.isVisible()
            self.details.setVisible(not vis)
            self.toggleBtn.setText("▾ options" if not vis else "▸ options")
            w = self.window()
            if hasattr(w, "request_fit_to_contents"):
                w.request_fit_to_contents()
        self.toggleBtn.clicked.connect(toggle)

# ---------- quickSELECT ----------
class QuickSelect(QtWidgets.QWidget):
    def __init__(self):
        super().__init__(); self.setFixedWidth(W_CONTENT)

        # Load tangent icons with your names prioritized
        self.icon_cache: dict[str, QtGui.QIcon] = {}
        for name, cands in TANGENT_ICON_CANDIDATES.items():
            ic = load_icon_smart(cands, keywords=TANGENT_FUZZY.get(name))
            if ic: self.icon_cache[name] = ic

        v = QtWidgets.QVBoxLayout(self); v.setContentsMargins(0,0,0,0); v.setSpacing(2)

        row = QtWidgets.QHBoxLayout(); row.setContentsMargins(QS_LRM,0,QS_LRM,0); row.setSpacing(6)

        strip = QtWidgets.QHBoxLayout(); strip.setContentsMargins(0,0,0,0); strip.setSpacing(2)

        def mk_tangent(name: str, short: str):
            ic = self.icon_cache.get(name)
            t = QtWidgets.QToolButton()
            t.setAutoRaise(True); t.setFocusPolicy(QtCore.Qt.NoFocus)
            t.setCursor(QtCore.Qt.PointingHandCursor)
            t.setFixedSize(18,18); t.setToolTip(name)
            t.setStyleSheet(
                "QToolButton{border:0;background:transparent;border-radius:3px;}"
                "QToolButton:hover{background:rgba(255,255,255,0.12);}"
                "QToolButton:pressed{background:rgba(255,255,255,0.20);}"
                "QToolButton::menu-indicator{image:none;width:0;height:0;}"
            )
            if ic and not ic.isNull():
                t.setIcon(ic); t.setIconSize(QtCore.QSize(16,16))
            else:
                t.setText(short)
            return t

        strip.addStretch(1)
        tangents = [("Auto","A"),("Spline","Sp"),("Linear","L"),("Clamped","Cl"),
                    ("Flat","Fl"),("Plateau","P"),("Stepped","St")]
        self.tangent_buttons = []
        for nm,short in tangents:
            b = mk_tangent(nm, short); self.tangent_buttons.append(b); strip.addWidget(b)
        strip.addStretch(1)

        strip_holder = QtWidgets.QWidget(); strip_holder.setLayout(strip); strip_holder.setFixedHeight(20)
        row.addWidget(strip_holder, 1)

        vline = QtWidgets.QFrame(); vline.setFrameShape(QtWidgets.QFrame.VLine); vline.setFrameShadow(QtWidgets.QFrame.Sunken)
        row.addWidget(vline, 0)

        # Default Tangent popup (icon + text)
        default_ic = self.icon_cache.get("Auto")
        self.defaultBtn = QtWidgets.QToolButton()
        self.defaultBtn.setAutoRaise(True); self.defaultBtn.setFixedSize(18,18)
        self.defaultBtn.setToolTip("Default Tangent Type")
        self.defaultBtn.setStyleSheet(
            "QToolButton{border:0;background:transparent;border-radius:3px;}"
            "QToolButton:hover{background:rgba(255,255,255,0.12);}"
            "QToolButton:pressed{background:rgba(255,255,255,0.20);}"
            "QToolButton::menu-indicator{image:none;width:0;height:0;}"
        )
        if default_ic and not default_ic.isNull():
            self.defaultBtn.setIcon(default_ic); self.defaultBtn.setIconSize(QtCore.QSize(16,16))
        else:
            self.defaultBtn.setText("A")

        menu = QtWidgets.QMenu(self.defaultBtn)
        for nm,_sh in tangents:
            act_icon = self.icon_cache.get(nm, QtGui.QIcon())
            a = QtWidgets.QAction(act_icon, nm, menu)
            def _set(nm=nm):
                ic = self.icon_cache.get(nm)
                if ic and not ic.isNull():
                    self.defaultBtn.setIcon(ic); self.defaultBtn.setText("")
                else:
                    self.defaultBtn.setIcon(QtGui.QIcon()); self.defaultBtn.setText(nm[:2] if nm!="Auto" else "A")
            a.triggered.connect(_set)
            menu.addAction(a)
        self.defaultBtn.setMenu(menu); self.defaultBtn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        row.addWidget(self.defaultBtn, 0)

        v.addLayout(row)
        v.addWidget(hline())

        def two(a,b):
            h = QtWidgets.QHBoxLayout(); h.setContentsMargins(QS_LRM,0,QS_LRM,0); h.setSpacing(QS_COL_GAP)
            h.addWidget(push_btn(a,QS_COL_W)); h.addWidget(push_btn(b,QS_COL_W)); return h
        v.addLayout(two("Snap","Snap Key"))
        v.addLayout(two("Graph Editor","Dope Sheet"))

        row2 = QtWidgets.QHBoxLayout(); row2.setContentsMargins(QS_LRM,0,QS_LRM,0); row2.setSpacing(QS_COL_GAP)
        row2.addWidget(push_btn("Incremental Save", QS_COL_W))
        right_wrap = QtWidgets.QWidget(); right_wrap.setFixedSize(QS_COL_W, BTN_H)
        rw = QtWidgets.QHBoxLayout(right_wrap); rw.setContentsMargins(0,0,0,0); rw.setSpacing(0)
        rw.addStretch(1)
        self.cb_maya_inc = QtWidgets.QCheckBox("Maya Increments"); self.cb_maya_inc.setChecked(True); self.cb_maya_inc.setFixedHeight(BTN_H)
        rw.addWidget(self.cb_maya_inc, 0, QtCore.Qt.AlignVCenter)
        rw.addStretch(1)
        row2.addWidget(right_wrap)
        v.addLayout(row2)

        end = QtWidgets.QHBoxLayout(); end.setContentsMargins(GUTTER,0,GUTTER,0)
        end.addWidget(push_btn("animBLAST", W_CONTENT - 2*GUTTER, BTN_H_LG)); v.addLayout(end)

# ---------- Dockable window ----------
class TradigiToolsDock(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(APP_ID); self.setWindowTitle(TITLE)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.setFixedWidth(W_CONTENT + 2*GUTTER)

        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(GUTTER, GUTTER//2, GUTTER, GUTTER//2); main.setSpacing(SPACING)

        self.tabs = QtWidgets.QTabWidget(); self.tabs.setDocumentMode(True); main.addWidget(self.tabs)

        # corner dock buttons
        corner = QtWidgets.QWidget(); ch = QtWidgets.QHBoxLayout(corner)
        ch.setContentsMargins(0,0,0,0); ch.setSpacing(4)
        def load_cand(c): 
            ic = _load_from_candidates(c); return ic if ic else QtGui.QIcon()
        left_ic, float_ic = load_cand(DOCK_LEFT_CANDS), load_cand(DOCK_FLOAT_CANDS)
        right_ic = mirrored_icon(left_ic) if not left_ic.isNull() else QtGui.QIcon()
        def dock_tool(icon, glyph, tip, slot):
            if icon and not icon.isNull():
                t = QtWidgets.QToolButton(); t.setAutoRaise(True); t.setFixedSize(18,18)
                t.setCursor(QtCore.Qt.PointingHandCursor); t.setIcon(icon); t.setIconSize(QtCore.QSize(16,16))
                t.setToolTip(tip)
                t.setStyleSheet("QToolButton{border:0;background:transparent;border-radius:3px;}"+
                                "QToolButton:hover{background:rgba(255,255,255,0.12);}"+
                                "QToolButton:pressed{background:rgba(255,255,255,0.20);}")
                t.clicked.connect(slot); return t
            return glyph_tool(glyph, tip, slot)
        self.btn_dock_left  = dock_tool(left_ic,  "⟸", "Dock left (inner lane)",  self._dock_left)
        self.btn_float      = dock_tool(float_ic, "□",  "Float window",           self._float_window)
        self.btn_dock_right = dock_tool(right_ic, "⟹", "Dock right (inner lane)", self._dock_right)
        ch.addWidget(self.btn_dock_left); ch.addWidget(self.btn_float); ch.addWidget(self.btn_dock_right)
        self.tabs.setCornerWidget(corner, QtCore.Qt.TopRightCorner)

        # aniMATE
        t1 = QtWidgets.QWidget(); self.tabs.addTab(t1, "aniMATE")
        t1v = QtWidgets.QVBoxLayout(t1); t1v.setContentsMargins(0,TOP_GAP,0,0); t1v.setSpacing(SPACING)

        def add_section(title, widget):
            sec = Collapsible(title, widget, start_open=True, top_gap=TOP_GAP)
            t1v.addWidget(sec); sec.toggled.connect(self.request_fit_to_contents)
        add_section("keyCONTROL", KeyControl())
        add_section("timeSHIFT",  TimeShift())
        add_section("viewSWITCH", ViewSwitch())
        add_section("quickSELECT",QuickSelect())
        t1v.addStretch(1)  # keep top-aligned

        # aniMASK placeholder
        t2 = QtWidgets.QWidget(); self.tabs.addTab(t2, "aniMASK")
        QtWidgets.QVBoxLayout(t2).addStretch(1)

        main.addWidget(hline())
        vr = QtWidgets.QHBoxLayout(); vr.setContentsMargins(0,0,0,0); vr.setSpacing(0)
        vr.addStretch(1)
        ver = QtWidgets.QLabel(__ui_version__); ver.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter); ver.setFixedHeight(16)
        vr.addWidget(ver); main.addLayout(vr)

        self._fit_timer0 = QtCore.QTimer(self); self._fit_timer0.setSingleShot(True)
        self._fit_timer1 = QtCore.QTimer(self); self._fit_timer1.setSingleShot(True)
        self._fit_timer0.timeout.connect(self._do_fit_to_contents)
        self._fit_timer1.timeout.connect(self._do_fit_to_contents)
        self.tabs.currentChanged.connect(self.request_fit_to_contents)
        QtCore.QTimer.singleShot(0, self._post_show)

    # --- docking helpers / layout fit ---
    def _workspace_control_name(self):
        try: return self.workspaceControlName()
        except Exception: return None
    def _delete_wc_if_exists(self):
        try:
            wc = self._workspace_control_name()
            if wc and cmds.workspaceControl(wc, q=True, exists=True):
                cmds.deleteUI(wc)
        except Exception: pass
    def _dock_to_side(self, side:str):
        try: self.show(dockable=True, floating=False, area=side, retain=True)
        except Exception: self.show()
        wc = self._workspace_control_name()
        try:
            targets = ["ToolSettings","Outliner"] if side=='left' else ["ChannelBoxLayerEditor","AttributeEditor"]
            for tgt in targets:
                if cmds.workspaceControl(tgt, q=True, exists=True):
                    cmds.workspaceControl(wc, e=True, tabToControl=(tgt, -1)); break
            else:
                cmds.workspaceControl(wc, e=True, dockToMainWindow=(side, 1))
        except Exception: pass
        self.request_fit_to_contents()
    def _dock_left(self):  self._delete_wc_if_exists(); self._dock_to_side('left')
    def _dock_right(self): self._delete_wc_if_exists(); self._dock_to_side('right')
    def _float_window(self):
        self._delete_wc_if_exists()
        try: self.show(dockable=True, floating=True, area='right')
        except Exception: self.show()
        self.request_fit_to_contents()
    def request_fit_to_contents(self, *args):
        self._do_fit_to_contents()
        self._fit_timer0.start(0); self._fit_timer1.start(50)
    def _post_show(self): self.request_fit_to_contents()
    def _is_docked(self) -> bool:
        try:
            wc = self.workspaceControlName()
            return bool(wc and cmds.workspaceControl(wc, q=True, exists=True)
                        and not cmds.workspaceControl(wc, q=True, isFloating=True))
        except Exception: return False
    def _apply_size_policy(self, content_h:int):
        if self._is_docked():
            self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
            self.setMinimumHeight(content_h); self.setMaximumHeight(16777215)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            self.setMinimumHeight(content_h); self.setMaximumHeight(content_h)
    def _do_fit_to_contents(self):
        self.layout().activate()
        for tl in self.findChildren(QtWidgets.QLayout): tl.activate()
        h = self.sizeHint().height(); self._apply_size_policy(h); self.resize(self.width(), h)
        try:
            wc = self.workspaceControlName()
            if wc and cmds.workspaceControl(wc, q=True, exists=True):
                cmds.workspaceControl(wc, e=True, restore=True)
        except Exception: pass
        QtWidgets.QApplication.processEvents(QtCore.QEventLoop.AllEvents, 20)

# ---------- show ----------
_UI = None
def show_tradigiTOOLS():
    global _UI
    try:
        if _UI and _UI.isVisible(): _UI.close(); _UI.deleteLater()
    except Exception: pass
    _UI = TradigiToolsDock()
    try: _UI.show(dockable=True, floating=True, area='right')
    except Exception: _UI.show()
    _UI.request_fit_to_contents()
    return _UI

if __name__ == "__main__":
    show_tradigiTOOLS()
