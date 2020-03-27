import os
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = r'C:\Users\Sutalite\AppData\Local\Programs\Python\Python38-32\tcl'
os.environ['TK_LIBRARY'] = r'C:\Users\Sutalite\AppData\Local\Programs\Python\Python38-32\tcl\tk8.6'

buildOptions = dict(
    packages = [],
    excludes = [],
    include_files=[r'C:\Users\Sutalite\AppData\Local\Programs\Python\Python38-32\DLLs\tcl86t.dll', r'C:\Users\Sutalite\AppData\Local\Programs\Python\Python38-32\DLLs\tk86t.dll']
)


setup (
        name = "jeu",
        version = "0.1",
        description = "casse pas la tete",
        options = dict(build_exe = buildOptions),
        executables = [Executable("main.py"), Executable('editor.py')],
)
