import maya.cmds as cmds

def test_keyCONTROL_v13():
    # Clean old
    if cmds.window("testKeyCONTROLv13", exists=True):
        cmds.deleteUI("testKeyCONTROLv13")

    win = cmds.window("testKeyCONTROLv13", title="keyCONTROL v13", widthHeight=(306, 540), sizeable=False)
    form = cmds.formLayout()

    # --- constants ---
    btn_specs = [
        (7, 36, "<<"), (44, 30, "1/7"), (75, 28, "1/5"), (104, 26, "1/3"),
        (131, 44, "<>"),
        (176, 26, "1/3"), (203, 28, "1/5"), (232, 30, "1/7"), (263, 36, ">>")
    ]
    btn_height = 24
    slider_width = 256
    bias_width = 46

    # ================= KEYs =================
    key_label = cmds.text(label="▼ KEYs ▼", align="center", height=20)
    cmds.formLayout(form, edit=True,
        attachForm=[(key_label, "top", 5), (key_label, "left", 0), (key_label, "right", 0)]
    )

    # Buttons
    for x, w, lbl in btn_specs:
        btn = cmds.button(label=lbl, width=w, height=btn_height, backgroundColor=(1.0, 0.2, 0.2))
        cmds.formLayout(form, edit=True,
            attachForm=[(btn, "top", 30)],
            attachPosition=[(btn, "left", x, 0)]
        )

    # Slider
    key_slider = cmds.floatSlider(width=slider_width, min=0, max=100, value=50)
    cmds.formLayout(form, edit=True,
        attachForm=[(key_slider, "top", 66)],
        attachPosition=[(key_slider, "left", 25, 0)]
    )

    # Bias
    key_bias = cmds.textField(width=bias_width, text="50", bgc=(1.0, 0.7, 0.7))
    cmds.formLayout(form, edit=True,
        attachForm=[(key_bias, "top", 91)],
        attachPosition=[(key_bias, "left", 130, 0)]
    )

    # ================= BRKs =================
    brk_bias = cmds.textField(width=bias_width, text="50", bgc=(0.7, 1.0, 0.7))
    cmds.formLayout(form, edit=True,
        attachForm=[(brk_bias, "top", 131)],
        attachPosition=[(brk_bias, "left", 130, 0)]
    )

    brk_slider = cmds.floatSlider(width=slider_width, min=0, max=100, value=50)
    cmds.formLayout(form, edit=True,
        attachForm=[(brk_slider, "top", 156)],
        attachPosition=[(brk_slider, "left", 25, 0)]
    )

    for x, w, lbl in btn_specs:
        btn = cmds.button(label=lbl, width=w, height=btn_height, backgroundColor=(0.2, 1.0, 0.2))
        cmds.formLayout(form, edit=True,
            attachForm=[(btn, "top", 181)],
            attachPosition=[(btn, "left", x, 0)]
        )

    brk_label = cmds.text(label="▲ BRKs ▲", align="center", height=20)
    cmds.formLayout(form, edit=True,
        attachForm=[(brk_label, "top", 211), (brk_label, "left", 0), (brk_label, "right", 0)]
    )

    # ================= Separator =================
    sep1 = cmds.separator(style="in", height=12)
    cmds.formLayout(form, edit=True,
        attachForm=[(sep1, "top", 240), (sep1, "left", 0), (sep1, "right", 0)]
    )

    # ================= KEY/BRK Maker =================
    maker_title = cmds.text(label="KEY/BRK Maker", align="left", height=20)
    cmds.formLayout(form, edit=True,
        attachForm=[(maker_title, "top", 255), (maker_title, "left", 7)]
    )

    # KEY (60) @ x=7
    key_btn = cmds.button(label="KEY", width=60, height=24, backgroundColor=(1.0, 0.2, 0.2))
    cmds.formLayout(form, edit=True,
        attachForm=[(key_btn, "top", 280)],
        attachPosition=[(key_btn, "left", 7, 0)]
    )

    # R (40) @ x=68
    r_btn = cmds.button(label="R", width=40, height=24, backgroundColor=(1.0, 0.2, 0.2))
    cmds.formLayout(form, edit=True,
        attachForm=[(r_btn, "top", 280)],
        attachPosition=[(r_btn, "left", 68, 0)]
    )

    # smartKEY (88) spanning R→G gap @ x=109
    smart_btn = cmds.button(label="smartKEY", width=88, height=24, backgroundColor=(0.6, 0.6, 1.0))
    cmds.formLayout(form, edit=True,
        attachForm=[(smart_btn, "top", 280)],
        attachPosition=[(smart_btn, "left", 109, 0)]
    )

    # G (40) @ x=198
    g_btn = cmds.button(label="G", width=40, height=24, backgroundColor=(0.2, 1.0, 0.2))
    cmds.formLayout(form, edit=True,
        attachForm=[(g_btn, "top", 280)],
        attachPosition=[(g_btn, "left", 198, 0)]
    )

    # BRK (60) @ x=239
    brk_btn = cmds.button(label="BRK", width=60, height=24, backgroundColor=(0.2, 1.0, 0.2))
    cmds.formLayout(form, edit=True,
        attachForm=[(brk_btn, "top", 280)],
        attachPosition=[(brk_btn, "left", 239, 0)]
    )

    # ================= Separator =================
    sep2 = cmds.separator(style="in", height=12)
    cmds.formLayout(form, edit=True,
        attachForm=[(sep2, "top", 310), (sep2, "left", 0), (sep2, "right", 0)]
    )

    # ================= Mode Section =================
    mode_title = cmds.text(label="Mode", align="left", height=20)
    cmds.formLayout(form, edit=True,
        attachForm=[(mode_title, "top", 330), (mode_title, "left", 20)]
    )

    ripple_cb = cmds.checkBox(label="Ripple")
    cmds.formLayout(form, edit=True,
        attachForm=[(ripple_cb, "top", 355), (ripple_cb, "left", 20)]
    )

    sel_attr_cb = cmds.checkBox(label="Selected Attributes")
    cmds.formLayout(form, edit=True,
        attachForm=[(sel_attr_cb, "top", 371), (sel_attr_cb, "left", 20)]
    )

    skip_cb = cmds.checkBox(label="Skip Unkeyed")
    cmds.formLayout(form, edit=True,
        attachForm=[(skip_cb, "top", 387), (skip_cb, "left", 20)]
    )

    cmds.showWindow(win)

# run it
test_keyCONTROL_v13()
