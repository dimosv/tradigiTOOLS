from maya import cmds


def tdtRetiming(
    relative=False,
    delta=1,
    nextKeyOnComplete=False,
    query=False,
    **kwargs,
):
    """Adjust the current timing between selected keys

    Args:
        relative|rel (bool, optional):
            Indicates whether retiming delta should be treated as an absolute or relative value.
            Defaults to `False`.

        delta|d (int, optional):
            The change to the current timing between keys Abs/Rel determined by the relative flag.
            Defaults to `1`.

        nextKeyOnComplete|nkc (bool, optional):
            Determines where the playhead will be placed after retiming. If this is true, it is
            moved to the last key in the current retiming strip, if false, it will move to the
            first key. Defaults to `False`.

        query|q (bool, optional):
            Indicates if the command is in query mode. Defaults to `False`.

    """
    RetimingCommand(
        relative=kwargs.get('rel', relative),
        delta=kwargs.get('d', delta),
        nextKeyOnComplete=kwargs.get('nkc', nextKeyOnComplete),
        query=kwargs.get('q', query),
    ).run()


class RetimingCommand:
    def __init__(self, relative=False, delta=1, nextKeyOnComplete=False, query=False):
        self.relative_mode = relative
        self.timing_delta = delta
        self.next_key_on_complete = nextKeyOnComplete
        self.query_mode = query

        self.num_retimed = 0
        self.orig_playhead_time = cmds.currentTime(query=True)
        self.new_playhead_time = self.orig_playhead_time
        self.strip_string = 'No Keys Set'

        # TODO ?

    def run(self):
        # TODO
        raise NotImplementedError
