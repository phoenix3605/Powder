c:\
cd C:\New folder\vsc\python\Powder
start cmd /k "pip install -U pyinstaller"
start cmd /k "pyinstaller main.py --onefile --hidden-import=skimage._shared.geometry --hidden-import=skimage.draw._draw"