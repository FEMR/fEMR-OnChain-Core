try:
    from django_silk.profiling.profiler import silk_profile
except ImportError:
    def silk_profile(name=None):
        def decorator(func):
            return func
        return decorator
