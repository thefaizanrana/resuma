from setuptools import Extension, setup

import pybind11

ext_modules = [
    Extension(
        "job_matcher",
        ["matcher.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
        extra_compile_args=["-std=c++17", "-O3"],
    ),
]

setup(
    name="job_matcher",
    version="0.2.0",
    description="High-performance C++ matching engine for the job portal",
    ext_modules=ext_modules,
    zip_safe=False,
)
