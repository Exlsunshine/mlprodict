# -*- encoding: utf-8 -*-
# pylint: disable=E0203,E1101,C0111
"""
@file
@brief Runtime operator.
"""
import numpy
from ._op import OpRun


class ArgMax(OpRun):

    atts = {'axis': 0, 'keepdims': 1}

    def __init__(self, onnx_node, desc=None, **options):
        OpRun.__init__(self, onnx_node, desc=desc,
                       expected_attributes=ArgMax.atts,
                       **options)

    def _run(self, data):  # pylint: disable=W0221
        r = numpy.argmax(data, axis=self.axis)
        if self.keepdims == 0:
            return (r, )
        else:
            if len(data.shape) == 2:
                if self.axis == 0:
                    return (r[numpy.newaxis, :], )
                else:
                    return (r[:, numpy.newaxis], )
            else:
                raise NotImplementedError(
                    "keepdims not implemented for dimension > 2.")
