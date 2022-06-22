# Save sascfg_personal.py to your SASPy installation location.
# Run the following commands in your Python command window to get the full pathname of where to save your sascfg_personal.py file.

# import saspy, os
# print(saspy.__file__.replace('__init__.py', 'sascfg_personal.py'))
# Ex: c:\Users\jhs\AppData\Local\pypoetry\Cache\virtualenvs\datadoc-lLkivG_q-py3.9\lib\site-packages\saspy\sascfg_personal.py

# win: where java
# mac: which java or $(dirname $(readlink $(which javac)))/java_home


SAS_config_names = ['oda']
oda = {
    'java': 'C:\\Program Files (x86)\\Common Files\\Oracle\\Java\\javapath\\java.exe',
    # US Home Region 1
    # 'iomhost' : ['odaws01-usw2.oda.sas.com','odaws02-usw2.oda.sas.com','odaws03-usw2.oda.sas.com','odaws04-usw2.oda.sas.com'],
    # US Home Region 2
    # 'iomhost' : ['odaws01-usw2-2.oda.sas.com','odaws02-usw2-2.oda.sas.com'],
    # European Home Region 1
    'iomhost': ['odaws01-euw1.oda.sas.com', 'odaws02-euw1.oda.sas.com'],
    # Asia Pacific Home Region 1
    # 'iomhost' : ['odaws01-apse1.oda.sas.com','odaws02-apse1.oda.sas.com'],
    # Asia Pacific Home Region 2
    # 'iomhost' : ['odaws01-apse1-2.oda.sas.com','odaws02-apse1-2.oda.sas.com'],
    'iomport': 8591,
    'authkey': 'oda',
    'encoding': 'utf-8'
}
