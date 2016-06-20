# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


requires = [
    'six',
    'docopt',
    'requests',
    'AppDirs',
    'python-dateutil',
    'sphinx_rtd_theme',
]


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content


setup(
    name='pyimeji',
    version="1.2.2",
    description='A python wrapper for the imeji API',
    long_description=read("README.rst"),
    author='Robert Forkel & Max Planck Digital Library (MPDL)',
    author_email='support@imeji.org',
    url='https://github.com/imeji-community/pyimeji',
    install_requires=requires,
    license=read("LICENSE"),
    zip_safe=False,
    keywords='imeji',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            "imeji = pyimeji.cli:main"
        ]
    },
    tests_require=['tox', 'nose', 'coverage', 'httmock'],
)
