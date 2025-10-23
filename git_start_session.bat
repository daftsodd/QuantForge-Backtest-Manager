@echo off
echo ========================================
echo Starting Git Session
echo ========================================
echo.
echo Fetching latest changes from GitHub...
git fetch origin
echo.
echo Resetting local branch to match remote...
git reset --hard origin/main
echo.
echo Checking for untracked files (dry run)...
git clean -nd
echo.
echo Cleaning untracked files...
git clean -fd
echo.
echo ========================================
echo Session started! Your workspace is now
echo synced with the latest GitHub version.
echo ========================================
echo.
pause

