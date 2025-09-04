from contextlib import contextmanager

from maya import cmds


def get_selected_objects() -> list[str]:
    """Get a list of all the selected objects

    Selected Objects Include:
       1) The Active Character Set (if in use) and its subset
       2) Character Sets selected by the user (and their subsets)
       3) Objects selected by the user

    """
    selected = []

    # Get the character set if active (in Maya) and the associated character set subsets
    selected.extend(get_active_character_sets())

    # Get the character sets selected (by user) and the associated character set subsets
    selected.extend(get_selected_character_sets())

    # Get the currently selected objects
    selected.extend(cmds.ls(selection=True, objectsOnly=True))

    return list(set(selected))


def get_active_character_sets() -> list[str]:
    """Create a list of the currently active character set and its subsets"""
    nodes = cmds.selectionConnection('highlightList', query=True, object=True) or []
    return epxand_character_subsets(nodes)


def get_selected_character_sets() -> list[str]:
    """Create a list of selected character sets and their subsets"""
    return epxand_character_subsets(cmds.ls(selection=True))


def get_sub_character_sets(character_set: str) -> list[str]:
    """Recursively create a list of sub character sets"""
    nodes = set(cmds.character(character_set, query=True, nodesOnly=True))
    return epxand_character_subsets(nodes)


def epxand_character_subsets(nodes):
    results = []
    char_sets = [n for n in nodes if cmds.objectType(n, isType='character')]
    for char_set in char_sets:
        results.append(char_set)
        results.extend(get_sub_character_sets(char_set))
    return results


@contextmanager
def undo_chunk(chunkname):
    """Context for grouping commands under one undo"""
    try:
        cmds.undoInfo(chunkName=chunkname, openChunk=True)
        yield
    finally:
        cmds.undoInfo(chunkName=chunkname, closeChunk=True)
