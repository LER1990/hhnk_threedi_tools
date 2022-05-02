from setuptools import setup, find_packages

import codecs
import re
import os

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    """
    Search the file for a version string.
    file_path contain string path components.
    Reads the supplied Python module as text without importing it.
    """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="hhnk_research_tools",
    version=find_version("hhnk_research_tools", "__init__.py"),
    description='HHNK tools for working with 3di',
    url='https://github.com/HHNK/hhnk-research-tools',
    author='Wietse van Gerwen',
    author_email='w.vangerwen@hhnk.nl',
    project_urls={
        "Bug Tracker": "https://github.com/HHNK/hhnk-research-tools/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.17.0",  # Was 1.19.1
        "Shapely>=1.6.4",  # Was 1.7.0
        "gdal>=2.4.0",  # Was 3.1.4
        "pandas>=0.25.3",  # Was 1.0.1
        "geopandas>=0.6.0",  # Was 0.7.0
        "threedigrid>=1.0.16",  # Was 1.0.25
        "xarray",
    ],
)
