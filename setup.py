#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README", 'r') as f:
    long_description = f.read()

setup(name='orbits',
      version='1.0',
      description='Allows the user to animate the trajectories of objects in space',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/Anthony-Giacinto/orbits',
      author='Anthony Giacinto',
      author_email='anthonygiacinto1@gmail.com',
      packages=find_packages())
