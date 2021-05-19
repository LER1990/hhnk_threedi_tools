from setuptools import setup, find_packages

setup(
    name='hhnk_research_tools',
    version='0.1.0',
    description='HHNK tools for working with 3di',
    url='https://github.com/HHNK/hhnk_research_tools_py',
    author='Wietse van Gerwen',
    author_email='w.vangerwen@hhnk.nl',
    project_urls={
        "Bug Tracker": "https://github.com/HHNK/hhnk_research_tools_py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
	install_requires=[
   	'numpy>=1.17.0', # Was 1.19.1
	'Shapely>=1.6.4', # Was 1.7.0
	'gdal>=2.4.0', # Was 3.1.4
    'pandas>=0.25.3', # Was 1.0.1
    'geopandas>=0.6.0', # Was 0.7.0
    'threedigrid>=1.0.16' # Was 1.0.25
	]
)
