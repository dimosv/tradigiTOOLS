from maya import cmds


def tdtInsertBreakdown(
    weight=0.5,
    selectedAttr=False,
    mode='overwrite',
    invalidAttrOpFlag='skipAll',
    ignoreRippleCheck=False,
    tickDrawSpecial=False,
    **kwargs,
):
    """Insert breakdowns, for keyframable attributes, on selected objects.

    Args:
        weight|w (float, optional):
            Specifies the weighting of the breakdown between the key prior to and after the current
            time. Defaults to `0.5`.

        selectedAttr|sa (bool, optional):
            Only attributes that are highlighted in the channelBox will have breakdowns set.
            Defaults to `False`.

        mode|m (str, optional):
            Indicates whether the breakdown will be set in ripple ("ripple") or overwrite
            ("overwrite") mode. Defaults to `'overwrite'`.

        invalidAttrOpFlag|iao (str, optional):
            Dictates how the command will proceed if an attribute cannot have a key set on it.
                - "skipAll" - The command will fail. No breakdowns will be set.
                - "skipObject" - No breakdowns will be set on the object with the invalid attribute
                - "skipAttr" - No breakdowns will be set on the invalid attributes. All others will
                    have a breakdown set.

            Defaults to `'skipAll'`.

        ignoreRippleCheck|irc (bool, optional):
            This check verifies that, when in ripple mode, if a single key exists at the current
            time, all attributes must have a key at the current time. This is to prevent a partial
            ripple where keys that don't exist are created at the current time and keys that do
            exist are rippled forward. Defaults to `False`.

        tickDrawSpecial|tds (bool, optional):
            Sets the special drawing state for the breakdowns when it is drawn in as a tick in the
            timeline. Defaults to `False`.

    """
    BreakdownCommand(
        weight=kwargs.get('w', weight),
        selectedAttr=kwargs.get('sa', selectedAttr),
        mode=kwargs.get('m', mode),
        invalidAttrOpFlag=kwargs.get('iao', invalidAttrOpFlag),
        ignoreRippleCheck=kwargs.get('irc', ignoreRippleCheck),
        tickDrawSpecial=kwargs.get('tds', tickDrawSpecial),
    ).run()


class BreakdownCommand:
    def __init__(
        self,
        weight=0.5,
        selectedAttr=False,
        mode='overwrite',
        invalidAttrOpFlag='skipAll',
        ignoreRippleCheck=False,
        tickDrawSpecial=False,
    ):
        self.current_animation_frame = cmds.currentTime(query=True)

        self.breakdown_weight = weight
        self.breakdown_mode = mode
        self.selected_attr_only = selectedAttr
        self.invalid_attr_op = invalidAttrOpFlag
        self.ignore_ripple_check = ignoreRippleCheck
        self.tick_draw_special = tickDrawSpecial

        self.attributes_skipped = False
        self.objects_skipped = False

        # TODO ?

    def run(self):
        # TODO
        raise NotImplementedError
