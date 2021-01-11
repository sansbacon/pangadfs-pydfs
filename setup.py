from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-pydfsoptimizer',
        packages=find_packages(),
        entry_points={
          'pangadfs.pool': ['pool_pydfs = plugin:PyDfsPool'],
          'pangadfs.populate': ['populate_pydfs = plugin:PyDfsPopulate'],
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
