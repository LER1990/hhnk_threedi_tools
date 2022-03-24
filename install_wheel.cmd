python setup.py bdist_wheel 

python -m pip uninstall hhnk_research_tools -y
python -m pip install --upgrade dist/hhnk_research_tools-0.4-py3-none-any.whl
