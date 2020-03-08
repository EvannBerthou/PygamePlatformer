from cx_Freeze import setup, Executable

setup (
        name = "jeu",
        version = "0.1",
        description = "casse pas la tete",
        executables = [Executable("main.py")],
)
