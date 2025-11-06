# Snowflake Deployment Guide

## Overview

This guide walks you through deploying HackTheTrack with Snowflake for cloud-based telemetry data storage, solving the issue of large CSV files (100MB+) not deploying to Vercel.

## Architecture

```
┌─────────────────┐
│ Frontend (React)│
│  on Vercel      │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────────┐  ┌──────────────────┐
│ Backend (FastAPI)│  │   Snowflake DB   │
│  on Vercel      │──│ Telemetry Data   │
└─────────────────┘  └──────────────────┘
```

## Prerequisites

- Snowflake account (free trial available at https://signup.snowflake.com/)
- Vercel account (already set up)
- Anthropic API key for AI coaching

## Step 1: Set Up Snowflake Database

### 1.1 Create Snowflake Account

If you don't have a Snowflake account:
1. Go to https://signup.snowflake.com/
2. Choose a cloud provider (AWS, Azure, or GCP)
3. Select a region (choose closest to your users)
4. Complete registration

### 1.2 Run Setup SQL Script

1. Log into Snowflake Web UI
2. Go to Worksheets
3. Open the file `snowflake_setup.sql` from this repository
4. Run the entire script to:
   - Create database `HACKTHETRACK`
   - Create schema `TELEMETRY`
   - Create table `telemetry_data`
   - Create staging area for CSV uploads

```sql
-- This script creates:
-- Database: HACKTHETRACK
-- Schema: TELEMETRY
-- Table: telemetry_data
-- Stage: telemetry_stage
```

## Step 2: Upload Telemetry Data to Snowflake

### Option A: Using Python Script (Recommended)

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` with your Snowflake credentials:**
   ```env
   SNOWFLAKE_ACCOUNT=xy12345.us-east-1
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_DATABASE=HACKTHETRACK
   SNOWFLAKE_SCHEMA=TELEMETRY
   ```

4. **Run the upload script:**
   ```bash
   cd ..  # Back to project root
   python upload_to_snowflake.py
   ```

   This will:
   - Connect to Snowflake
   - Upload all telemetry CSV files from `data/telemetry/`
   - Add metadata (track_id, race_num, data_source)
   - Verify the upload

### Option B: Manual Upload via SnowSQL

1. **Install SnowSQL:**
   ```bash
   # macOS
   brew install snowflake-snowsql

   # Or download from: https://docs.snowflake.com/en/user-guide/snowsql-install-config.html
   ```

2. **Upload files manually:**
   ```bash
   # Connect to Snowflake
   snowsql -a <account> -u <username>

   # Upload a file
   PUT file:///path/to/barber_r1_wide.csv @telemetry_stage;

   # Copy into table
   COPY INTO telemetry_data(...)
   FROM @telemetry_stage/barber_r1_wide.csv
   FILE_FORMAT = (...);
   ```

   See `snowflake_setup.sql` for complete COPY INTO commands.

## Step 3: Verify Data in Snowflake

Run these verification queries in Snowflake:

```sql
-- Check record counts per track/race
SELECT track_id, race_num, COUNT(*) as record_count
FROM telemetry_data
GROUP BY track_id, race_num
ORDER BY track_id, race_num;

-- Check distinct drivers per track
SELECT track_id, race_num, COUNT(DISTINCT vehicle_number) as driver_count
FROM telemetry_data
GROUP BY track_id, race_num;

-- View sample data
SELECT *
FROM telemetry_data
WHERE track_id = 'barber' AND race_num = 1
LIMIT 10;
```

Expected results:
- 12 track/race combinations (6 tracks × 2 races)
- ~35 unique drivers per track
- Millions of telemetry records total

## Step 4: Configure Vercel Environment Variables

1. **Go to Vercel Dashboard:**
   - Navigate to your project: https://vercel.com/
   - Click on Settings → Environment Variables

2. **Add the following variables:**

   | Variable Name | Value | Environment |
   |--------------|-------|-------------|
   | `ANTHROPIC_API_KEY` | `sk-ant-...` | Production, Preview, Development |
   | `USE_SNOWFLAKE` | `true` | Production, Preview |
   | `SNOWFLAKE_ACCOUNT` | `xy12345.us-east-1` | Production, Preview |
   | `SNOWFLAKE_USER` | `your_username` | Production, Preview |
   | `SNOWFLAKE_PASSWORD` | `your_password` | Production, Preview |
   | `SNOWFLAKE_WAREHOUSE` | `COMPUTE_WH` | Production, Preview |
   | `SNOWFLAKE_DATABASE` | `HACKTHETRACK` | Production, Preview |
   | `SNOWFLAKE_SCHEMA` | `TELEMETRY` | Production, Preview |
   | `SNOWFLAKE_ROLE` | `ACCOUNTADMIN` | Production, Preview |

   **Security Note:** These are sensitive credentials. Vercel encrypts environment variables.

## Step 5: Deploy to Vercel

### 5.1 Commit and Push Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add Snowflake integration for telemetry data storage

- Add snowflake-connector-python to requirements
- Create SnowflakeService for data access
- Update endpoints to query Snowflake when configured
- Add fallback to local CSV files for development
- Update DriverContext to filter drivers with telemetry
- Add comprehensive setup scripts and documentation"

# Push to GitHub (triggers Vercel deployment)
git push origin main
```

### 5.2 Monitor Deployment

1. Go to Vercel Dashboard
2. Watch the deployment progress
3. Check build logs for any errors

### 5.3 Verify Deployment

Once deployed, test these endpoints:

```bash
# Get drivers with telemetry
curl https://your-app.vercel.app/api/telemetry/drivers

# Expected response:
# {
#   "drivers_with_telemetry": [0, 2, 3, 5, 7, 8, 11, ...],
#   "count": 35,
#   "source": "snowflake"
# }
```

**Important:** The `"source": "snowflake"` confirms data is coming from Snowflake.

## Step 6: Test the Application

1. **Navigate to your Vercel URL:**
   ```
   https://your-app-name.vercel.app
   ```

2. **Verify driver list:**
   - Should see ~35 drivers in the dropdown
   - All drivers should have telemetry data

3. **Test telemetry coaching:**
   - Select a driver (e.g., #13)
   - Go to "Improve" tab
   - Select track and reference driver
   - Click "Analyze Telemetry"
   - Wait 10-15 seconds for AI coaching to generate
   - Verify coaching recommendations appear

## Architecture Benefits

### Before (Local CSV Files)
- ❌ 100MB+ CSV files don't deploy to Vercel
- ❌ Limited to 50MB serverless function size
- ❌ No data in production = broken app

### After (Snowflake)
- ✅ All telemetry data in cloud database
- ✅ Fast queries with Snowflake's columnar storage
- ✅ Scalable to millions of records
- ✅ Works perfectly with Vercel serverless functions
- ✅ Driver filtering works in production

## Cost Considerations

### Snowflake Free Trial
- $400 credit
- Lasts 30 days
- More than enough for this app

### Snowflake Production Costs
- **Compute:** ~$2/hour for XSMALL warehouse
- **Storage:** ~$23/TB/month (you'll use < 1GB = ~$0.02/month)
- **Auto-suspend:** Warehouse suspends after 60 seconds of inactivity

### Estimated Monthly Cost
With typical usage (100 users/day):
- **Compute:** ~$5-10/month (warehouse only runs during queries)
- **Storage:** < $1/month
- **Total:** ~$10-15/month

**Note:** Set AUTO_SUSPEND to 60 seconds to minimize costs.

## Troubleshooting

### Issue: "No drivers found" in production

**Cause:** Snowflake not configured or credentials incorrect

**Solution:**
1. Check Vercel environment variables are set correctly
2. Verify `USE_SNOWFLAKE=true` is set
3. Test Snowflake connection:
   ```bash
   curl https://your-app.vercel.app/api/telemetry/drivers
   ```
4. Check deployment logs for Snowflake connection errors

### Issue: "Failed to connect to Snowflake"

**Cause:** Invalid credentials or network issue

**Solution:**
1. Verify Snowflake credentials in Vercel dashboard
2. Check Snowflake account status (suspended?)
3. Test connection locally:
   ```bash
   python -c "from backend.app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
   ```

### Issue: Slow query performance

**Cause:** Warehouse suspended or query not optimized

**Solution:**
1. Increase warehouse size (XSMALL → SMALL)
2. Ensure AUTO_RESUME is TRUE
3. Check query patterns and add indexes if needed

### Issue: "Telemetry data not found"

**Cause:** Data not uploaded or wrong track/race name

**Solution:**
1. Run verification queries in Snowflake (see Step 3)
2. Check uploaded data:
   ```sql
   SELECT DISTINCT track_id, race_num FROM telemetry_data;
   ```
3. Re-run upload script if data missing

## Development vs Production

### Local Development (CSV Files)
```env
# .env (local)
USE_SNOWFLAKE=false
ANTHROPIC_API_KEY=sk-ant-...
```

### Production (Snowflake)
```env
# Vercel environment variables
USE_SNOWFLAKE=true
SNOWFLAKE_ACCOUNT=...
SNOWFLAKE_USER=...
SNOWFLAKE_PASSWORD=...
ANTHROPIC_API_KEY=sk-ant-...
```

The backend automatically falls back to local CSV files if Snowflake is not configured or fails.

## Monitoring and Maintenance

### Monitor Snowflake Usage
1. Go to Snowflake Web UI
2. Click "History" to see all queries
3. Check "Warehouses" to see compute usage
4. Review costs in "Account" → "Usage"

### Optimize Costs
- Set AUTO_SUSPEND to 60 seconds (already configured)
- Use XSMALL warehouse (already configured)
- Monitor query patterns and cache common queries

### Update Data
To add new telemetry data:
1. Add new CSV files to `data/telemetry/`
2. Run upload script again:
   ```bash
   python upload_to_snowflake.py
   ```
3. Data appends automatically (no duplicates)

## Next Steps

1. ✅ Complete Snowflake setup (Steps 1-2)
2. ✅ Configure Vercel environment variables (Step 4)
3. ✅ Deploy to Vercel (Step 5)
4. ✅ Test the application (Step 6)
5. Monitor usage and costs
6. Optimize performance as needed

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check Snowflake query history for errors
3. Test endpoints with curl to isolate frontend vs backend issues
4. Review this guide's troubleshooting section

## Summary

By integrating Snowflake, you've solved the "no data in production" problem and unlocked:
- ✅ Cloud-based telemetry storage
- ✅ Fast, scalable data access
- ✅ Production-ready deployment on Vercel
- ✅ Driver filtering working correctly
- ✅ Full telemetry coaching functionality

The application is now ready for production use with all 35 drivers and full telemetry data available!
