
.. |gitlogo| image:: _static/git_logo.png
             :height: 20

mlprodict
=========

**Links:** `github <https://github.com/sdpython/mlprodict/>`_,
`documentation <http://www.xavierdupre.fr/app/mlprodict/helpsphinx/index.html>`_,
:ref:`l-README`,
:ref:`blog <ap-main-0>`

.. image:: https://travis-ci.org/sdpython/mlprodict.svg?branch=master
    :target: https://travis-ci.org/sdpython/mlprodict
    :alt: Build status

.. image:: https://ci.appveyor.com/api/projects/status/g8chk1ufyk1m8uep?svg=true
    :target: https://ci.appveyor.com/project/sdpython/mlprodict
    :alt: Build Status Windows

.. image:: https://circleci.com/gh/sdpython/mlprodict/tree/master.svg?style=svg
    :target: https://circleci.com/gh/sdpython/mlprodict/tree/master

.. image:: https://dev.azure.com/xavierdupre3/mlprodict/_apis/build/status/sdpython.mlprodict
    :target: https://dev.azure.com/xavierdupre3/mlprodict/

.. image:: https://badge.fury.io/py/mlprodict.svg
    :target: https://pypi.org/project/mlprodict/

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: MIT License
    :target: http://opensource.org/licenses/MIT

.. image:: https://requires.io/github/sdpython/mlprodict/requirements.svg?branch=master
     :target: https://requires.io/github/sdpython/mlprodict/requirements/?branch=master
     :alt: Requirements Status

.. image:: https://codecov.io/github/sdpython/mlprodict/coverage.svg?branch=master
    :target: https://codecov.io/github/sdpython/mlprodict?branch=master

.. image:: http://img.shields.io/github/issues/sdpython/mlprodict.png
    :alt: GitHub Issues
    :target: https://github.com/sdpython/mlprodict/issues

.. image:: nbcov.png
    :target: http://www.xavierdupre.fr/app/mlprodict/helpsphinx/all_notebooks_coverage.html
    :alt: Notebook Coverage

.. image:: https://pepy.tech/badge/mlprodict
    :target: https://pypi.org/project/mlprodict/
    :alt: Downloads

.. image:: https://img.shields.io/github/forks/sdpython/mlprodict.svg
    :target: https://github.com/sdpython/pyquickhelper/
    :alt: Forks

.. image:: https://img.shields.io/github/stars/sdpython/mlprodict.svg
    :target: https://github.com/sdpython/mlprodict/
    :alt: Stars

.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/sdpython/mlprodict/master?filepath=_doc%2Fnotebooks

.. toctree::
    :maxdepth: 1

    tutorial/index
    api/index
    onnx
    i_cmd
    i_ex
    i_index
    gyexamples/index
    all_notebooks
    HISTORY

*mlprodict* explores couple of ways to compute predictions faster
than the library used to build the machine learned model,
mostly :epkg:`scikit-learn` which is optimized for training,
which is equivalent to batch predictions.
One way is to use :epkg:`ONNX`.
:epkg:`onnxruntime` provides an efficient way
to compute predictions. The current code explores ways to be faster
at implementing something working and provides a :epkg:`python`
runtime for :epkg:`ONNX`.

.. runpython::
    :showcode:

    from sklearn.linear_model import LinearRegression
    from sklearn.datasets import load_iris
    from mlprodict.onnxrt import OnnxInference, measure_relative_difference
    import numpy

    iris = load_iris()
    X = iris.data[:, :2]
    y = iris.target
    lr = LinearRegression()
    lr.fit(X, y)

    # Predictions with scikit-learn.
    expected = lr.predict(X[:5])
    print(expected)

    # Conversion into ONNX.
    from mlprodict.onnxrt import to_onnx
    model_onnx = to_onnx(lr, X.astype(numpy.float32))
    print("ONNX:", str(model_onnx)[:200] + "\n...")

    # Predictions with onnxruntime
    oinf = OnnxInference(model_onnx, runtime='onnxruntime1')
    ypred = oinf.run({'X': X[:5].astype(numpy.float32)})
    print("ONNX output:", ypred)

    # Measuring the maximum difference.
    print("max abs diff:", measure_relative_difference(expected, ypred['variable']))

These predictions are obtained with the
following :epkg:`ONNX` graph.

.. gdot::
    :script: DOT-SECTION

    from sklearn.linear_model import LinearRegression
    from sklearn.datasets import load_iris
    from mlprodict.onnxrt import OnnxInference
    import numpy

    iris = load_iris()
    X = iris.data[:, :2]
    y = iris.target
    lr = LinearRegression()
    lr.fit(X, y)

    from mlprodict.onnxrt import to_onnx
    model_onnx = to_onnx(lr, X.astype(numpy.float32))
    oinf = OnnxInference(model_onnx)
    print("DOT-SECTION", oinf.to_dot())

Notebook :ref:`onnxvisualizationrst`
shows how to visualize an :epkg:`ONNX` pipeline.
Another way is to convert the prediction function
into :epkg:`C`.

.. runpython::
    :showcode:

    from sklearn.linear_model import LogisticRegression
    from sklearn.datasets import load_iris

    iris = load_iris()
    X = iris.data[:, :2]
    y = iris.target
    y[y == 2] = 1
    lr = LogisticRegression()
    lr.fit(X, y)

    # Conversion into a graph.
    from mlprodict.grammar_sklearn import sklearn2graph
    gr = sklearn2graph(lr, output_names=['Prediction', 'Score'])

    # Conversion into C
    ccode = gr.export(lang='c')
    # We print after a little bit of cleaning (remove all comments)
    print("\n".join(_ for _ in ccode['code'].split("\n") if "//" not in _))

+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`l-modules`     |  :ref:`l-functions` | :ref:`l-classes`    | :ref:`l-methods`   | :ref:`l-staticmethods` | :ref:`l-properties`                            |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`modindex`      |  :ref:`l-EX2`       | :ref:`search`       | :ref:`l-license`   | :ref:`l-changes`       | :ref:`l-README`                                |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
| :ref:`genindex`      |  :ref:`l-FAQ2`      | :ref:`l-notebooks`  |                    | :ref:`l-statcode`      | `Unit Test Coverage <coverage/index.html>`_    |
+----------------------+---------------------+---------------------+--------------------+------------------------+------------------------------------------------+
