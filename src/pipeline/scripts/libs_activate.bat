set CONDALIBS=%CONDA_PREFIX%\..\py27libs\Lib
IF DEFINED PYTHONPATH (
	set PYTHONPATH=%PYTHONPATH%:%CONDALIBS%\site-packages
) ELSE (
	set PYTHONPATH=%CONDALIBS%\site-packages
)
