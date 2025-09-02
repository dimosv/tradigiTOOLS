import maya.cmds as cmds

_CAM_OPTVAR = "tradigi_cam_default"

# ---------- camera helpers ----------
def _cams_list(include_ortho=False):
    cams = cmds.ls(type='camera') or []
    out = []
    for shape in cams:
        if not cmds.objExists(shape): continue
        if shape == "perspShape":     continue
        if cmds.getAttr(shape + ".orthographic") and not include_ortho:
            continue
        tr = (cmds.listRelatives(shape, p=True, f=False) or [None])[0]
        if tr: out.append(tr)
    return sorted(out, key=lambda x: x.lower())

def _populate_menu(menu, include_ortho=False):
    for mi in cmds.optionMenu(menu, q=True, ill=True) or []:
        cmds.deleteUI(mi)
    cmds.menuItem(label="None", parent=menu)
    items = _cams_list(include_ortho)
    for cam in items:
        cmds.menuItem(label=cam, parent=menu)
    sel = "None"
    if items and cmds.optionVar(exists=_CAM_OPTVAR):
        last = cmds.optionVar(q=_CAM_OPTVAR)
        if last in items: sel = last
    cmds.optionMenu(menu, e=True, v=sel)
    return items

def _get_model_panel():
    p = cmds.getPanel(withFocus=True)
    if p and cmds.getPanel(typeOf=p) == "modelPanel": return p
    for mp in cmds.getPanel(vis=True) or []:
        if cmds.getPanel(typeOf=mp) == "modelPanel": return mp
    return None

def _current_camera_name():
    pan = _get_model_panel()
    return cmds.modelPanel(pan, q=True, cam=True) if pan else None

# ---------- UI refresh ----------
def _update_current_label(menu, current_label):
    sel = cmds.optionMenu(menu, q=True, v=True)
    cmds.text(current_label, e=True, label=("Current: %s" % (sel if sel!="None" else "No Selected Camera")))

def _refresh_switch_button(menu, switch_btn):
    sel = cmds.optionMenu(menu, q=True, v=True)
    if sel == "None" or not cmds.objExists(sel):
        cmds.button(switch_btn, e=True, label="setSWITCH", enable=True); return
    cmds.optionVar(sv=(_CAM_OPTVAR, sel))
    cur = _current_camera_name()
    lbl = "camSWITCH" if (cur == "persp" or cur != sel) else "perspSWITCH"
    cmds.button(switch_btn, e=True, label=lbl, enable=True)

def _repopulate_and_refresh(menu, orthos_cb, current_lbl, switch_btn):
    _populate_menu(menu, include_ortho=cmds.checkBox(orthos_cb, q=True, v=True))
    _update_current_label(menu, current_lbl)
    _refresh_switch_button(menu, switch_btn)

# ---------- actions ----------
def _do_switch(menu, switch_btn, open_options_fn):
    sel = cmds.optionMenu(menu, q=True, v=True)
    if sel == "None" or not cmds.objExists(sel):
        open_options_fn(); return
    pan = _get_model_panel()
    if not pan: cmds.warning("No modelPanel in focus."); return
    cur = cmds.modelPanel(pan, q=True, cam=True)
    cmds.modelEditor(pan, e=True, camera=(sel if cur=="persp" or cur!=sel else "persp"))
    _refresh_switch_button(menu, switch_btn)

def _create_shotcam(name_field, persp_copy_cb, menu, orthos_cb, cur_label, switch_btn):
    base = cmds.textField(name_field, q=True, text=True).strip() or "shotCam"
    tr = cmds.rename(cmds.createNode("transform", n=base), base)
    shp = cmds.createNode("camera", n=tr+"Shape", p=tr)
    cmds.setAttr(shp+".orthographic", 0)
    if cmds.checkBox(persp_copy_cb, q=True, v=True) and cmds.objExists("perspShape"):
        t = cmds.xform("persp", q=True, ws=True, t=True)
        r = cmds.xform("persp", q=True, ws=True, ro=True)
        cmds.xform(tr, ws=True, t=t); cmds.xform(tr, ws=True, ro=r)
        for a in ("focalLength","horizontalFilmAperture","verticalFilmAperture",
                  "lensSqueezeRatio","nearClipPlane","farClipPlane"):
            try: cmds.setAttr(shp+"."+a, cmds.getAttr("perspShape."+a))
            except: pass
    else:
        cmds.xform(tr, ws=True, t=[0,0,0]); cmds.xform(tr, ws=True, ro=[0,0,0])

    # repopulate & select new cam
    _populate_menu(menu, include_ortho=cmds.checkBox(orthos_cb, q=True, v=True))
    if cmds.objExists(tr):
        cmds.optionMenu(menu, e=True, v=tr); cmds.optionVar(sv=(_CAM_OPTVAR, tr))
    _update_current_label(menu, cur_label); _refresh_switch_button(menu, switch_btn)

    # clear input after create
    cmds.textField(name_field, e=True, text="")
    cmds.inViewMessage(amg='Created <hl>%s</hl>' % tr, pos='midCenter', fade=True)

# ---------- light + auto-aware watchers ----------
def _setup_camera_watchers(parent_window, menu, orthos_cb, current_lbl, switch_btn):
    cmds.scriptJob(e=["DagObjectCreated", lambda *a:_repopulate_and_refresh(menu, orthos_cb, current_lbl, switch_btn)],
                   parent=parent_window, protected=True)
    cmds.scriptJob(e=["SceneOpened",     lambda *a:_repopulate_and_refresh(menu, orthos_cb, current_lbl, switch_btn)],
                   parent=parent_window, protected=True)

# ---------- Mini-Test UI ----------
def test_viewSWITCH_v16():
    win = "testViewSWITCHv16"
    if cmds.window(win, exists=True): cmds.deleteUI(win)
    cmds.window(win, title="viewSWITCH v16", widthHeight=(306, 250), sizeable=False)
    root = cmds.formLayout()

    title = cmds.text(label="▼ viewSWITCH ▼", align="center", height=20)
    cmds.formLayout(root, e=True, attachForm=[(title,"top",5),(title,"left",0),(title,"right",0)])

    switch_btn = cmds.button(label="setSWITCH", height=24, width=294)
    cmds.formLayout(root, e=True, attachForm=[(switch_btn,"top",30),(switch_btn,"left",7)])

    toggle_btn  = cmds.button(label="▸ options", height=20, width=80, align="left")
    current_lbl = cmds.text(label="Current: No Selected Camera", align="right", height=20)
    cmds.formLayout(root, e=True,
        attachForm=[(toggle_btn,"top",56),(toggle_btn,"left",7),
                    (current_lbl,"top",58),(current_lbl,"right",7)],
        attachControl=[(current_lbl,"left",6,toggle_btn)]
    )

    details = cmds.formLayout(visible=False)  # collapsed by default
    cmds.formLayout(root, e=True, attachForm=[(details,"left",0),(details,"right",0)],
                    attachControl=[(details,"top",4,toggle_btn)])

    # CAM row: CAM | menu expands | ↻ | Orthos (right)
    cam_lbl   = cmds.text(label="CAM", align="left", width=40, height=20)
    cam_menu  = cmds.optionMenu(width=120,
        postMenuCommand=lambda *_:_repopulate_and_refresh(cam_menu, orthos_cb, current_lbl, switch_btn))
    refresh   = cmds.button(label="↻", width=22, height=20,
        c=lambda *_:_repopulate_and_refresh(cam_menu, orthos_cb, current_lbl, switch_btn))
    orthos_cb = cmds.checkBox(label="Orthos", v=False)

    cmds.formLayout(details, e=True,
        attachForm=[(cam_lbl,"left",7),(cam_lbl,"top",0),
                    (orthos_cb,"top",0),(orthos_cb,"right",7),
                    (cam_menu,"top",0),(refresh,"top",0)],
        attachControl=[(cam_menu,"left",6,cam_lbl),
                       (refresh,"left",6,cam_menu),
                       (orthos_cb,"left",6,refresh)]
    )

    # makeCAM row: makeCAM | input(140) | Camera.png (right)
    make_lbl   = cmds.text(label="makeCAM", align="left", width=60, height=20)
    name_field = cmds.textField(width=140, text="", placeholderText="input camera name here")
    create_btn = cmds.iconTextButton(style="iconOnly", image="Camera.png", width=24, height=24,
                                     annotation="Create new shotCAM")

    cmds.formLayout(details, e=True,
        attachControl=[(make_lbl,"top",8,cam_menu)],
        attachForm=[(make_lbl,"left",7)]
    )
    cmds.formLayout(details, e=True,
        attachControl=[(create_btn,"top",4,cam_menu)],
        attachForm=[(create_btn,"right",7)]
    )
    cmds.formLayout(details, e=True,
        attachControl=[(name_field,"top",6,cam_menu),(name_field,"left",6,make_lbl),
                       (name_field,"right",6,create_btn)]
    )

    # perspCOPY below
    persp_copy = cmds.checkBox(label="perspCOPY", v=True)
    cmds.formLayout(details, e=True,
        attachControl=[(persp_copy,"top",6,name_field)],
        attachForm=[(persp_copy,"left",7)]
    )

    # initial populate/state
    _populate_menu(cam_menu, include_ortho=False)
    _update_current_label(cam_menu, current_lbl)
    _refresh_switch_button(cam_menu, switch_btn)

    # wiring
    def open_options():
        cmds.formLayout(details, e=True, visible=True)
        cmds.button(toggle_btn, e=True, label="▾ options")
    def toggle(*_):
        vis = cmds.formLayout(details, q=True, visible=True)
        cmds.formLayout(details, e=True, visible=not vis)
        cmds.button(toggle_btn, e=True, label=("▾ options" if not vis else "▸ options"))
    cmds.button(toggle_btn, e=True, c=toggle)

    cmds.optionMenu(cam_menu, e=True, cc=lambda *_: (_update_current_label(cam_menu, current_lbl),
                                                     _refresh_switch_button(cam_menu, switch_btn)))
    cmds.checkBox(orthos_cb, e=True,
        cc=lambda *_: (_populate_menu(cam_menu, cmds.checkBox(orthos_cb, q=True, v=True)),
                       _update_current_label(cam_menu, current_lbl),
                       _refresh_switch_button(cam_menu, switch_btn)))
    cmds.button(switch_btn, e=True, c=lambda *_:_do_switch(cam_menu, switch_btn, open_options))
    cmds.iconTextButton(create_btn, e=True,
        c=lambda *_:_create_shotcam(name_field, persp_copy, cam_menu, orthos_cb, current_lbl, switch_btn))

    _setup_camera_watchers(win, cam_menu, orthos_cb, current_lbl, switch_btn)
    cmds.showWindow(win)

# run
test_viewSWITCH_v16()
