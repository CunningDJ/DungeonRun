reg query "hkcu\software\Python35"
if ERRORLEVEL 1 GOTO NOPYTHON

goto :HASPYTHON

:NOPYTHON
setx PYTHONPATH "%PYTHONPATH%;%cd%\py-install\Python-3.5.0"

python py-install\Python-3.5.0\setup.py install

goto :HASPYTHON

:HASPYTHON
pip install sdl2
