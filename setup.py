from setuptools import setup, find_packages


def run():
    setup(
        name='pangadfs-pydfs',
        packages=find_packages(),
        entry_points={
          'pangadfs.pool': ['pool_pydfs = pydfs:PyDfsPool'],
          'pangadfs.populate': ['populate_pydfs = pydfs:PyDfsPopulate'],
        },
        zip_safe=False,
    )


if __name__ == '__main__':
    run()
