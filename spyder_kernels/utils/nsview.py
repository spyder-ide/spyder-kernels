# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2009- Spyder Kernels Contributors
#
# Licensed under the terms of the MIT License
# (see spyder_kernels/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Utilities
"""

from __future__ import print_function

from itertools import islice
import re

# Local imports
from spyder_kernels.py3compat import (NUMERIC_TYPES, INT_TYPES, TEXT_TYPES,
                                      to_text_string, is_text_string,
                                      is_type_text_string,
                                      is_binary_string, PY2,
                                      to_binary_string, iteritems)


#==============================================================================
# FakeObject
#==============================================================================
class FakeObject(object):
    """Fake class used in replacement of missing modules"""
    pass


#==============================================================================
# Numpy arrays and numeric types support
#==============================================================================
try:
    from numpy import (ndarray, array, matrix, recarray,
                       int64, int32, int16, int8, uint64, uint32, uint16, uint8,
                       float64, float32, float16, complex64, complex128, bool_)
    from numpy.ma import MaskedArray
    from numpy import savetxt as np_savetxt
    from numpy import get_printoptions, set_printoptions
except:
    ndarray = array = matrix = recarray = MaskedArray = np_savetxt = \
     int64 = int32 = int16 = int8 = uint64 = uint32 = uint16 = uint8 = \
     float64 = float32 = float16 = complex64 = complex128 = bool_ = FakeObject


def get_numpy_dtype(obj):
    """Return NumPy data type associated to obj
    Return None if NumPy is not available
    or if obj is not a NumPy array or scalar"""
    if ndarray is not FakeObject:
        # NumPy is available
        import numpy as np
        if isinstance(obj, np.generic) or isinstance(obj, np.ndarray):
        # Numpy scalars all inherit from np.generic.
        # Numpy arrays all inherit from np.ndarray.
        # If we check that we are certain we have one of these
        # types then we are less likely to generate an exception below.
            try:
                return obj.dtype.type
            except (AttributeError, RuntimeError):
                #  AttributeError: some NumPy objects have no dtype attribute
                #  RuntimeError: happens with NetCDF objects (Issue 998)
                return


#==============================================================================
# Pandas support
#==============================================================================
try:
    from pandas import DataFrame, Index, Series
except:
    DataFrame = Index = Series = FakeObject


#==============================================================================
# PIL Images support
#==============================================================================
try:
    from spyder import pil_patch
    Image = pil_patch.Image.Image
except:
    Image = FakeObject  # analysis:ignore


#==============================================================================
# BeautifulSoup support (see Issue 2448)
#==============================================================================
try:
    import bs4
    NavigableString = bs4.element.NavigableString
except:
    NavigableString = FakeObject  # analysis:ignore


# =============================================================================
# SymPy support
# =============================================================================
try:
    from sympy import Basic, Set, Tuple
    from sympy.matrices import MatrixBase
    from sympy.tensor.array import NDimArray
except:
    Basic = MatrixBase = NDimArray = Set = Tuple = FakeObject


#==============================================================================
# Misc.
#==============================================================================
def address(obj):
    """Return object address as a string: '<classname @ address>'"""
    return "<%s @ %s>" % (obj.__class__.__name__,
                          hex(id(obj)).upper().replace('X', 'x'))


def try_to_eval(value):
    """Try to eval value"""
    try:
        return eval(value)
    except (NameError, SyntaxError, ImportError):
        return value

    
def get_size(item):
    """Return size of an item of arbitrary type"""
    if isinstance(item, (list, set, tuple, dict)):
        return len(item)
    elif isinstance(item, (ndarray, MaskedArray, MatrixBase, DataFrame, Index,
                           Series, NDimArray)):
        return item.shape
    elif isinstance(item, Image):
        return item.size
    elif isinstance(item, (Set, Tuple)):
        return len(item.args)
    else:
        return 1


def get_object_attrs(obj):
    """
    Get the attributes of an object using dir.

    This filters protected attributes
    """
    attrs = [k for k in dir(obj) if not k.startswith('__')]
    if not attrs:
        attrs = dir(obj)
    return attrs


# =============================================================================
# String truncation
# =============================================================================
def truncate_string(s, linelength, ellipses=None, eol=None):
    if len(s) > linelength:
        if not ellipses:
            if is_binary_string(s):
                ellipses = b' ...'
            else:
                ellipses = u' ...'

        if not eol:
            if is_binary_string(s):
                eol = b'\n'
            else:
                eol = u'\n'

        s = s[:linelength] + ellipses
    return s


def truncate_rows(s, nlines=None, linelength=None):
    if is_binary_string(s):
        ellipses = b' ...'
        eol = b'\n'
    else:
        ellipses = u' ...'
        eol = u'\n'
    strings = s.split(eol)
    if nlines is not None and len(strings) > nlines:
        del strings[nlines:]
        strings.append(ellipses)

    if linelength is not None:
        new_strings = []
        for line in strings:
            new_strings.append(truncate_string(line, linelength,
                                               ellipses=ellipses,
                                               eol=eol))
        strings = new_strings

    return eol.join(strings)


#==============================================================================
# Date and datetime objects support
#==============================================================================
import datetime


try:
    from dateutil.parser import parse as dateparse
except:
    def dateparse(datestr):  # analysis:ignore
        """Just for 'year, month, day' strings"""
        return datetime.datetime( *list(map(int, datestr.split(','))) )


def datestr_to_datetime(value):
    rp = value.rfind('(')+1
    v = dateparse(value[rp:-1])
    print(value, "-->", v)  # spyder: test-skip
    return v


def str_to_timedelta(value):
    """Convert a string to a datetime.timedelta value.

    The following strings are accepted:

        - 'datetime.timedelta(1, 5, 12345)'
        - 'timedelta(1, 5, 12345)'
        - '(1, 5, 12345)'
        - '1, 5, 12345'
        - '1'

    if there are less then three parameters, the missing parameters are
    assumed to be 0. Variations in the spacing of the parameters are allowed.

    Raises:
        ValueError for strings not matching the above criterion.

    """
    m = re.match(r'^(?:(?:datetime\.)?timedelta)?'
                 r'\(?'
                 r'([^)]*)'
                 r'\)?$', value)
    if not m:
        raise ValueError('Invalid string for datetime.timedelta')
    args = [int(a.strip()) for a in m.group(1).split(',')]
    return datetime.timedelta(*args)


#==============================================================================
# Background colors for supported types
#==============================================================================
ARRAY_COLOR = "#00ff00"
SCALAR_COLOR = "#0000ff"
SYMPY_COLOR ="#008080"
COLORS = {
          bool:               "#ff00ff",
          NUMERIC_TYPES:      SCALAR_COLOR,
          list:               "#ffff00",
          set:                "#008000",
          dict:               "#00ffff",
          tuple:              "#c0c0c0",
          TEXT_TYPES:         "#800000",
          (ndarray,
           MaskedArray,
           matrix,
           DataFrame,
           Series,
           Index):            ARRAY_COLOR,
          (Basic,
           MatrixBase,
           NDimArray):        SYMPY_COLOR,
          Image:              "#008000",
          datetime.date:      "#808000",
          datetime.timedelta: "#808000",
          }
CUSTOM_TYPE_COLOR = "#7755aa"
UNSUPPORTED_COLOR = "#ffffff"


def get_color_name(value):
    """Return color name depending on value type"""
    if not is_known_type(value):
        return CUSTOM_TYPE_COLOR
    for typ, name in list(COLORS.items()):
        if isinstance(value, typ):
            return name
    else:
        np_dtype = get_numpy_dtype(value)
        if np_dtype is None or not hasattr(value, 'size'):
            return UNSUPPORTED_COLOR
        elif value.size == 1:
            return SCALAR_COLOR
        else:
            return ARRAY_COLOR


def is_editable_type(value):
    """Return True if data type is editable with a standard GUI-based editor,
    like CollectionsEditor, ArrayEditor, QDateEdit or a simple QLineEdit"""
    return get_color_name(value) not in (UNSUPPORTED_COLOR, CUSTOM_TYPE_COLOR)


#==============================================================================
# Sorting
#==============================================================================
def sort_against(list1, list2, reverse=False):
    """
    Arrange items of list1 in the same order as sorted(list2).

    In other words, apply to list1 the permutation which takes list2 
    to sorted(list2, reverse).
    """
    try:
        return [item for _, item in
                sorted(zip(list2, list1), key=lambda x: x[0], reverse=reverse)]
    except:
        return list1


def unsorted_unique(lista):
    """Removes duplicates from lista neglecting its initial ordering"""
    return list(set(lista))


#==============================================================================
# Display <--> Value
#==============================================================================

MAX_LINE_LENGTH = 80
MAX_NUMBER_OF_LINES = 10


def default_display(value, with_module=True):
    """Default display for unknown objects."""
    object_type = type(value)
    try:
        name = object_type.__name__
        module = object_type.__module__
        if with_module:
            return name + ' object of ' + module + ' module'
        else:
            return name
    except:
        type_str = to_text_string(object_type)
        return type_str[1:-1]


def collections_display(value, level):
    """Display for collections (i.e. list, set, tuple and dict)."""
    is_dict = isinstance(value, dict)
    is_set = isinstance(value, set)

    # Get elements
    if is_dict:
        elements = iteritems(value)
    else:
        elements = value

    # Truncate values
    truncate = False
    if level == 1 and len(value) > 10:
        elements = islice(elements, 10) if is_dict or is_set else value[:10]
        truncate = True
    elif level == 2 and len(value) > 5:
        elements = islice(elements, 5) if is_dict or is_set else value[:5]
        truncate = True

    # Get display of each element
    if level <= 2:
        if is_dict:
            displays = [value_to_display(k, level=level) + ':' +
                        value_to_display(v, level=level)
                        for (k, v) in list(elements)]
        else:
            displays = [value_to_display(e, level=level)
                        for e in elements]
        if truncate:
            displays.append('...')
        display = ', '.join(displays)
    else:
        display = '...'

    # Return display
    if is_dict:
        display = '{' + display + '}'
    elif isinstance(value, list):
        display = '[' + display + ']'
    elif isinstance(value, set):
        display = '{' + display + '}'
    else:
        display = '(' + display + ')'

    return display


def value_to_display(value, minmax=False, level=0):
    """Convert value for display purpose"""
    # To save current Numpy printoptions
    np_printoptions = FakeObject

    truncated = False
    try:
        numeric_numpy_types = (int64, int32, int16, int8,
                               uint64, uint32, uint16, uint8,
                               float64, float32, float16,
                               complex128, complex64, bool_)
        if ndarray is not FakeObject:
            # Save printoptions
            np_printoptions = get_printoptions()
            # Set max number of elements to show for Numpy arrays
            # in our display
            set_printoptions(threshold=10)
        if isinstance(value, recarray):
            if level == 0:
                fields = value.names
                display = 'Field names: ' + ', '.join(fields)
            else:
                display = 'Recarray'
        elif isinstance(value, MaskedArray):
            display = 'Masked array'
        elif isinstance(value, ndarray):
            if level == 0:
                if minmax:
                    try:
                        display = 'Min: %r\nMax: %r' % (value.min(), value.max())
                    except (TypeError, ValueError):
                        if value.dtype.type in numeric_numpy_types:
                            display = str(value)
                        else:
                            display = default_display(value)
                elif value.dtype.type in numeric_numpy_types:
                    display = str(value)
                else:
                    display = default_display(value)
                display = truncate_rows(display, MAX_NUMBER_OF_LINES,
                                        MAX_LINE_LENGTH)
                truncated = True
            else:
                display = 'Numpy array'
        elif any([type(value) == t for t in [list, set, tuple, dict]]):
            display = collections_display(value, level+1)
        elif isinstance(value, Image):
            if level == 0:
                display = '%s  Mode: %s' % (address(value), value.mode)
            else:
                display = 'Image'
        elif isinstance(value, DataFrame):
            if level == 0:
                cols = value.columns
                if PY2 and len(cols) > 0:
                    # Get rid of possible BOM utf-8 data present at the
                    # beginning of a file, which gets attached to the first
                    # column header when headers are present in the first
                    # row.
                    # Fixes Issue 2514
                    try:
                        ini_col = to_text_string(cols[0], encoding='utf-8-sig')
                    except:
                        ini_col = to_text_string(cols[0])
                    cols = [ini_col] + [to_text_string(c) for c in cols[1:]]
                else:
                    cols = [to_text_string(c) for c in cols]
                display = 'Column names: ' + ', '.join(list(cols))
            else:
                display = 'Dataframe'
        elif isinstance(value, NavigableString):
            # Fixes Issue 2448
            display = to_text_string(value)
            if level > 0:
                display = u"'" + display + u"'"
        elif isinstance(value, Index):
            if level == 0:
                try:
                    display = value._summary()
                except AttributeError:
                    display = value.summary()
            else:
                display = 'Index'
        elif isinstance(value, Tuple):
            if level == 0:
                # Convert to tuple for printing (value.args is a tuple already)
                display = value_to_display(value.args, level=1)
            else:
                display = 'SymPy Tuple'
        elif isinstance(value, Set):
            if level == 0:
                # Convert to set for displaying
                display = value_to_display(set(value.args))
            else:
                display = 'SymPy Set'
        elif isinstance(value, (Basic, MatrixBase, NDimArray)):
            if level == 0:
                try:
                    from sympy import pretty
                    display = pretty(value)
                    truncated = True
                    display = truncate_rows(display,
                                            linelength=MAX_LINE_LENGTH)
                except:
                    display = repr(value)
            else:
                display = 'SymPy expression'
                try:
                    # Some types, as symbols and numbers, are often short
                    # (and single line) so print these even at higher levels
                    from sympy import Integer, Float, Symbol, MatrixSymbol
                    if isinstance(value, (Integer, Float, Symbol,
                                          MatrixSymbol)):
                        from sympy import pretty
                        display = pretty(value)
                except:
                    pass
        elif is_binary_string(value):
            # We don't apply this to classes that extend string types
            # See issue 5636
            if is_type_text_string(value):
                try:
                    display = to_text_string(value, 'utf8')
                    if level > 0:
                        display = u"'" + display + u"'"
                except:
                    display = value
                    if level > 0:
                        display = b"'" + display + b"'"
            else:
                display = default_display(value)
        elif is_text_string(value):
            # We don't apply this to classes that extend string types
            # See issue 5636
            if is_type_text_string(value):
                display = value
                if level > 0:
                    display = u"'" + display + u"'"
            else:
                display = default_display(value)
        elif (isinstance(value, datetime.date) or
              isinstance(value, datetime.timedelta)):
            display = str(value)
        elif (isinstance(value, NUMERIC_TYPES) or
              isinstance(value, bool) or
              isinstance(value, numeric_numpy_types)):
            display = repr(value)
        else:
            if level == 0:
                display = default_display(value)
            else:
                display = default_display(value, with_module=False)
    except:
        display = default_display(value)

    # Truncate display to MAX_NUMBER_OF_LINES lines and MAX_LINE_LENGTH chars
    # to avoid freezing Spyder because of large displays
    if not truncated:
        display = truncate_rows(display, MAX_NUMBER_OF_LINES, MAX_LINE_LENGTH)

    # Restore Numpy printoptions
    if np_printoptions is not FakeObject:
        set_printoptions(**np_printoptions)

    return display


def display_to_value(value, default_value, ignore_errors=True):
    """Convert back to value"""
    from qtpy.compat import from_qvariant
    value = from_qvariant(value, to_text_string)
    try:
        np_dtype = get_numpy_dtype(default_value)
        if isinstance(default_value, bool):
            # We must test for boolean before NumPy data types
            # because `bool` class derives from `int` class
            try:
                value = bool(float(value))
            except ValueError:
                value = value.lower() == "true"
        elif np_dtype is not None:
            if 'complex' in str(type(default_value)):
                value = np_dtype(complex(value))
            else:
                value = np_dtype(value)
        elif isinstance(default_value, Tuple):
            # Check Tuple before Basic as Tuple is instance of Basic
            try:
                from sympy import sympify
                # Assume that it is still on tuple
                value = Tuple(*sympify(value))
            except:
                try:
                    # If not (maybe only one item left, and forgotten ",")
                    value = Tuple(sympify(value))
                except:
                    # Something went wrong, restore
                    value = default_value
        elif isinstance(default_value, (MatrixBase, NDimArray)):
            try:
                from sympy import sympify
                # Use class as there are many variants
                # (mutable/immutable/dense/sparse)
                value = default_value.__class__(sympify(value))
            except:
                # Something went wrong, restore
                value = default_value
        elif isinstance(default_value, Basic):
            try:
                from sympy import sympify
                value = sympify(value)
            except:
                value = default_value
        elif is_binary_string(default_value):
            value = to_binary_string(value, 'utf8')
        elif is_text_string(default_value):
            value = to_text_string(value)
        elif isinstance(default_value, complex):
            value = complex(value)
        elif isinstance(default_value, float):
            value = float(value)
        elif isinstance(default_value, int):
            try:
                value = int(value)
            except ValueError:
                value = float(value)
        elif isinstance(default_value, datetime.datetime):
            value = datestr_to_datetime(value)
        elif isinstance(default_value, datetime.date):
            value = datestr_to_datetime(value).date()
        elif isinstance(default_value, datetime.timedelta):
            value = str_to_timedelta(value)
        elif ignore_errors:
            value = try_to_eval(value)
        else:
            value = eval(value)
    except (ValueError, SyntaxError):
        if ignore_errors:
            value = try_to_eval(value)
        else:
            return default_value
    return value


# =============================================================================
# Types
# =============================================================================
def get_type_string(item):
    """Return type string of an object."""
    if isinstance(item, DataFrame):
        return "DataFrame"
    if isinstance(item, Index):
        return type(item).__name__
    if isinstance(item, Series):
        return "Series"
    found = re.findall(r"<(?:type|class) '(\S*)'>",
                       to_text_string(type(item)))
    if found:
        return found[0]


def is_known_type(item):
    """Return True if object has a known type"""
    # Unfortunately, the masked array case is specific
    return isinstance(item, MaskedArray) or get_type_string(item) is not None


def get_human_readable_type(item):
    """Return human-readable type string of an item"""
    if isinstance(item, (ndarray, MaskedArray)):
        return item.dtype.name
    elif isinstance(item, Image):
        return "Image"
    else:
        text = get_type_string(item)
        if text is None:
            text = to_text_string('unknown')
        else:
            return text[text.find('.')+1:]


#==============================================================================
# Globals filter: filter namespace dictionaries (to be edited in
# CollectionsEditor)
#==============================================================================
def is_supported(value, check_all=False, filters=None, iterate=False):
    """Return True if the value is supported, False otherwise"""
    assert filters is not None
    if value is None:
        return True
    if not is_editable_type(value):
        return False
    elif not isinstance(value, filters):
        return False
    elif iterate:
        if isinstance(value, (list, tuple, set)):
            valid_count = 0
            for val in value:
                if is_supported(val, filters=filters, iterate=check_all):
                    valid_count += 1
                if not check_all:
                    break
            return valid_count > 0
        elif isinstance(value, dict):
            for key, val in list(value.items()):
                if not is_supported(key, filters=filters, iterate=check_all) \
                   or not is_supported(val, filters=filters,
                                       iterate=check_all):
                    return False
                if not check_all:
                    break
    return True


def globalsfilter(input_dict, check_all=False, filters=None,
                  exclude_private=None, exclude_capitalized=None,
                  exclude_uppercase=None, exclude_unsupported=None,
                  excluded_names=None):
    """Keep only objects that can be pickled"""
    output_dict = {}
    for key, value in list(input_dict.items()):
        excluded = (exclude_private and key.startswith('_')) or \
                   (exclude_capitalized and key[0].isupper()) or \
                   (exclude_uppercase and key.isupper()
                    and len(key) > 1 and not key[1:].isdigit()) or \
                   (key in excluded_names) or \
                   (exclude_unsupported and \
                    not is_supported(value, check_all=check_all,
                                     filters=filters))
        if not excluded:
            output_dict[key] = value
    return output_dict


#==============================================================================
# Create view to be displayed by NamespaceBrowser
#==============================================================================
REMOTE_SETTINGS = ('check_all', 'exclude_private', 'exclude_uppercase',
                   'exclude_capitalized', 'exclude_unsupported',
                   'excluded_names', 'minmax', 'show_callable_attributes',
                   'show_special_attributes')


def get_supported_types():
    """
    Return a dictionnary containing types lists supported by the
    namespace browser.

    Note:
    If you update this list, don't forget to update variablexplorer.rst
    in spyder-docs
    """
    from datetime import date, timedelta
    editable_types = [int, float, complex, list, set, dict, tuple, date,
                      timedelta] + list(TEXT_TYPES) + list(INT_TYPES)
    try:
        from numpy import ndarray, matrix, generic
        editable_types += [ndarray, matrix, generic]
    except:
        pass
    try:
        from pandas import DataFrame, Series, DatetimeIndex
        editable_types += [DataFrame, Series, Index]
    except:
        pass
    try:
        from sympy import Basic, NDimArray, MatrixBase
        editable_types += [Basic, NDimArray, MatrixBase]
    except:
        pass
    picklable_types = editable_types[:]
    try:
        from spyder.pil_patch import Image
        editable_types.append(Image.Image)
    except:
        pass
    return dict(picklable=picklable_types, editable=editable_types)


def get_remote_data(data, settings, mode, more_excluded_names=None):
    """
    Return globals according to filter described in *settings*:
        * data: data to be filtered (dictionary)
        * settings: variable explorer settings (dictionary)
        * mode (string): 'editable' or 'picklable'
        * more_excluded_names: additional excluded names (list)
    """
    supported_types = get_supported_types()
    assert mode in list(supported_types.keys())
    excluded_names = settings['excluded_names']
    if more_excluded_names is not None:
        excluded_names += more_excluded_names
    return globalsfilter(data, check_all=settings['check_all'],
                         filters=tuple(supported_types[mode]),
                         exclude_private=settings['exclude_private'],
                         exclude_uppercase=settings['exclude_uppercase'],
                         exclude_capitalized=settings['exclude_capitalized'],
                         exclude_unsupported=settings['exclude_unsupported'],
                         excluded_names=excluded_names)


def make_remote_view(data, settings, more_excluded_names=None):
    """
    Make a remote view of dictionary *data*
    -> globals explorer
    """
    data = get_remote_data(data, settings, mode='editable',
                           more_excluded_names=more_excluded_names)
    remote = {}
    for key, value in list(data.items()):
        view = value_to_display(value, minmax=settings['minmax'])
        remote[key] = {'type':  get_human_readable_type(value),
                       'size':  get_size(value),
                       'color': get_color_name(value),
                       'view':  view}
    return remote
