from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all submodules of pandasai
hiddenimports = collect_submodules('pandasai')

# Collect data files
datas = collect_data_files('pandasai') 