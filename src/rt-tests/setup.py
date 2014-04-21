from setuptools import setup, find_packages

setup(
    name="rt-tests",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        'Django',
        'tornado',
    ],
    entry_points={
        'console_scripts': [
            'rttests=rttests:main'
        ]
    }
)
