import maya.cmds as cmds

def test_timeSHIFT_v26():
    # Clean old
    if cmds.window("testTimeSHIFTv26", exists=True):
        cmds.deleteUI("testTimeSHIFTv26")

    win = cmds.window("testTimeSHIFTv26", title="timeSHIFT v26", widthHeight=(306, 260), sizeable=False)
    form = cmds.formLayout()

    btn_height = 24

    # ================= Section Title =================
    section_title = cmds.text(label="▼ timeSHIFT ▼", align="center", height=20)
    cmds.formLayout(form, edit=True,
        attachForm=[(section_title, "top", 5), (section_title, "left", 0), (section_title, "right", 0)]
    )

    # ================= setTIME =================
    set_title = cmds.text(label="setTIME", align="left", height=18)
    cmds.formLayout(form, edit=True,
        attachForm=[(set_title, "top", 25), (set_title, "left", 7)]
    )

    std_buttons = ["1s", "2s", "3s", "4s", "5s", "6s", "8s"]
    x = 7
    for lbl in std_buttons:
        btn = cmds.button(label=lbl, width=40, height=btn_height)
        cmds.formLayout(form, edit=True,
            attachForm=[(btn, "top", 45)],
            attachPosition=[(btn, "left", x, 0)]
        )
        x += 42  # 40 width + 2 spacing

    # ================= Current Timing + Input + Apply Row =================
    current_label = cmds.text(label="Current Timing: 12", align="left", height=20, width=140)
    cmds.formLayout(form, edit=True,
        attachForm=[(current_label, "top", 80), (current_label, "left", 7)]
    )

    input_box = cmds.textField(text="", width=80, editable=True, bgc=(1,1,1))
    cmds.formLayout(form, edit=True,
        attachForm=[(input_box, "top", 80), (input_box, "right", 40)]
    )

    apply_btn = cmds.button(label="✔", width=28, height=28)
    cmds.formLayout(form, edit=True,
        attachForm=[(apply_btn, "top", 78), (apply_btn, "right", 7)]
    )

    # ================= nudgeTIME =================
    nudge_title = cmds.text(label="nudgeTIME", align="left", height=18)
    cmds.formLayout(form, edit=True,
        attachForm=[(nudge_title, "top", 115), (nudge_title, "left", 7)]
    )

    nudge_values = ["-8","-4","-2","-1","+1","+2","+4","+8"]

    # Buttons (35 px wide, 2 px spacing → total width = 294 px)
    x = 7
    for lbl in nudge_values:
        btn = cmds.button(label=lbl, width=35, height=btn_height)
        cmds.formLayout(form, edit=True,
            attachForm=[(btn, "top", 135)],
            attachPosition=[(btn, "left", x, 0)]
        )
        x += 37  # 35 width + 2 spacing

    cmds.showWindow(win)

# run it
test_timeSHIFT_v26()
