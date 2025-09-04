import math
from contextlib import contextmanager

import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as oma2
from maya import cmds

from . import util


def tdtCleanCurves(
    tangents=False,
    removeRedundantKeys=False,
    splineStartEnd=True,
    smoothness=0.0,
    weightFactor=0.333,
    smoothAllSplines=False,
    **kwargs,
):
    """Perform a number of operations to clean up the animation curves associated
    with the selected objects.

    Args:
        tangents|t (bool, optional):
            Indicates that tangents should be updated. Flatten peaks and valleys and spline without
            overshoot for all other keys. Defaults to `False`.

        removeRedundantKeys|rrk (bool, optional):
            Indicates that all keys that don't affect the shape of the curve should be removed.
            Defaults to `False`.

        splineStartEnd|sse (bool, optional):
            Indicates that the tangent type for the start and end keys should be spline.
            Defaults to `True`.

        smoothness|s (float, optional):
            The smoothing value applied to tangent angles. Defaults to `0.0`.

        weightFactor|wf (float, optional):
            The weighting factor applied to tangents that are not locked. Defaults to `0.333`.

        smoothAllSplines|sas (bool, optional):
            Indicates whether or not to apply the softness value to all spline tangents or just
            those on keys immediately before and after a peak/valley. Defaults to `False`.

    """
    CurveCleanerCommand(
        tangents=kwargs.get('t', tangents),
        removeRedundantKeys=kwargs.get('rrk', removeRedundantKeys),
        splineStartEnd=kwargs.get('sse', splineStartEnd),
        smoothness=kwargs.get('s', smoothness),
        weightFactor=kwargs.get('wf', weightFactor),
        smoothAllSplines=kwargs.get('sas', smoothAllSplines),
    ).run()


class CurveCleanerCommand:
    VALID_ANIMCURVES = ['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU']

    TANGENT_DICT = {
        oma2.MFnAnimCurve.kTangentFlat: 'flat',
        oma2.MFnAnimCurve.kTangentSmooth: 'spline',
    }

    def __init__(
        self,
        tangents=False,
        removeRedundantKeys=False,
        splineStartEnd=True,
        smoothness=0.0,
        weightFactor=0.333,
        smoothAllSplines=False,
    ):
        # Default to clean tangents if no cleaning flags provided
        if not tangents and not removeRedundantKeys:
            tangents = True

        self.clean_tangents = tangents
        self.remove_redundant_keys = removeRedundantKeys

        self.start_end_tangent_type = oma2.MFnAnimCurve.kTangentSmooth
        if splineStartEnd is False:
            self.start_end_tangent_type = oma2.MFnAnimCurve.kTangentFlat

        self.smoothing_value = smoothness
        self.weight_factor = weightFactor
        self.smooth_all_splines = smoothAllSplines

        self.num_keys_removed = 0
        self.num_curves_cleaned = 0

        self.selected = util.get_selected_objects()

    def run(self):
        if not self.selected:
            cmds.warning('No Objects Selected')
            return

        # Run commands
        with util.undo_chunk('tradigiTOOLS-tdtCleanCurves'):
            if self.remove_redundant_keys:
                self.remove_redundant_keys_from_selected()
                if self.num_keys_removed:
                    om2.MGlobal.displayInfo(f'Result: Removed {self.num_keys_removed} keys')

            if self.clean_tangents:
                self.clean_tangents_on_selected()
                if self.num_curves_cleaned:
                    om2.MGlobal.displayInfo(f'Result: Cleaned {self.num_curves_cleaned} curves')

    def remove_redundant_keys_from_selected(self):
        """Remove the keys from the provided selection list's animation curves that don't affect
        the curve shape.
        """
        anim_curves = get_anim_curve_list(self.selected)
        for anim_curve in anim_curves:
            keytimes = get_key_times(anim_curve)
            # First and last keys will never be redundant, minimum of 3 keys for a possible key removal
            if len(keytimes) <= 2:
                continue
            keyvalues = get_key_values(anim_curve)
            removekeys = []
            for i in range(1, len(keytimes) - 1):
                prev_val, curr_val, next_val = keyvalues[i - 1 : i + 2]
                # Add the current key to remove list if it is the same as the previous and next keys
                if curr_val == prev_val and curr_val == next_val:
                    removekeys.append(keytimes[i])
            # Remove all keys from list
            if removekeys:
                cmds.cutKey(anim_curve, clear=True, time=[(k,) for k in removekeys])
                self.num_keys_removed += len(removekeys)

    def clean_tangents_on_selected(self):
        """Switch the tangents on peaks and valleys to flat, while splining the remaining keys for
        the anim curves on all selected objects.
        """
        anim_curves = get_anim_curve_list(self.selected)
        for anim_curve in anim_curves:
            self.clean_tangents_on_anim_curve(anim_curve)
            self.num_curves_cleaned += 1

    def clean_tangents_on_anim_curve(self, anim_curve: str):
        """Switch the tangents on peaks and valleys to flat, while splining the remaining keys on
        an anim curve.
        """
        self.keytimes = get_key_times(anim_curve)
        keyvalues = get_key_values(anim_curve)
        num_keys = len(self.keytimes)

        # First and last keys will be handed according to the tangent type flag
        if num_keys > 0:
            # Set the first tangent to spline
            self.update_tangents(
                anim_curve=anim_curve,
                index=0,
                tangent_type=self.start_end_tangent_type,
                angle_in=om2.MAngle(0),
                angle_out=om2.MAngle(0),
                ignore_angle=True,
                apply_softness=False,
            )
            prev_inequal_value = keyvalues[0]
        if num_keys > 1:
            # Set the last tangent to spline
            self.update_tangents(
                anim_curve=anim_curve,
                index=num_keys - 1,
                tangent_type=self.start_end_tangent_type,
                angle_in=om2.MAngle(0),
                angle_out=om2.MAngle(0),
                ignore_angle=True,
                apply_softness=False,
            )

        # Make a list that determines whether key is a peak or valley
        peak_or_valley = [False] * num_keys
        for i in range(1, num_keys - 1):
            prev_val, curr_val, next_val = keyvalues[i - 1 : i + 2]

            # Keep track of last inequal values to determine if the key is on a peak or a value
            if curr_val != prev_val:
                prev_inequal_value = prev_val

            if curr_val != next_val:
                next_inequal_val = next_val
            else:
                # Find the next inequal value
                for j in range(i + 2, num_keys):
                    next_inequal_val = keyvalues[j]

                    # exit the loop when a new inequal value is found
                    if next_inequal_val != curr_val:
                        break

            if (curr_val <= prev_inequal_value and curr_val <= next_inequal_val) or (
                curr_val >= prev_inequal_value and curr_val >= next_inequal_val
            ):
                peak_or_valley[i] = True

        # Start on the second key and finish on the second last key
        for i in range(1, num_keys - 1):
            prev_val, curr_val, next_val = keyvalues[i - 1 : i + 2]
            prev_time, curr_time, next_time = self.keytimes[i - 1 : i + 2]

            angle_in = get_angle(
                value1=prev_val, value2=curr_val, time1=prev_time, time2=curr_time
            )
            angle_out = get_angle(
                value1=curr_val, value2=next_val, time1=curr_time, time2=next_time
            )

            # If the current key is a valley or a peak, the tangent type will be set to flat
            if peak_or_valley[i]:
                self.update_tangents(
                    anim_curve=anim_curve,
                    index=i,
                    tangent_type=oma2.MFnAnimCurve.kTangentFlat,
                    angle_in=angle_in,
                    angle_out=angle_out,
                    ignore_angle=True,
                    apply_softness=False,
                )
            else:
                # Determine if the smoothing should be applied to the spline.
                # If not in a smooth all splines mode, only splines next to a peak or valley will be
                # smoothed
                apply_softness = (
                    self.smooth_all_splines or peak_or_valley[i - 1] or peak_or_valley[i + 1]
                )
                self.update_tangents(
                    anim_curve=anim_curve,
                    index=i,
                    tangent_type=oma2.MFnAnimCurve.kTangentSmooth,
                    angle_in=angle_in,
                    angle_out=angle_out,
                    ignore_angle=False,
                    apply_softness=apply_softness,
                )

    def update_tangents(
        self,
        anim_curve: str,
        index: int,
        tangent_type: int,
        angle_in: om2.MAngle,
        angle_out: om2.MAngle,
        ignore_angle: bool,
        apply_softness: bool,
    ):
        """Modify the current tangent type and, if necessary, the tangent weight to avoid overshoots"""
        # Update the tangent type for the key
        cmds.keyTangent(
            anim_curve,
            edit=True,
            time=(self.keytimes[index],),
            inTangentType=CurveCleanerCommand.TANGENT_DICT[tangent_type],
            outTangentType=CurveCleanerCommand.TANGENT_DICT[tangent_type],
        )

        angle_out_rad = angle_out.asRadians()
        angle_in_rad = angle_in.asRadians()

        # The smallest angle is used to avoid overshoots
        if abs(angle_out_rad) > abs(angle_in_rad):
            tangent_angle = angle_in
        else:
            tangent_angle = angle_out

        # Adjust angle for smoothing if necessary
        if not ignore_angle and apply_softness:
            # Add in the smoothing value (softness)
            radian_diff = abs(angle_out_rad - angle_in_rad)
            softness = radian_diff * self.smoothing_value

            # Add or subtract the softness depending on positive or negative slope
            if angle_in_rad > 0 or (angle_in_rad == 0 and angle_out_rad > 0):
                # Positive slope
                tangent_angle = om2.MAngle(tangent_angle.asRadians() + softness)
            else:
                # Negative Slope
                tangent_angle = om2.MAngle(tangent_angle.asRadians() - softness)

            # Unlock tangent and weights
            with temp_unlock_curve(anim_curve):
                cmds.keyTangent(
                    anim_curve,
                    edit=True,
                    time=(self.keytimes[index],),
                    inAngle=tangent_angle.asDegrees(),
                    outAngle=tangent_angle.asDegrees(),
                )

                # Update the in-tangent weight
                if index != 0:
                    this_index = index
                    other_index = index - 1
                else:
                    this_index = index + 1
                    other_index = index
                delta_time = self.keytimes[this_index] - self.keytimes[other_index]
                new_weight = delta_time / math.cos(tangent_angle.asRadians()) * self.weight_factor
                cmds.keyTangent(
                    anim_curve,
                    edit=True,
                    time=(self.keytimes[index],),
                    inWeight=new_weight,
                    outWeight=new_weight,
                )


# -------------------------------------------------------------------------------------------------


def get_anim_curve_list(nodes: list[str]) -> list[str]:
    """Get a list of anim curves given a nodes list"""
    curves = [n for n in cmds.listHistory(nodes) if cmds.objectType(n, isAType='animCurve')] or []
    # Filter to valid anim curves and convert to set to avoid returning duplicates
    curves = {c for c in curves if cmds.objectType(c) in CurveCleanerCommand.VALID_ANIMCURVES}
    return list(curves)


def get_key_times(anim_curve: str) -> list[float]:
    """Get a list of key times for a given anim curve"""
    return cmds.keyframe(anim_curve, query=True) or []


def get_key_values(anim_curve: str) -> list[float]:
    """Get a list of key values for a given anim curve"""
    return cmds.keyframe(anim_curve, query=True, valueChange=True) or []


def get_angle(value1: float, value2: float, time1: float, time2: float) -> om2.MAngle:
    """Return the angle for two points on a curve"""
    value_delta = value2 - value1
    time_delta = time2 - time1
    radians = math.atan(value_delta / time_delta)
    return om2.MAngle(radians)


@contextmanager
def temp_unlock_curve(anim_curve: str):
    """Context for temporarily unlocking the tangents for the given anim curve"""
    weighted = cmds.keyTangent(anim_curve, query=True, weightedTangents=True)[0]
    t_locks = cmds.keyTangent(anim_curve, query=True, lock=True)
    w_locks = cmds.keyTangent(anim_curve, query=True, weightLock=True)
    keytimes = get_key_times(anim_curve)
    try:
        cmds.keyTangent(anim_curve, edit=True, lock=False, weightLock=False, weightedTangents=True)
        yield
    finally:
        for t_lock, w_lock, keytime in zip(t_locks, w_locks, keytimes):
            cmds.keyTangent(anim_curve, edit=True, lock=t_lock, weightLock=w_lock, time=(keytime,))
        cmds.keyTangent(anim_curve, edit=True, weightedTangents=weighted)
