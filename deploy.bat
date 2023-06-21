python setup.py bdist_wheel 
pip uninstall hhnk_research_tools -y
python -m pip install --target %appdata%\3Di\QGIS3\profiles\default\python\plugins\hhnk_threedi_plugin\external-dependencies --upgrade dist\hhnk_research_tools-2023.3-py3-none-any.whl
