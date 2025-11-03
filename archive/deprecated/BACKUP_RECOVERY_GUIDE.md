# Backup & Recovery Guide

**Backup Created:** 2025-11-02 15:21:52
**Original Size:** 2.7GB
**Backup Size:** 2.6GB ✅

---

## BACKUP LOCATIONS

### 1. Full Directory Backup (PRIMARY)
```
Location: /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152
Type: Complete copy of entire repository
Size: 2.6GB
Includes: All files, data, git history
```

### 2. Git Branch Backup (SECONDARY)
```
Branch: backup-before-reorganization
Type: Git branch snapshot
Status: Created successfully
```

---

## RECOVERY OPTIONS

### Option 1: Full Rollback (Nuclear Option)
If everything breaks, restore entire directory:

```bash
# Navigate to parent directory
cd /Users/justingrosz/Documents/AI-Work

# Remove broken repository
rm -rf hackthetrack-master

# Restore from backup
cp -R hackthetrack-master-backup-20251102_152152 hackthetrack-master

# Navigate back
cd hackthetrack-master

echo "✅ Full repository restored!"
```

**Recovery Time:** ~5 minutes (copying 2.6GB)
**Data Loss:** None (complete restore)

---

### Option 2: Git Reset (Surgical Rollback)
If only code changes broke (not file moves):

```bash
# Check current branch
git branch

# Reset to backup branch
git checkout backup-before-reorganization

# Or reset current branch to backup point
git reset --hard backup-before-reorganization

echo "✅ Git state restored!"
```

**Recovery Time:** Instant
**Data Loss:** Only uncommitted changes

---

### Option 3: Selective File Restore
If only specific files need restoration:

```bash
# Restore specific file
cp /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152/path/to/file.py ./path/to/file.py

# Restore entire directory
cp -R /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152/backend ./

# Restore frontend
cp -R /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152/frontend ./

echo "✅ Selective files restored!"
```

**Recovery Time:** Seconds to minutes
**Data Loss:** None for restored files

---

## VERIFICATION CHECKLIST

Before declaring recovery successful, verify:

### Backend Verification
```bash
cd backend
source venv/bin/activate  # If venv exists
python main.py

# Should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Frontend Verification
```bash
cd frontend
npm run dev

# Should see:
# VITE v5.x.x ready in X ms
# ➜ Local: http://localhost:5173/
```

### Data Verification
```bash
ls -lh data/telemetry/
ls -lh data/lap_timing/
ls -lh data/race_results/

# Should see all CSV files intact
```

### Database Verification
```bash
ls -lh backend/circuit-fit.db
# Should show ~340MB file

sqlite3 backend/circuit-fit.db "SELECT name FROM sqlite_master WHERE type='table';"
# Should list database tables
```

---

## SAFETY PROTOCOLS

### Before Any Major Change:

1. ✅ **Verify backup exists**
   ```bash
   ls -lh /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152
   ```

2. ✅ **Verify backup integrity**
   ```bash
   du -sh hackthetrack-master
   du -sh /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152
   # Should be similar sizes
   ```

3. ✅ **Verify git branch backup**
   ```bash
   git branch | grep backup-before-reorganization
   ```

4. ✅ **Test application works BEFORE changes**
   - Start backend server
   - Start frontend dev server
   - Verify both run without errors

---

## EMERGENCY RECOVERY SCRIPT

Save this as `emergency_restore.sh`:

```bash
#!/bin/bash

echo "🚨 EMERGENCY RECOVERY INITIATED"
echo "================================"

# Confirm
read -p "This will COMPLETELY RESTORE from backup. Continue? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 1
fi

# Navigate to parent
cd /Users/justingrosz/Documents/AI-Work

# Backup current broken state (just in case)
echo "📦 Backing up current state..."
mv hackthetrack-master hackthetrack-master-broken-$(date +%Y%m%d_%H%M%S)

# Restore from backup
echo "♻️  Restoring from backup..."
cp -R hackthetrack-master-backup-20251102_152152 hackthetrack-master

# Navigate back
cd hackthetrack-master

echo "✅ RECOVERY COMPLETE!"
echo "===================="
echo "Repository restored to backup state."
echo ""
echo "Next steps:"
echo "1. cd backend && source venv/bin/activate && python main.py"
echo "2. cd frontend && npm run dev"
```

**To use:**
```bash
chmod +x emergency_restore.sh
./emergency_restore.sh
```

---

## BACKUP RETENTION

### Keep Backup Until:
- ✅ All reorganization completed
- ✅ Backend API tested and working
- ✅ Frontend tested and working
- ✅ All import paths verified
- ✅ Application deployed successfully
- ✅ At least 7 days of stable operation

### Minimum Retention: 30 days

### When to Delete Backup:
```bash
# Only after confirming everything works for 30+ days
rm -rf /Users/justingrosz/Documents/AI-Work/hackthetrack-master-backup-20251102_152152

# Also can delete git branch
git branch -D backup-before-reorganization
```

---

## CONTACT & TROUBLESHOOTING

### If Recovery Fails:
1. Check backup directory still exists
2. Check disk space: `df -h`
3. Check file permissions: `ls -la`
4. Try Option 1 (full rollback) first
5. If all else fails, restore from backup-20251102_152152

### Testing After Recovery:
```bash
# Quick test script
cd backend
python -c "import app; print('Backend imports OK')"

cd frontend
npm run build
# Should complete without errors

echo "✅ Recovery verified!"
```

---

## REORGANIZATION PHASES

This backup covers the state BEFORE these changes:

### Phase 1: Backend Reorganization
- Move models to backend/models/
- Update import statements

### Phase 2: Frontend Reorganization
- Move configs to frontend/config/
- Reorganize components into folders
- Move pages into individual folders

### Phase 3: Data & Assets Reorganization
- Rename data/Telemetry → data/telemetry
- Move track_maps to assets/

### Phase 4: Scripts Reorganization
- Organize scripts by purpose
- Create categorical subfolders

### Phase 5: Documentation Reorganization
- Move docs to docs/ folder structure
- Archive old documentation

**If any phase fails, STOP and rollback immediately!**

---

## STATUS LOG

| Phase | Status | Date | Notes |
|-------|--------|------|-------|
| Backup Creation | ✅ COMPLETE | 2025-11-02 15:21 | 2.6GB backup created |
| Git Branch Backup | ✅ COMPLETE | 2025-11-02 15:22 | Branch: backup-before-reorganization |
| Phase 1: Backend | ⏳ PENDING | - | - |
| Phase 2: Frontend | ⏳ PENDING | - | - |
| Phase 3: Data/Assets | ⏳ PENDING | - | - |
| Phase 4: Scripts | ⏳ PENDING | - | - |
| Phase 5: Documentation | ⏳ PENDING | - | - |
| Testing | ⏳ PENDING | - | - |
| Verification | ⏳ PENDING | - | - |

---

## REMEMBER

🛑 **STOP immediately if anything breaks**
🔄 **Test after EACH phase**
💾 **This backup is your safety net**
✅ **Don't delete backup until 30+ days of stability**

---

**Backup verified and ready for reorganization!**
