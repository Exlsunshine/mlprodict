# -*- encoding: utf-8 -*-
# pylint: disable=E0203,E1101,C0111
"""
@file
@brief Runtime operator.
"""
from collections import OrderedDict
import numpy
from ._op_helper import _get_typed_class_attribute
from ._op import OpRunUnaryNum, RuntimeTypeError
from ._new_ops import OperatorSchema
from .op_tree_ensemble_regressor_ import (  # pylint: disable=E0611
    RuntimeTreeEnsembleRegressorFloat,
    RuntimeTreeEnsembleRegressorDouble,
)


class TreeEnsembleRegressorCommon(OpRunUnaryNum):

    def __init__(self, dtype, onnx_node, desc=None,
                 expected_attributes=None, **options):
        OpRunUnaryNum.__init__(self, onnx_node, desc=desc,
                               expected_attributes=expected_attributes,
                               **options)
        self._init(dtype=dtype)

    def _get_typed_attributes(self, k):
        return _get_typed_class_attribute(self, k, self.__class__.atts)

    def _find_custom_operator_schema(self, op_name):
        """
        Finds a custom operator defined by this runtime.
        """
        if op_name == "TreeEnsembleRegressorDouble":
            return TreeEnsembleRegressorDoubleSchema()
        raise RuntimeError(
            "Unable to find a schema for operator '{}'.".format(op_name))

    def _init(self, dtype):
        if dtype == numpy.float32:
            self.rt_ = RuntimeTreeEnsembleRegressorFloat()
        elif dtype == numpy.float64:
            self.rt_ = RuntimeTreeEnsembleRegressorDouble()
        else:
            raise RuntimeTypeError("Unsupported dtype={}.".format(dtype))
        atts = [self._get_typed_attributes(k)
                for k in self.__class__.atts]
        self.rt_.init(*atts)

    def _run(self, x):  # pylint: disable=W0221
        """
        This is a C++ implementation coming from
        :epkg:`onnxruntime`.
        `tree_ensemble_classifier.cc
        <https://github.com/microsoft/onnxruntime/blob/master/onnxruntime/core/providers/cpu/ml/tree_ensemble_classifier.cc>`_.
        See class :class:`RuntimeTreeEnsembleRegressorFloat
        <mlprodict.onnxrt.ops_cpu.op_tree_ensemble_regressor_.RuntimeTreeEnsembleRegressorFloat>` or
        class :class:`RuntimeTreeEnsembleRegressorDouble
        <mlprodict.onnxrt.ops_cpu.op_tree_ensemble_regressor_.RuntimeTreeEnsembleRegressorDouble>`.
        """
        pred = self.rt_.compute(x)
        if pred.shape[0] != x.shape[0]:
            pred = pred.reshape(x.shape[0], pred.shape[0] // x.shape[0])
        return (pred, )


class TreeEnsembleRegressor(TreeEnsembleRegressorCommon):

    atts = OrderedDict([
        ('aggregate_function', b'SUM'),
        ('base_values', numpy.empty(0, dtype=numpy.float32)),
        ('n_targets', 1),
        ('nodes_falsenodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_featureids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_hitrates', numpy.empty(0, dtype=numpy.float32)),
        ('nodes_missing_value_tracks_true', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_modes', []),
        ('nodes_nodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_treeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_truenodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_values', numpy.empty(0, dtype=numpy.float32)),
        ('post_transform', b'NONE'),
        ('target_ids', numpy.empty(0, dtype=numpy.int64)),
        ('target_nodeids', numpy.empty(0, dtype=numpy.int64)),
        ('target_treeids', numpy.empty(0, dtype=numpy.int64)),
        ('target_weights', numpy.empty(0, dtype=numpy.float32)),
    ])

    def __init__(self, onnx_node, desc=None, **options):
        TreeEnsembleRegressorCommon.__init__(
            self, numpy.float32, onnx_node, desc=desc,
            expected_attributes=TreeEnsembleRegressor.atts,
            **options)


class TreeEnsembleRegressorDouble(TreeEnsembleRegressorCommon):

    atts = OrderedDict([
        ('aggregate_function', b'SUM'),
        ('base_values', numpy.empty(0, dtype=numpy.float64)),
        ('n_targets', 1),
        ('nodes_falsenodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_featureids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_hitrates', numpy.empty(0, dtype=numpy.float64)),
        ('nodes_missing_value_tracks_true', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_modes', []),
        ('nodes_nodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_treeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_truenodeids', numpy.empty(0, dtype=numpy.int64)),
        ('nodes_values', numpy.empty(0, dtype=numpy.float64)),
        ('post_transform', b'NONE'),
        ('target_ids', numpy.empty(0, dtype=numpy.int64)),
        ('target_nodeids', numpy.empty(0, dtype=numpy.int64)),
        ('target_treeids', numpy.empty(0, dtype=numpy.int64)),
        ('target_weights', numpy.empty(0, dtype=numpy.float64)),
    ])

    def __init__(self, onnx_node, desc=None, **options):
        TreeEnsembleRegressorCommon.__init__(
            self, numpy.float64, onnx_node, desc=desc,
            expected_attributes=TreeEnsembleRegressorDouble.atts,
            **options)


class TreeEnsembleRegressorDoubleSchema(OperatorSchema):
    """
    Defines a schema for operators added in this package
    such as @see cl TreeEnsembleRegressorDouble.
    """

    def __init__(self):
        OperatorSchema.__init__(self, 'TreeEnsembleRegressorDouble')
        self.attributes = TreeEnsembleRegressorDouble.atts
