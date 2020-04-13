from setuptools import setup

setup(
    packages=['svnlog'],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    extras_require=dict(
        dev=['flake8', 'pytest-cov']
    )
)
