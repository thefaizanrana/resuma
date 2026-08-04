"""Thin wrapper around the compiled job_matcher C++ extension."""

try:
    import job_matcher
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        'The C++ matching engine is not built. '
        'Run: cd cpp_engine && python setup.py build_ext --inplace'
    ) from exc

calculate_match = job_matcher.calculate_match
