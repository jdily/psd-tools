"""
Mask module.
"""
from __future__ import absolute_import, unicode_literals
import logging

from psd_tools.constants import ChannelID

logger = logging.getLogger(__name__)


class Mask(object):
    """Mask data attached to a layer.

    There are two distinct internal mask data: user mask and vector mask.
    User mask refers any pixel-based mask whereas vector mask refers a mask
    from a shape path. Internally, two masks are combined and referred
    real mask.
    """

    def __init__(self, layer):
        self._layer = layer
        self._data = layer._record.mask_data

    @property
    def background_color(self):
        """Background color."""
        if self._has_real():
            return self._data.real_background_color
        return self._data.background_color

    @property
    def bbox(self):
        """BBox"""
        return self.left, self.top, self.right, self.bottom

    @property
    def left(self):
        """Left coordinate."""
        if self._has_real():
            return self._data.real_left
        return self._data.left

    @left.setter
    def left(self, value):
        if self._has_real():
            self._data.real_left = int(value)
            self._data.real_right = int(value) + self.width
        else:
            self._data.left = int(value)
            self._data.right = int(value) + self.width 

    @property
    def right(self):
        """Right coordinate."""
        if self._has_real():
            return self._data.real_right
        return self._data.right

    @property
    def top(self):
        """Top coordinate."""
        if self._has_real():
            return self._data.real_top
        return self._data.top

    @top.setter
    def top(self, value):
        if self._has_real():
            self._data.real_top = int(value)
            self._data.real_bottom = int(value) + self.height
        else:
            self._data.top = int(value)
            self._data.bottom = int(value) + self.height

    @property
    def bottom(self):
        """Bottom coordinate."""
        if self._has_real():
            return self._data.real_bottom
        return self._data.bottom

    @property
    def width(self):
        """Width."""
        return self.right - self.left

    @property
    def height(self):
        """Height."""
        return self.bottom - self.top

    @property
    def size(self):
        """(Width, Height) tuple."""
        return self.width, self.height

    @property
    def disabled(self):
        """Disabled."""
        return self._data.flags.mask_disabled

    @property
    def flags(self):
        """Flags."""
        return self._data.flags

    @property
    def parameters(self):
        """Parameters."""
        return self._data.parameters

    @property
    def real_flags(self):
        """Real flag."""
        return self._data.real_flags

    def _has_real(self):
        """Return True if the mask has real flags."""
        return (
            self.real_flags is not None and self.real_flags.parameters_applied
        )

    def topil(self, real=True, **kwargs):
        """
        Get PIL Image of the mask.

        :param real: When True, returns pixel + vector mask combined.
        :return: PIL Image object, or None if the mask is empty.
        """
        if real and self._has_real():
            channel = ChannelID.REAL_USER_LAYER_MASK
        else:
            channel = ChannelID.USER_LAYER_MASK
        return self._layer.topil(channel, **kwargs)

    def __repr__(self):
        return '%s(offset=(%d,%d) size=%dx%d)' % (
            self.__class__.__name__,
            self.left,
            self.top,
            self.width,
            self.height,
        )

    @property
    def offset(self):
        """
        (left, top) tuple. Writable.

        :return: `tuple`
        """
        return self.left, self.top

    @offset.setter
    def offset(self, value):
        self.left, self.top = tuple(int(x) for x in value)

    ## TODO: check the moving range usign parent_bbox
    def move(self, move_offset=(0,0), mode='tl', parent_bbox=None):
        if mode == "tl":
            exact_offset_x, exact_offset_y = 0, 0
            if self.left+move_offset[0] < parent_bbox[0]:
                exact_offset_x = self.left - parent_bbox[0]
            else:
                exact_offset_x = move_offset[0]
            if self.top+move_offset[1] < parent_bbox[1]:
                exact_offset_y = self.top - parent_bbox[1] 
            else:
                exact_offset_y = move_offset[1]
        
            self.offset = (self.left+exact_offset_x, self.top+exact_offset_y)
        else:
            pass