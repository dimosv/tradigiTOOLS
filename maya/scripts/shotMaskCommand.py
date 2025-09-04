from maya import cmds


def tdtShotMask(
    camera='',
    aspectRatio=0.0,
    cleanScene=False,
    maskThickness=0.05,
    title='Title',
    text1='',
    text2='',
    keyType=False,
    frameDigits=False,
    query=False,
    **kwargs,
):
    """Create an overlay in 3D space that is used to display a timecode and current shot details

    Args:
        camera|c (str, optional):
            The camera transform node name. Defaults to `''`.

        aspectRatio|ar (float, optional):
            Aspect ratio for the overlay. Defaults to `0.0`.

        cleanScene|cs (bool, optional):
            Clears out all nodes related to the Shot Mask on the scene, nothing is created.
            Defaults to `False`.

        maskThickness|mt (float, optional):
            The thickness of the border as a fraction of the total width/height. Defaults to `0.05`.

        title|t (str, optional):
            TODO _description_. Defaults to `'Title'`.

        text1|t1 (str, optional):
            TODO _description_. Defaults to `''`.

        text2|t2 (str, optional):
            TODO _description_. Defaults to `''`.

        keyType|kt (bool, optional):
            Query only: Indicates the command should return the key type at the current frame.
            Key types can be "none", "key" or "breakdown". Defaults to `False`.

        frameDigits|fd (bool, optional):
            Query only: Converts the current frame into an int array where index 0 represents the
            1 second column, index 2 represents the 10 second column, etc.... Defaults to `False`.

        query|q (bool, optional):
            Indicates if the command is in query mode. Defaults to `False`.

    """
    ShotMaskCommand(
        camera=kwargs.get('c', camera),
        aspectRatio=kwargs.get('ar', aspectRatio),
        cleanScene=kwargs.get('cs', cleanScene),
        maskThickness=kwargs.get('mt', maskThickness),
        title=kwargs.get('t', title),
        text1=kwargs.get('t1', text1),
        text2=kwargs.get('t2', text2),
        keyType=kwargs.get('kt', keyType),
        frameDigits=kwargs.get('fd', frameDigits),
        query=kwargs.get('q', query),
    ).run()


class ShotMaskCommand:
    def __init__(
        self,
        camera='',
        aspectRatio=0.0,
        cleanScene=False,
        maskThickness=0.05,
        title='Title',
        text1='',
        text2='',
        keyType=False,
        frameDigits=False,
        query=False,
    ):
        self.query_mode = query
        self.query_key_type = keyType and self.query_mode
        self.query_digits = frameDigits and self.query_mode

        self.clean_scene = cleanScene

        self.camera = camera
        self.aspect_ratio = aspectRatio
        self.render_aspect_ratio = 0.0
        self.film_aspect_ratio = 0.0

        self.mask_thickness = maskThickness
        self.min_thickness = 0.02
        self.max_thickness = 0.2

        self.title = title
        self.text1 = text1
        self.text2 = text2

        # TODO ?

    def run(self):
        if not self.camera:
            cmds.warning('No camera selected')
            return

        # TODO
        raise NotImplementedError
