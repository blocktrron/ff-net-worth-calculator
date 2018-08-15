#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='ff-net-worth-calculator',
    version='0.1',
    description='Calculates the worth of your Freifunk network',
    url='https://github.com/blocktrron/ff-net-worth-calculator',
    author='blocktrron',
    author_email='mail@david-bauer.net',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests'],
    scripts=['bin/ff-net-worth-calc.py'],
    package_data={'ff_net_worth_calculator': ['data/*']},
    zip_safe=False,
)
