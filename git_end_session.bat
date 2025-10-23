@echo off
echo ========================================
echo Ending Git Session
echo ========================================
echo.
set /p commit_msg="Enter commit message: "
echo.
echo Staging all changes...
git add -A
echo.
echo Committing changes...
git commit -m "%commit_msg%"
if errorlevel 1 (
    echo.
    echo No changes to commit.
    pause
    exit /b 0
)
echo.
echo Fetching latest remote state...
git fetch origin
echo.
echo Pushing changes to GitHub...
git push --force-with-lease origin HEAD:main
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Push failed!
    echo ========================================
    echo.
    echo Remote may have changed. Check with:
    echo   git log HEAD..origin/main
    echo.
    echo To force push anyway:
    echo   git push --force origin main
    echo.
    pause
    exit /b 1
)
echo.
echo ========================================
echo Session ended! Changes pushed to GitHub.
echo ========================================
echo.
pause

