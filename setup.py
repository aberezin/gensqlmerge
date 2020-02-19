#! /usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gensqlmerge",
    version="0.1",
    packages=find_packages(),

   package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
        # And include any *.msg files found in the "hello" package, too:
        "hello": ["*.msg"],
    },

    entry_points={
    'console_scripts': [
        'gensqlmerge=gensqlmerge.gen:main',
      ]},
    # metadata to display on PyPI
    author="Alan Berezin",
    author_email="alan.berezin1@gmail.com",
    description="Writes the sql for a sqlserver merge statement.",
    long_description=long_description,
    long_description_content_type="text/markdown",    keywords="SQL Generator SqlServer merge",
    url="",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Source Code": "https://code.example.com/HelloWorld/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
        "License :: OSI Approved :: MIT License",
    ]

)

