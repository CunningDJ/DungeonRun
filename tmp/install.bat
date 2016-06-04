reg query "HKCU\SOFTWARE\Python"  
if ERRORLEVEL 1 GOTO NOPYTHON  
goto :HASPYTHON  

:NOPYTHON
echo No Python!
py-install\python-3.5.0-amd64.exe 

:HASPYTHON
echo Has Python!
pip install python-3.5.1

IF ERRORLEVEL 1 (
	echo This is where we'd install pip!
	)
IF ERRORLEVEL 0 (
	echo This is where we'd install requirements!
	py-install\python-3.5.0-amd64.exe
	
	)

