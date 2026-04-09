from importlib.metadata import version, PackageNotFoundError as DistributionNotFound

def get_distribution(name):
    class _Dist:
        def __init__(self, n):
            try:
                self.version = version(n)
            except DistributionNotFound:
                self.version = "0.0.0"
    return _Dist(name)
