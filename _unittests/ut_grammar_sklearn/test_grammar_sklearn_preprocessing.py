"""
@brief      test log(time=2s)
"""
import unittest
import numpy
from pyquickhelper.pycode import ExtTestCase
from mlprodict.testing import check_model_representation


class TestGrammarSklearnPreprocessing(ExtTestCase):

    def test_sklearn_scaler(self):
        from sklearn.preprocessing import StandardScaler
        data = numpy.array([[0, 0], [0, 0], [1, 1], [1, 1]],
                           dtype=numpy.float32)
        check_model_representation(
            StandardScaler, data, verbose=False)
        # The second compilation fails if suffix is not specified.
        check_model_representation(
            model=StandardScaler, X=data, verbose=False, suffix="_2")


if __name__ == "__main__":
    unittest.main()
