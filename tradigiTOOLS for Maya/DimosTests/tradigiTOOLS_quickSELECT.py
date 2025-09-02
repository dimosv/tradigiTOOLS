# tradigiTOOLS_quickSELECT_tangentStrip.py
# Tangent row centered. Spacing: 6px under divider, 4px elsewhere (rows + center gutters).
# Incremental Save row: equal column widths; checkbox padded inside the right half.
# Tangent icons act on selected objects in highlighted range if present, else playback range.

import os, re
import maya.cmds as cmds

# ---------- Icons ----------
_ICON_CANDIDATES = {
    "auto":     ["autoTangent.png", "autoTangent.xpm"],
    "spline":   ["splineTangent.png", "splineTangent.xpm"],
    "linear":   ["linearTangent.png", "linearTangent.xpm"],
    "clamped":  ["clampedTangent.png", "clampedTangent.xpm"],
    "flat":     ["flatTangent.png", "flatTangent.xpm"],
    "plateau":  ["plateauTangent.png", "plateauTangent.xpm"],
    "step":     ["stepTangent.png", "stepTangent.xpm", "steppedTangent.png", "steppedTangent.xpm"],
}
_FALLBACK_ICON = "menuIconWindow.png"

def _find_icon(name_list):
    for n in name_list:
        try:
            hits = cmds.resourceManager(nameFilter=n) or []
            if any(h.endswith(n) or h == n for h in hits):
                return n
        except Exception:
            pass
    return _FALLBACK_ICON

_ICONS = {k: _find_icon(v) for k, v in _ICON_CANDIDATES.items()}
_LABELS = {"auto":"Auto","spline":"Spline","linear":"Linear","clamped":"Clamped","flat":"Flat","plateau":"Plateau","step":"Stepped"}

# ---------- Tangent mappings ----------
_APPLY_IOTT = {
    "auto":("auto","auto"),
    "spline":("spline","spline"),
    "linear":("linear","linear"),
    "clamped":("clamped","clamped"),
    "flat":("flat","flat"),
    "plateau":("plateau","plateau"),
    "step":("clamped","step"),
}
_SET_GLOBAL = {
    "auto":("auto","auto"),
    "spline":("spline","spline"),
    "linear":("linear","linear"),
    "clamped":("clamped","clamped"),
    "flat":("flat","flat"),
    "plateau":("plateau","plateau"),
    "step":("clamped","stepped"),
}
_PREF_SET = _SET_GLOBAL.copy()

# ---------- Prefs + current default ----------
def _norm(v):
    if isinstance(v,(list,tuple)):
        v = v[0] if v else ""
    return (v or "").strip().lower()

def _has_keyTangentPref():
    try:
        import maya.mel as mel
        return not mel.eval('whatIs "keyTangentPref";').lower().startswith("unknown")
    except Exception:
        return False

def _read_pref_pair():
    if not _has_keyTangentPref(): return None
    try:
        import maya.mel as mel
        it = _norm(mel.eval('keyTangentPref -q -itt;'))
        ot = _norm(mel.eval('keyTangentPref -q -ott;'))
        return it, ot
    except Exception:
        return None

def _read_global_pair():
    try:
        it = _norm(cmds.keyTangent(q=True, g=True, itt=True))
        ot = _norm(cmds.keyTangent(q=True, g=True, ott=True))
        return it, ot
    except Exception:
        return "", ""

def _pair_to_kind(it, ot):
    itn = "stepped" if it in ("step","stepped") else it
    otn = "stepped" if ot in ("step","stepped") else ot
    if otn == "stepped": return "step"
    if itn == otn:
        if itn in ("auto","spline","linear","clamped","flat","plateau"): return itn
        if itn == "stepped": return "step"
    return "step" if otn == "stepped" else (ot if ot in ("auto","spline","linear","clamped","flat","plateau") else "auto")

def _current_default_kind():
    pr = _read_pref_pair()
    if pr: return _pair_to_kind(pr[0], pr[1])
    it, ot = _read_global_pair()
    return _pair_to_kind(it, ot)

def _set_global_pair(itt, ott):
    try:
        cmds.keyTangent(e=True, g=True, itt=itt, ott=ott); return True
    except Exception:
        pass
    ok = False
    try: cmds.keyTangent(e=True, g=True, itt=itt); ok = True
    except Exception: ok = False
    try: cmds.keyTangent(e=True, g=True, ott=ott); ok = True and ok
    except Exception: pass
    return ok

def _confirm_kind(kind): return _current_default_kind() == kind

def _set_global_kind(kind):
    if kind != "step":
        gi, go = _SET_GLOBAL.get(kind, ("auto","auto"))
        if _set_global_pair(gi, go) and _confirm_kind(kind): return True
        if _set_global_pair(gi, go) and _confirm_kind(kind): return True
        return False
    for gi,go in [("clamped","stepped"),("clamped","step"),("stepped","stepped"),("step","step")]:
        if _set_global_pair(gi,go) and _confirm_kind("step"): return True
    it,ot = _read_global_pair()
    if ot in ("stepped","step") and it != "clamped":
        if _set_global_pair("clamped",ot) and _confirm_kind("step"): return True
    return False

def _set_prefs_kind(kind):
    if not _has_keyTangentPref(): return False
    itt, ott = _PREF_SET.get(kind, ("auto","auto"))
    try:
        import maya.mel as mel
        mel.eval('keyTangentPref -e -itt "{0}" -ott "{1}";'.format(itt, ott))
        return True
    except Exception:
        if kind == "step":
            for gi,go in [("clamped","step"),("stepped","stepped"),("step","step")]:
                try:
                    import maya.mel as mel
                    mel.eval('keyTangentPref -e -itt "{0}" -ott "{1}";'.format(gi, go))
                    return True
                except Exception:
                    pass
    return False

# ---------- Targeting ----------
def _timeslider_range():
    for tc in ('$gPlayBackSlider','timeControl1'):
        try:
            if cmds.timeControl(tc, q=True, rangeVisible=True):
                ra = cmds.timeControl(tc, q=True, rangeArray=True)
                if ra and len(ra)==2: return (ra[0], ra[1])
        except Exception:
            pass
    return None

def _playback_range():
    try:
        return (cmds.playbackOptions(q=True, min=True),
                cmds.playbackOptions(q=True, max=True))
    except Exception:
        return (0.0, 1.0)

def _selected_transforms():
    sel = cmds.ls(sl=True, long=True) or []
    out, seen = [], set()
    for s in sel:
        t = s
        if cmds.nodeType(t) != "transform":
            p = cmds.listRelatives(t, p=True, f=True) or []
            if not p: continue
            t = p[0]
        if t not in seen:
            out.append(t); seen.add(t)
    return out

def _count_keys(targets, time_range):
    try:
        kc = cmds.keyframe(targets, q=True, kc=True, time=time_range)
        if kc is None: return 0
        if isinstance(kc, (list, tuple)): return sum(int(x or 0) for x in kc)
        return int(kc)
    except Exception:
        return 0

def _apply_kind(kind):
    targets = _selected_transforms()
    if not targets:
        print("// tradigiTOOLS: No objects selected.")
        return
    tr = _timeslider_range() or _playback_range()
    pre_count = _count_keys(targets, tr)

    gi, go = _APPLY_IOTT.get(kind, ("auto","auto"))
    cmds.undoInfo(openChunk=True)
    try:
        try:
            cmds.keyTangent(targets, e=True, itt=gi, ott=go, time=tr)
        except Exception:
            if kind == "step":
                for gi2, go2 in [("clamped","stepped"), ("clamped","step"), ("stepped","stepped"), ("step","step")]:
                    try:
                        cmds.keyTangent(targets, e=True, itt=gi2, ott=go2, time=tr)
                        break
                    except Exception:
                        pass
    finally:
        cmds.undoInfo(closeChunk=True)

    if pre_count > 0:
        try:
            cmds.inViewMessage(amg='Set <hl>{0}</hl> on {1} key{2}'.format(
                _LABELS.get(kind, kind.title()), pre_count, "" if pre_count==1 else "s"), pos='midCenter', fade=True)
        except Exception:
            pass

# ---------- Snap / Editors / Save / Blast ----------
def _snap(set_keys=False):
    sel = cmds.ls(sl=True, long=True) or []
    if len(sel) < 2:
        cmds.warning("Select child(ren) first, then the parent target."); return
    target = sel[-1]; children = sel[:-1]
    try:
        m = cmds.xform(target, q=True, ws=True, matrix=True)
        for c in children:
            if cmds.nodeType(c) != "transform":
                p = cmds.listRelatives(c, p=True, f=True) or []
                if not p: continue
                c = p[0]
            cmds.xform(c, ws=True, matrix=m)
            if set_keys:
                for a in ("tx","ty","tz","rx","ry","rz","sx","sy","sz"):
                    try: cmds.setKeyframe(c, at=a)
                    except Exception: pass
        try: cmds.inViewMessage(amg='Snap{0} done'.format(" + Key" if set_keys else ""), pos='midCenter', fade=True)
        except Exception: pass
    except Exception as e:
        cmds.warning("Snap failed: %s" % e)

def _toggle_graph_editor():
    import maya.mel as mel
    wins = [w for w in (cmds.lsUI(windows=True) or []) if "graphEditor" in w or "GraphEditor" in w]
    if wins:
        try: cmds.deleteUI(wins[0]); return
        except Exception: pass
    try: mel.eval('GraphEditor;')
    except Exception: cmds.warning("Could not open Graph Editor.")

def _toggle_dope_sheet():
    import maya.mel as mel
    wins = [w for w in (cmds.lsUI(windows=True) or []) if "dope" in w.lower()]
    if wins:
        try: cmds.deleteUI(wins[0]); return
        except Exception: pass
    try: mel.eval('DopeSheetEditor;')
    except Exception: cmds.warning("Could not open Dope Sheet.")

def _maya_incremental_save():
    try:
        import maya.mel as mel
        mel.eval('incrementalSave;'); return True
    except Exception:
        return False

_version_re = re.compile(r"(.*?)(_v)(\d{4})(\.[^./\\]+)$", re.IGNORECASE)

def _tool_incremental_save():
    scene = cmds.file(q=True, sn=True)
    if not scene:
        cmds.warning("Save the scene once (File > Save Scene As) before using Incremental Save.")
        try: cmds.inViewMessage(amg='Save the scene first, then press <hl>Incremental Save</hl>.', pos='midCenter', fade=True)
        except Exception: pass
        return False
    folder, name = os.path.split(scene)
    m = _version_re.match(name)
    if m:
        base, tag, num, ext = m.groups(); n = int(num) + 1
        new_name = f"{base}{tag}{n:04d}{ext}"
    else:
        base, ext = os.path.splitext(name)
        new_name = f"{base}_v0001{ext}"
    new_path = os.path.join(folder, new_name)
    try:
        cmds.file(rename=new_path); cmds.file(save=True, f=True)
        try: cmds.inViewMessage(amg='Saved <hl>{0}</hl>'.format(os.path.basename(new_path)), pos='midCenter', fade=True)
        except Exception: pass
        return True
    except Exception as e:
        cmds.warning("Incremental save failed: %s" % e); return False

def _incremental_save(use_maya_inc=True):
    if use_maya_inc and _maya_incremental_save(): return
    _tool_incremental_save()

def _anim_blast():
    st = cmds.playbackOptions(q=True, min=True)
    et = cmds.playbackOptions(q=True, max=True)
    try:
        cmds.playblast(st=st, et=et, viewer=True, showOrnaments=False, percent=100,
                       quality=70, offScreen=True, fo=True)
    except Exception:
        cmds.playblast(st=st, et=et)

# ---------- UI ----------
def _build_strip():
    win = "tradigi_tangent_strip"
    if cmds.window(win, exists=True):
        try: cmds.deleteUI(win)
        except Exception: pass

    WINDOW_W = 320
    cmds.window(win, t="tangent strip", wh=(WINDOW_W, 190), s=False)
    root = cmds.formLayout()

    LM, GAP, H, W = 7, 2, 24, 24  # margins, icon size

    # --- Tangent strip (centered) ---
    total_w = (7*W + 6*GAP) + 4 + 4 + 4 + W  # icons + 4 gap + divider + 4 gap + badge
    LM_CENTER = max(4, int((WINDOW_W - total_w) / 2))

    order = ["auto","spline","linear","clamped","flat","plateau","step"]
    prev = None
    for idx, k in enumerate(order):
        img = _ICONS[k]; tip = _LABELS[k]
        try:
            ctrl = cmds.iconTextButton(style="iconOnly", image=img, w=W, h=H, ann=tip, parent=root)
        except Exception:
            ctrl = cmds.button(l=tip, w=W, h=H, ann=tip, parent=root)

        if idx == 0:
            cmds.formLayout(root, e=True, attachForm=[(ctrl,"top",6),(ctrl,"left",LM_CENTER)])
        else:
            cmds.formLayout(root, e=True, attachControl=[(ctrl,"left",GAP,prev)],
                            attachPosition=[(ctrl,"top",6,0)])
        prev = ctrl

        if cmds.objectTypeUI(ctrl) == "iconTextButton":
            cmds.iconTextButton(ctrl, e=True, c=lambda *_, kk=k: _apply_kind(kk))
        else:
            cmds.button(ctrl, e=True, c=lambda *_, kk=k: _apply_kind(kk))

    gap_div = cmds.separator(style="none", hr=False, w=4, h=H, parent=root)
    cmds.formLayout(root, e=True, attachControl=[(gap_div,"left",4,prev)],
                    attachPosition=[(gap_div,"top",6,0)])

    div = cmds.separator(style="single", hr=False, w=4, h=H-6, parent=root)
    cmds.formLayout(root, e=True, attachControl=[(div,"left",0,gap_div)],
                    attachPosition=[(div,"top",9,0)])

    badge_gap = cmds.separator(style="none", hr=False, w=4, h=H, parent=root)
    cmds.formLayout(root, e=True, attachControl=[(badge_gap,"left",0,div)],
                    attachPosition=[(badge_gap,"top",6,0)])

    cur_kind = _current_default_kind()
    badge = cmds.iconTextButton(style="iconOnly", image=_ICONS.get(cur_kind, _FALLBACK_ICON),
                                w=W, h=H,
                                ann="Default (new keys): {0}".format(_LABELS.get(cur_kind, cur_kind.title())),
                                parent=root)
    cmds.formLayout(root, e=True, attachControl=[(badge,"left",0,badge_gap)],
                    attachPosition=[(badge,"top",6,0)])

    # Popup menu on badge (left + right click)
    pm_left  = cmds.popupMenu(parent=badge, button=1)
    pm_right = cmds.popupMenu(parent=badge, button=3)

    def _badge_set_icon(kind):
        img = _ICONS.get(kind, _FALLBACK_ICON)
        try:
            cmds.iconTextButton(badge, e=True, image=img,
                                ann="Default (new keys): {0}".format(_LABELS.get(kind, kind.title())))
        except Exception: pass

    def _set_default_from_menu(kind):
        ok_runtime = _set_global_kind(kind if kind != "step" else "step")
        _set_prefs_kind(kind)
        if ok_runtime: _badge_set_icon(_current_default_kind())
        else: cmds.warning("Failed to set runtime default.")

    def _populate_menu(menu_name, *_):
        cmds.setParent(menu_name, menu=True); cmds.popupMenu(menu_name, e=True, dai=True)
        cur_kind2 = _current_default_kind()
        cmds.menuItem(enable=False, l="Current: {0}".format(_LABELS.get(cur_kind2, cur_kind2.title())),
                      image=_ICONS.get(cur_kind2, _FALLBACK_ICON))
        cmds.menuItem(divider=True)
        for k in ["auto","spline","linear","clamped","flat","plateau","step"]:
            cmds.menuItem(l=_LABELS[k], image=_ICONS.get(k, _FALLBACK_ICON),
                          c=lambda *_, kk=k: _set_default_from_menu(kk))

    cmds.popupMenu(pm_left,  e=True, postMenuCommand=lambda *args: _populate_menu(pm_left))
    cmds.popupMenu(pm_right, e=True, postMenuCommand=lambda *args: _populate_menu(pm_right))

    # --- horizontal divider under tangent row ---
    hdiv = cmds.separator(style="single", hr=True, parent=root)
    cmds.formLayout(root, e=True,
        attachForm=[(hdiv,"left",LM),(hdiv,"right",LM)],
        attachControl=[(hdiv,"top",6,badge)])  # 6px

    # -------- helpers: paired rows --------
    def _pair_buttons(parent_top, left_label, left_ann, left_cmd,
                      right_label, right_ann, right_cmd):
        row = cmds.formLayout(parent=root)
        cmds.formLayout(root, e=True,
            attachForm=[(row,"left",LM),(row,"right",LM)],
            attachControl=[(row,"top",4,parent_top)])  # 4px between rows

        # center spacer = 4px wide, pinned to 50%
        mid = cmds.separator(parent=row, style="none", hr=False, h=H, w=4)
        cmds.formLayout(row, e=True,
            attachPosition=[(mid,"left",-2,50),(mid,"right",2,50)],
            attachForm=[(mid,"top",0)])

        left_btn = cmds.button(parent=row, l=left_label, h=H, ann=left_ann)
        cmds.formLayout(row, e=True,
            attachForm=[(left_btn,"left",0),(left_btn,"top",0)],
            attachControl=[(left_btn,"right",0,mid)])
        if left_cmd: cmds.button(left_btn, e=True, c=left_cmd)

        right_btn = cmds.button(parent=row, l=right_label, h=H, ann=right_ann)
        cmds.formLayout(row, e=True,
            attachForm=[(right_btn,"right",0),(right_btn,"top",0)],
            attachControl=[(right_btn,"left",0,mid)])
        if right_cmd: cmds.button(right_btn, e=True, c=right_cmd)

        return row, left_btn, right_btn

    def _pair_button_checkbox_paddedRight(parent_top, btn_label, btn_ann, btn_cmd,
                                          cb_label, cb_ann, cb_default=True, pad_left=4):
        """Equal column widths. Checkbox sits in a right-half container with left padding."""
        row = cmds.formLayout(parent=root)
        cmds.formLayout(root, e=True,
            attachForm=[(row,"left",LM),(row,"right",LM)],
            attachControl=[(row,"top",4,parent_top)])  # 4px between rows

        # center spacer = 4px at 50%
        mid = cmds.separator(parent=row, style="none", hr=False, h=H, w=4)
        cmds.formLayout(row, e=True,
            attachPosition=[(mid,"left",-2,50),(mid,"right",2,50)],
            attachForm=[(mid,"top",0)])

        # Left half: full width button up to mid
        btn = cmds.button(parent=row, l=btn_label, h=H, ann=btn_ann)
        cmds.formLayout(row, e=True,
            attachForm=[(btn,"left",0),(btn,"top",0)],
            attachControl=[(btn,"right",0,mid)])
        if btn_cmd: cmds.button(btn, e=True, c=btn_cmd)

        # Right half: container with internal left padding; checkbox inside
        rightPane = cmds.formLayout(parent=row)
        cmds.formLayout(row, e=True,
            attachForm=[(rightPane,"right",0),(rightPane,"top",0)],
            attachControl=[(rightPane,"left",0,mid)])

        cb = cmds.checkBox(parent=rightPane, l=cb_label, v=cb_default, h=H, ann=cb_ann)
        cmds.formLayout(rightPane, e=True,
            attachForm=[(cb,"top",0),(cb,"right",0),(cb,"left",pad_left)])

        return row, btn, cb

    # --- Snap / Snap Key ---
    row1, snap_btn, snapk_btn = _pair_buttons(
        hdiv,
        "Snap", "Match child(ren) to last-selected parent (no keys)", lambda *_: _snap(False),
        "Snap Key", "Snap + set keys on child(ren)", lambda *_: _snap(True)
    )

    # --- Graph Editor / Dope Sheet ---
    row2, ge_btn, ds_btn = _pair_buttons(
        row1,
        "Graph Editor", "Open/Close Graph Editor", lambda *_: _toggle_graph_editor(),
        "Dope Sheet",   "Open/Close Dope Sheet",   lambda *_: _toggle_dope_sheet()
    )

    # --- Incremental Save / Maya Increments (right padded) ---
    row3, inc_btn, inc_cb = _pair_button_checkbox_paddedRight(
        row2,
        "Incremental Save", "Save new version of the scene", None,
        "Maya Increments",  "On: use Maya's incremental save. Off: _v#### tool save.", True, pad_left=4
    )
    cmds.button(inc_btn, e=True, c=lambda *_, cb=inc_cb: _incremental_save(cmds.checkBox(cb, q=True, v=True)))

    # --- animBLAST ---
    blast_btn = cmds.button(l="animBLAST", h=H, ann="Playblast with standard settings", parent=root)
    cmds.formLayout(root, e=True,
        attachForm=[(blast_btn,"left",LM),(blast_btn,"right",LM)],
        attachControl=[(blast_btn,"top",4,row3)])

    cmds.showWindow(win)

# ---- entry points ----
def tdt_quickSELECT_tangent_strip_SAFE(): _build_strip()
def tdt_quickSELECT_tangent_strip():      _build_strip()

if __name__ == "__main__":
    tdt_quickSELECT_tangent_strip_SAFE()
