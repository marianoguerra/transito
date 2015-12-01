#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'transit-python==0.8.250',
    'requests==2.8.1',
    'rply==0.7.4'
]

test_requirements = [
]

setup(
    name='transito',
    version='0.1.3',
    description="Command Line Tool to Work with Transit Format",
    long_description=readme + '\n\n' + history,
    author="Mariano Guerra",
    author_email='luismarianoguerra@gmail.com',
    url='https://github.com/marianoguerra/transito',
    packages=[
        'transito',
    ],
    package_dir={'transito':
                 'transito'},
    entry_points={
        'console_scripts': [
            'transito = transito.__init__:main',
            ]},

    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='transito',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
