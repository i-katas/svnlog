from setuptools import setup

setup(
    package_dir={'': 'src'},
    packages=[''],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require=dict(
        dev=['flake8']
    )
)
