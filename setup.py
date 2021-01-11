from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-pydfsoptimizer',
        packages=find_packages(),
        entry_points={
          'pangadfs.pool': ['pool_pydfs = plugin.pydfs.PyDfsPool'],
          'pangadfs.populate': ['populate_pydfs = plugin.pydfs:PyDfsPopulate'],
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
