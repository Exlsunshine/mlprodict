# -*- encoding: utf-8 -*-
# pylint: disable=E0203,E1101,C0111
"""
@file
@brief Runtime operator.
"""
from ._op import OpRun


class Mean(OpRun):

    def __init__(self, onnx_node, desc=None, **options):
        OpRun.__init__(self, onnx_node, desc=desc,
                       **options)

    def _run(self, *args):  # pylint: disable=W0221
        res = args[0].copy()
        for m in args[1:]:
            res += m
        return (res / len(args), )
