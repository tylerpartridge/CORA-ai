# 📦 Data Segregation Plan - Keep the System, Move the Storage

## The Problem
Your AI learning/session system is good! But the data is stored inside the project, causing:
- 26,712 files cluttering your workspace
- Health checks failing
- Git performance issues
- Cognitive overload

## The Solution: Segregate the Data

### Option 1: Move to User Home Directory (Recommended)
```bash
# Windows
C:\Users\[YourName]\.cora-data\
    sessions\
    archives\
    patterns\
    
# Linux/WSL  
~/.cora-data/
```

### Option 2: Separate Data Drive
```bash
# Windows
D:\CORA-DATA\

# Linux
/data/cora/
```

### Option 3: Cloud Storage (Advanced)
- S3 bucket for archives
- Local cache for recent sessions
- Async upload/download

## Implementation Steps

1. **Create external data directory**
```bash
# Windows
mkdir C:\Users\%USERNAME%\.cora-data

# Linux/WSL
mkdir ~/.cora-data
```

2. **Move existing data**
```bash
# Move, don't copy - reclaim the space
mv .mind/* ~/.cora-data/
mv .ai/* ~/.cora-data/
mv .archive/* ~/.cora-data/
```

3. **Update your tools to use new location**
- Change paths in session tracking
- Update archive system paths  
- Modify pattern learning storage

4. **Keep minimal symlinks in project**
```bash
# Just enough for tools to find the data
ln -s ~/.cora-data/current-session .mind/today
```

## Benefits

1. **Project stays clean** - Only code in the repo
2. **Data grows freely** - No impact on project health
3. **Git stays fast** - Not tracking thousands of files
4. **Backups separate** - Different backup strategy for data vs code
5. **Easy cleanup** - Delete data without touching code

## This Fixes Everything

- ✅ Health checks pass (no data files to scan)
- ✅ Git performs well (only tracking code)
- ✅ You keep your AI learning system
- ✅ Data is preserved but segregated
- ✅ Easy to archive/purge old data

## The Key Insight

**Your system design is good.** The session tracking, pattern learning, and archiving are valuable. You just need to store the data OUTSIDE the project directory.

Think of it like a database - you wouldn't put PostgreSQL's data files in your git repo. Same principle here.