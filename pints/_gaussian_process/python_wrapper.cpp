#include "GaussianProcessDenseMatrix.hpp"
#include "GaussianProcessH2Matrix.hpp"
#include "GaussianProcessDirect.hpp"
#include "GaussianProcessMatrixFree.hpp"

namespace py = pybind11;
using namespace Aboria;

PYBIND11_MODULE(gaussian_process, m) {

#define ADD_DIMENSION(D)                                                       \
  py::class_<GaussianProcessMatrixFree<D>>(m, "GaussianProcessMatrixFree" #D)  \
      .def(py::init<>())                                                       \
      .def("grad_likelihood", &GaussianProcessMatrixFree<D>::grad_likelihood)  \
      .def("likelihood", &GaussianProcessMatrixFree<D>::likelihood)            \
      .def("predict", &GaussianProcessMatrixFree<D>::predict)                  \
      .def("predict_var", &GaussianProcessMatrixFree<D>::predict_var)          \
      .def("set_data", &GaussianProcessMatrixFree<D>::set_data,                \
           py::arg().noconvert(), py::arg().noconvert())                       \
      .def("n_parameters", &GaussianProcessMatrixFree<D>::n_parameters)        \
      .def("set_parameters", &GaussianProcessMatrixFree<D>::set_parameters)    \
      .def("set_uninitialised",                                                \
           &GaussianProcessMatrixFree<D>::set_uninitialised)                   \
      .def("set_max_iterations",                                               \
           &GaussianProcessMatrixFree<D>::set_max_iterations)                  \
      .def("set_tolerance", &GaussianProcessMatrixFree<D>::set_tolerance)      \
      .def("set_chebyshev_n", &GaussianProcessMatrixFree<D>::set_chebyshev_n)  \
      .def("set_stochastic_samples",                                           \
           &GaussianProcessMatrixFree<D>::set_stochastic_samples);             \
                                                                               \
  py::class_<GaussianProcessH2Matrix<D>>(m, "GaussianProcessH2Matrix" #D)      \
      .def(py::init<>())                                                       \
      .def("grad_likelihood", &GaussianProcessH2Matrix<D>::grad_likelihood)    \
      .def("likelihood", &GaussianProcessH2Matrix<D>::likelihood)              \
      .def("print_h2_errors", &GaussianProcessH2Matrix<D>::print_h2_errors)    \
      .def("predict", &GaussianProcessH2Matrix<D>::predict)                    \
      .def("predict_var", &GaussianProcessH2Matrix<D>::predict_var)            \
      .def("set_data", &GaussianProcessH2Matrix<D>::set_data,                  \
           py::arg().noconvert(), py::arg().noconvert())                       \
      .def("n_parameters", &GaussianProcessH2Matrix<D>::n_parameters)          \
      .def("set_parameters", &GaussianProcessH2Matrix<D>::set_parameters)      \
      .def("set_h2_order", &GaussianProcessH2Matrix<D>::set_h2_order)          \
      .def("set_uninitialised",                                                \
           &GaussianProcessH2Matrix<D>::set_uninitialised)                     \
      .def("set_max_iterations",                                               \
           &GaussianProcessH2Matrix<D>::set_max_iterations)                    \
      .def("set_tolerance", &GaussianProcessH2Matrix<D>::set_tolerance)        \
      .def("set_chebyshev_n", &GaussianProcessH2Matrix<D>::set_chebyshev_n)    \
      .def("set_stochastic_samples",                                           \
           &GaussianProcessH2Matrix<D>::set_stochastic_samples);               \
                                                                               \
  py::class_<GaussianProcessDirect<D>>(m, "GaussianProcessDirect" #D)          \
      .def(py::init<>())                                                       \
      .def("grad_likelihood", &GaussianProcessDirect<D>::grad_likelihood)      \
      .def("likelihood", &GaussianProcessDirect<D>::likelihood)                \
      .def("predict", &GaussianProcessDirect<D>::predict)                      \
      .def("predict_var", &GaussianProcessDirect<D>::predict_var)              \
      .def("set_data", &GaussianProcessDirect<D>::set_data,                    \
           py::arg().noconvert(), py::arg().noconvert())                       \
      .def("n_parameters", &GaussianProcessDirect<D>::n_parameters)            \
      .def("set_parameters", &GaussianProcessDirect<D>::set_parameters)        \
      .def("set_uninitialised", &GaussianProcessDirect<D>::set_uninitialised); \
                                                                               \
  py::class_<GaussianProcessDenseMatrix<D>>(m,                                 \
                                            "GaussianProcessDenseMatrix" #D)   \
      .def(py::init<>())                                                       \
      .def("grad_likelihood", &GaussianProcessDenseMatrix<D>::grad_likelihood) \
      .def("likelihood", &GaussianProcessDenseMatrix<D>::likelihood)           \
      .def("predict", &GaussianProcessDenseMatrix<D>::predict)                 \
      .def("predict_var", &GaussianProcessDenseMatrix<D>::predict_var)         \
      .def("set_data", &GaussianProcessDenseMatrix<D>::set_data,               \
           py::arg().noconvert(), py::arg().noconvert())                       \
      .def("n_parameters", &GaussianProcessDenseMatrix<D>::n_parameters)       \
      .def("set_uninitialised",                                                \
           &GaussianProcessDenseMatrix<D>::set_uninitialised)                  \
      .def("set_parameters", &GaussianProcessDenseMatrix<D>::set_parameters)   \
      .def("set_max_iterations",                                               \
           &GaussianProcessDenseMatrix<D>::set_max_iterations)                 \
      .def("set_tolerance", &GaussianProcessDenseMatrix<D>::set_tolerance)     \
      .def("set_chebyshev_n", &GaussianProcessDenseMatrix<D>::set_chebyshev_n) \
      .def("set_stochastic_samples",                                           \
           &GaussianProcessDenseMatrix<D>::set_stochastic_samples);

  ADD_DIMENSION(1)
  ADD_DIMENSION(2)
  ADD_DIMENSION(4)
  ADD_DIMENSION(9)
}
