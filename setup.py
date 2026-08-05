from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "job_matcher",
    ["cpp_engine/job_matcher.cpp"],
    ),
]

setup(
    name="job_matcher",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)
