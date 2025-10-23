# Git Setup Guide

## Initial Setup (First Time Only)

### 1. Initialize Git Repository

```bash
git init
```

### 2. Configure Git (if not done globally)

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### 3. Create GitHub Repository

1. Go to GitHub.com
2. Click "New Repository"
3. Name it (e.g., "quantforge-backtest-manager")
4. **DO NOT** initialize with README, .gitignore, or license
5. Copy the repository URL

### 4. Link to GitHub

```bash
git remote add origin https://github.com/yourusername/your-repo-name.git
```

Or with SSH:
```bash
git remote add origin git@github.com:yourusername/your-repo-name.git
```

### 5. Initial Commit

```bash
git add -A
git commit -m "Initial commit: QuantForge Backtest Manager"
git branch -M main
git push -u origin main
```

---

## Your Workflow

### Start Session (Pull Latest Changes)

```bash
git fetch origin
git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
git clean -nd
git clean -fd
```

**What this does:**
- `git fetch origin` - Download latest changes from GitHub
- `git reset --hard origin/...` - Reset local branch to match remote
- `git clean -nd` - Preview untracked files to delete (dry run)
- `git clean -fd` - Delete untracked files and directories

### End Session (Push Changes)

```bash
git add -A
git commit -m "Your commit message"
git fetch origin
git push --force-with-lease origin HEAD:main
```

**What this does:**
- `git add -A` - Stage all changes
- `git commit -m "..."` - Commit with message
- `git fetch origin` - Get latest remote state
- `git push --force-with-lease` - Safe force push (fails if remote changed)

---

## Commit Message Examples

```bash
git commit -m "Add progress tracking improvements"
git commit -m "Fix PyQt6 import error"
git commit -m "Update README with troubleshooting"
git commit -m "Implement total progress bar with ETA"
```

---

## Useful Commands

### Check Status
```bash
git status
```

### View Changes
```bash
git diff
```

### View Commit History
```bash
git log --oneline
```

### Undo Last Commit (Keep Changes)
```bash
git reset --soft HEAD~1
```

### Discard All Local Changes
```bash
git reset --hard HEAD
git clean -fd
```

### View Remote URL
```bash
git remote -v
```

### Change Remote URL
```bash
git remote set-url origin https://github.com/newuser/newrepo.git
```

---

## Branch Management (Optional)

### Create and Switch to New Branch
```bash
git checkout -b feature-name
```

### Switch Back to Main
```bash
git checkout main
```

### Merge Branch into Main
```bash
git checkout main
git merge feature-name
```

---

## What's Ignored

The `.gitignore` file excludes:
- Python cache (`__pycache__/`)
- Config files (`config.json`)
- Execution logs (`*_execution.json`)
- Output files (`.xlsx`, `.png`, etc.)
- IDE settings
- OS files

These files stay local and won't be pushed to GitHub.

---

## Safety Notes

- `--force-with-lease` is safer than `--force` - it checks if remote changed
- Always `git fetch` before force pushing
- Your workflow ensures clean syncs between sessions
- Consider creating a backup branch before major changes:
  ```bash
  git branch backup-$(date +%Y%m%d)
  ```

---

## Troubleshooting

### If Push is Rejected

```bash
# Check what changed remotely
git fetch origin
git log HEAD..origin/main

# If you want to keep remote changes
git pull --rebase origin main

# If you want to overwrite remote (careful!)
git push --force origin main
```

### If You Want to Start Fresh

```bash
# Keep your files but reset git history
rm -rf .git
git init
git add -A
git commit -m "Fresh start"
git remote add origin <your-repo-url>
git push -u --force origin main
```

---

## Quick Reference Card

```bash
# START SESSION
git fetch origin && git reset --hard origin/main && git clean -fd

# END SESSION  
git add -A && git commit -m "Update" && git fetch origin && git push --force-with-lease origin HEAD:main

# CHECK STATUS
git status

# VIEW LOG
git log --oneline -10
```

