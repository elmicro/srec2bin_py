__version__ = '1.0'
__title__ = 'srec2bin'
__description__ = 'This utility converts binary data from Motorola S-Record file format [1] to raw binary.'
__author__ = 'Oliver Thamm'
__email__ = 'support@elmicro.com'
__uri__ = 'https://github.com/mrbell321/srec2bin_py'
__doc__ = __description__ + ' <' + __uri__ + '>'
__license__ = 'MIT'

from .srecord import SRecord, Purpose, Type
from .srec import to_image, to_pages, load