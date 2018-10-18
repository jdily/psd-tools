from __future__ import absolute_import, unicode_literals
import attr
import logging
import io
from psd_tools2.utils import (
    read_fmt, write_fmt, read_pascal_string, write_pascal_string,
    read_length_block, write_length_block
)
from psd_tools2.validators import in_
from psd_tools2.decoder.base import BaseElement, ListElement
from psd_tools2.constants import ImageResourceID

logger = logging.getLogger(__name__)


@attr.s(repr=False)
class ImageResources(ListElement):
    """
    Image resources section of the PSD file.

    .. py:attribute:: items
    """
    items = attr.ib(factory=list)

    @classmethod
    def read(cls, fp, encoding='utf-8'):
        """Read the element from a file-like object.

        :param fp: file-like object
        :rtype: ImageResources
        """
        logger.debug('reading resources, pos=%d' % fp.tell())
        items = []
        data = read_length_block(fp)
        with io.BytesIO(data) as f:
            while f.tell() < len(data):
                item = ImageResource.read(f, encoding)
                items.append(item)
        return cls(items)

    def write(self, fp, encoding='utf-8'):
        """Write the element to a file-like object.

        :param fp: file-like object
        """
        return write_length_block(fp, lambda f: self._write_body(f, encoding))

    def _write_body(self, fp, encoding):
        return sum(block.write(fp, encoding) for block in self)


@attr.s
class ImageResource(BaseElement):
    """
    Image resource block.

    .. py:attribute:: signature
    .. py:attribute:: id
    .. py:attribute:: name
    .. py:attribute:: data
    """
    signature = attr.ib(default=b'8BIM', type=bytes, repr=False,
                        validator=in_((b'8BIM', b'MeSa')))
    id = attr.ib(default=1000, type=int)
    name = attr.ib(default='', type=str)
    data = attr.ib(default=b'', type=bytes, repr=False)

    @classmethod
    def read(cls, fp, encoding='utf-8'):
        """Read the element from a file-like object.

        :param fp: file-like object
        :rtype: ImageResource
        """
        signature, id = read_fmt('4sH', fp)
        name = read_pascal_string(fp, encoding, 2)
        data = read_length_block(fp, padding=2)
        # TODO: parse image resource
        return cls(signature, id, name, data)

    def write(self, fp, encoding='utf-8'):
        """Write the element to a file-like object.
        """
        written = write_fmt(fp, '4sH', self.signature, self.id)
        written += write_pascal_string(fp, self.name, encoding, 2)
        written += write_length_block(fp, lambda f: f.write(self.data),
                                      padding=2)
        return written
