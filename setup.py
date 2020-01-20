#!/usr/bin/env python
from setuptools import setup, find_packages
from distutils.core import Extension
import os

version_path = os.path.join('mpl_toolkits', 'clifford', '_version.py')
exec(open(version_path).read())

LONG_DESCRIPTION = """
A package to provide tools for plotting 2D and 3D GA in ``matplotlib``.

Often a
"""

setup(
    name='mpl_toolkits.clifford',
    version=__version__,
    license='MIT',
    description='Matplotlib tools for clifford',
    long_description=LONG_DESCRIPTION,
    author='Eric Wieser',
    py_modules=['mpl_toolkits.clifford'],
    namespace_packages=['mpl_toolkits'],
    install_requires=[
        'clifford',
        'matplotlib',
        'trimesh',
    ],
    package_dir={'mpl_toolkits': 'mpl_toolkits'},

    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',

        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    project_urls={
        "Bug Tracker": "https://github.com/pygae/mpl_toolkits.clifford/issues",
        "Source Code": "https://github.com/pygae/mpl_toolkits.clifford",
    },

    python_requires='>=3.5',
)
