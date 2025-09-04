from maya import cmds


def tdtSetKeyframe(edit=False, ignoreUnkeyed=False, tickDrawSpecial=False, **kwargs):
    """Set new keys or edit the value of keys

    Args:
        edit|e (bool, optional):
            Update existing keys. Defaults to `False`.

        ignoreUnkeyed|iuk (bool, optional):
            Don't create a key on attributes that don't have any keys set. Defaults to `False`.

        tickDrawSpecial|tds (bool, optional):
            Use the special drawing state for the keys. Defaults to `False`.

    """
    SetKeyCommand(
        edit=kwargs.get('e', edit),
        ignoreUnkeyed=kwargs.get('iuk', ignoreUnkeyed),
        tickDrawSpecial=kwargs.get('tds', tickDrawSpecial),
    ).run()


class SetKeyCommand:
    def __init__(self, edit=False, ignoreUnkeyed=False, tickDrawSpecial=False):
        self.edit_mode = edit
        self.ignore_unkeyed = ignoreUnkeyed
        self.tick_draw_special = tickDrawSpecial

        self.orig_playhead_time = cmds.currentTime(query=True)
        self.num_tick_draw_special = 0

        # TODO ?

    def run(self):
        # TODO
        raise NotImplementedError
