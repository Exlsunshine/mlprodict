"""
@file
@brief Functions which converts :epkg:`ONNX` object into
readable :epgk:`python` objects.
"""
import warnings
import numpy
from onnx import onnx_pb as onnx_proto


def _numpy_array(data, dtype=None, copy=True):
    """
    Single function to create an array.

    @param      data        data
    @param      dtype       dtype
    @param      copy        copy
    """
    if isinstance(data, numpy.ndarray):
        res = data
    else:
        res = numpy.array(data, dtype=dtype, copy=copy)
    return res


def _elem_type_as_str(elem_type):
    if elem_type == onnx_proto.TensorProto.FLOAT:  # pylint: disable=E1101
        return 'float'
    if elem_type == onnx_proto.TensorProto.BOOL:  # pylint: disable=E1101
        return 'bool'
    if elem_type == onnx_proto.TensorProto.DOUBLE:  # pylint: disable=E1101
        return 'double'
    if elem_type == onnx_proto.TensorProto.STRING:  # pylint: disable=E1101
        return 'str'
    if elem_type == onnx_proto.TensorProto.INT64:  # pylint: disable=E1101
        return 'int64'
    if elem_type == onnx_proto.TensorProto.INT32:  # pylint: disable=E1101
        return 'int32'

    # The following code should be refactored.
    selem = str(elem_type)

    if selem.startswith("tensor_type"):
        this = elem_type.tensor_type
        et = _elem_type_as_str(this.elem_type)
        shape = this.shape
        dim = shape.dim
        dims = [d.dim_value for d in dim]
        if len(dims) == 0:
            dims = '?'
        return {'kind': 'tensor', 'elem': et, 'shape': shape}

    if selem.startswith("map_type"):
        this = elem_type.map_type
        kt = _elem_type_as_str(this.key_type)
        vt = _elem_type_as_str(this.value_type)
        return {'kind': 'map', 'key': kt, 'value': vt}

    import pprint
    raise NotImplementedError("elem_type '{}' is unknown\nfields:\n{}\n-----\n{}.".format(
        elem_type, pprint.pformat(dir(elem_type)), type(elem_type)))


def _var_as_dict(var):
    """
    Converts a protobuf object into something readable.
    The current implementation relies on :epkg:`json`.
    That's not the most efficient way.
    """
    if hasattr(var, 'type') and str(var.type) != '':
        # variable
        if var.type is not None:
            if hasattr(var.type, 'tensor_type') and var.type.tensor_type.elem_type > 0:
                t = var.type.tensor_type
                elem_type = _elem_type_as_str(t.elem_type)
                shape = t.shape
                dim = shape.dim
                dims = [d.dim_value for d in dim]
                if len(dims) == 0:
                    dims = '?'
                dtype = dict(kind='tensor', elem=elem_type,
                             shape=tuple(dims))
            elif hasattr(var.type, 'real') and var.type.real == 5 and hasattr(var, 'g'):
                dtype = dict(kind='graph', elem=var.type.real)
            elif hasattr(var.type, 'real') and var.type.real == 4 and hasattr(var, 't'):
                dtype = dict(kind='tensor', elem=var.type.real)
            elif hasattr(var.type, 'real'):
                dtype = dict(kind='real', elem=var.type.real)
            elif (hasattr(var.type, "sequence_type") and var.type.sequence_type is not None and
                    str(var.type.sequence_type.elem_type) != ''):
                t = var.type.sequence_type
                elem_type = _elem_type_as_str(t.elem_type)
                dtype = dict(kind='sequence', elem=elem_type)
            elif (hasattr(var.type, "map_type") and var.type.map_type is not None and
                    str(var.type.map_type.key_type) != '' and
                    str(var.type.map_type.value_type) != ''):
                t = var.type.map_type
                key_type = _elem_type_as_str(t.key_type)
                value_type = _elem_type_as_str(t.value_type)
                dtype = dict(kind='map', key=key_type, value=value_type)
            else:
                import pprint
                raise NotImplementedError("Unable to convert a type into a dictionary for '{}'. "
                                          "Available fields: {}.".format(var.type, pprint.pformat(dir(var.type))))
        else:
            import pprint
            raise NotImplementedError("Unable to convert variable into a dictionary for '{}'. "
                                      "Available fields: {}.".format(var, pprint.pformat(dir(var.type))))

        res = dict(name=var.name, type=dtype)

        if hasattr(var, 'floats') and dtype.get('elem', None) == 6:
            res['value'] = _numpy_array(var.floats, dtype=numpy.float32)
        elif hasattr(var, 'strings') and dtype.get('elem', None) == 8:
            res['value'] = _numpy_array(var.strings)
        elif hasattr(var, 'ints') and dtype.get('elem', None) == 7:
            res['value'] = _numpy_array(var.ints)
        elif hasattr(var, 'f') and dtype.get('elem', None) == 1:
            res['value'] = var.f
        elif hasattr(var, 's') and dtype.get('elem', None) == 3:
            res['value'] = var.s
        elif hasattr(var, 'i') and dtype.get('elem', None) == 2:
            res['value'] = var.i
        elif hasattr(var, 'g') and dtype.get('elem', None) == 5:
            res['value'] = var.g
        elif hasattr(var, 't') and dtype.get('elem', None) == 4:
            ts = _var_as_dict(var.t)
            res['value'] = ts['value']
        elif "'value'" in str(var):
            warnings.warn("No value: {} -- {}".format(
                dtype, str(var).replace("\n", "").replace(" ", "")))
        return res

    elif hasattr(var, 'op_type'):
        if hasattr(var, 'attribute'):
            atts = {}
            for att in var.attribute:
                atts[att.name] = _var_as_dict(att)
        return dict(name=var.name, op_type=var.op_type,
                    domain=var.domain, atts=atts)

    elif hasattr(var, 'dims') and len(var.dims) > 0:
        # initializer
        dims = [d for d in var.dims]
        if var.data_type == 1 and var.float_data is not None:
            try:
                data = _numpy_array(var.float_data, dtype=numpy.float32,
                                    copy=False).reshape(dims)
            except ValueError:
                from onnx.numpy_helper import to_array
                data = _numpy_array(to_array(var))
        elif var.data_type == 11 and var.double_data is not None:
            try:
                data = _numpy_array(var.double_data, dtype=numpy.float64,
                                    copy=False).reshape(dims)
            except ValueError:
                from onnx.numpy_helper import to_array
                data = _numpy_array(to_array(var))
        elif var.data_type == 6 and var.int32_data is not None:
            data = _numpy_array(var.int32_data, dtype=numpy.int32,
                                copy=False).reshape(dims)
        elif var.data_type == 7 and var.int64_data is not None:
            data = _numpy_array(var.int64_data, dtype=numpy.int64,
                                copy=False).reshape(dims)
        else:
            raise NotImplementedError(
                "Iniatilizer {} cannot be converted into a dictionary.".format(var))
        return dict(name=var.name, value=data)

    elif hasattr(var, 'data_type') and var.data_type > 0:
        if var.data_type == 1 and var.float_data is not None:
            data = _numpy_array(var.float_data, dtype=numpy.float32,
                                copy=False)
        elif var.data_type == 6 and var.int32_data is not None:
            data = _numpy_array(var.int32_data, dtype=numpy.int32,
                                copy=False)
        elif var.data_type == 7 and var.int64_data is not None:
            data = _numpy_array(var.int64_data, dtype=numpy.int64,
                                copy=False)
        elif var.data_type == 11 and var.double_data is not None:
            data = _numpy_array(var.double_data, dtype=numpy.float64,
                                copy=False)
        else:
            raise NotImplementedError(
                "Iniatilizer {} cannot be converted into a dictionary.".format(var))
        return dict(name=var.name, value=data)

    else:
        raise NotImplementedError(
            "Unable to guess which object it is.\n{}".format(var))


def _type_to_string(dtype):
    """
    Converts a type into a readable string.
    """
    if not isinstance(dtype, dict):
        dtype_ = _var_as_dict(dtype)
    else:
        dtype_ = dtype
    if dtype_["kind"] == 'tensor':
        return "{0}({1})".format(dtype_['elem'], dtype_['shape'])
    if dtype_['kind'] == 'sequence':
        return "[{0}]".format(_type_to_string(dtype_['elem']))
    if dtype_["kind"] == 'map':
        return "{{{0}, {1}}}".format(dtype_['key'], dtype_['value'])
    raise NotImplementedError(
        "Unable to convert into string {} or {}.".format(dtype, dtype_))
