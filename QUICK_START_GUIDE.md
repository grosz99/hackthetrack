# QUICK START GUIDE - 10 Day Sprint

## Today (Day 1): Get Oriented

### What You Need to Do RIGHT NOW

1. **Read the Full Plan**: Open `10_DAY_EXECUTION_PLAN.md`

2. **Verify Your Data**:
   ```bash
   # Check Snowflake has data
   # Run this query in Snowflake console:
   SELECT TRACK_ID, RACE_NUM, COUNT(*) as rows
   FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
   GROUP BY TRACK_ID, RACE_NUM
   ORDER BY TRACK_ID, RACE_NUM;
   ```

3. **Start Day 1 Tasks** (in order):
   - Task 1.1: Data Pipeline Audit (2 hours)
   - Task 1.2: Backend Service Review (2 hours)
   - Task 1.3: UX Design Analysis (2 hours)
   - Task 1.4: Integration Testing Strategy (2 hours)

## Key Decisions Already Made

✅ **Data Strategy**: Snowflake single source of truth (Option A from TELEMETRY_ARCHITECTURE_PLAN.md)
✅ **Memory Safety**: Always use WHERE clause filtering (load 2K rows not 15.7M)
✅ **UX Direction**: Rankings table + gamification (see design/New_Design/)
✅ **Deployment**: Heroku backend + Vercel frontend (already set up)

## Critical Path (Can't Slip)

**Days 1-3**: Data pipeline migration (Snowflake)
**Days 4-6**: UX transformation (rankings + gamification)
**Days 7-8**: Integration + polish
**Days 9-10**: Testing + deployment

## Daily Rhythm

- **9:00 AM**: Daily standup (15 min)
- **Work**: Focus on day's tasks (8 hours)
- **End of Day**: Update checklist, prepare for tomorrow

## Emergency Contacts

If blocked > 2 hours:
1. Check `10_DAY_EXECUTION_PLAN.md` Risk Mitigation section
2. Post in team chat
3. Escalate to project lead

## Success Criteria (Day 10)

- [ ] Ranking table works with real data
- [ ] Telemetry compare endpoint doesn't crash (< 512MB memory)
- [ ] All 5 tracks return data (barber, cota, roadamerica, sonoma, vir)
- [ ] Production deployed and stable
- [ ] No 500 errors

## First 3 Commands to Run

```bash
# 1. Check current backend works
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/health

# 2. Check Snowflake connection
# (Run in Snowflake console)
SELECT CURRENT_VERSION();

# 3. Start backend locally for testing
cd backend && python main.py
```

## Files You'll Touch Most

**Backend** (Days 1-3):
- `backend/app/services/snowflake_service.py`
- `backend/app/api/routes.py`
- `backend/app/services/data_loader.py`

**Frontend** (Days 4-6):
- `frontend/src/pages/ScoutLanding/ScoutLanding.jsx`
- `frontend/src/components/RankingTable/` (new)
- `frontend/src/pages/DriverDetail/` (new)

## When Things Go Wrong

**Memory crash on Heroku**:
→ Check query has WHERE clause filtering
→ Verify returning < 5,000 rows
→ See Risk Mitigation in main plan

**404 on telemetry endpoint**:
→ Check track exists in Snowflake
→ Verify TRACK_ID spelling (lowercase)
→ Check VEHICLE_NUMBER exists for both drivers

**UX doesn't match design**:
→ Reference design/New_Design/ screenshots
→ Check CSS variables in design-system.css
→ Use existing Card component pattern

## Daily Checklist Format

At end of each day, update:
```
✅ Day 1 Complete - 4/4 tasks done
⚠️  Day 2 In Progress - 2/4 tasks done
❌ Day 3 Blocked - waiting on Snowflake index
```

## LET'S GO! 🚀

Start with Day 1, Task 1.1 in the main plan.
Read it completely before beginning.
Track your time - strict timeboxes!

Good luck! You've got this. 💪
