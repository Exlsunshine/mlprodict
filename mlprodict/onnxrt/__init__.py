# -*- encoding: utf-8 -*-
"""
@file
@brief Shortcut to *sklapi*.
"""
from .onnx_inference import OnnxInference
from .validate_difference import measure_relative_difference
from .validate_helper import get_opset_number_from_onnx, sklearn_operators, to_onnx
