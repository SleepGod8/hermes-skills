@echo off
echo ================================================
echo  %1
echo ================================================
echo.
echo Installing to %2 ... please wait.
echo Do NOT close this window.
echo.
"%~dp0%~3" install --quiet --accept-license --installation-dir="%2"
echo.
echo -------------------------------------------------
echo  Install command finished.
echo  If no error message above, installation is DONE.
echo -------------------------------------------------
echo.
pause
