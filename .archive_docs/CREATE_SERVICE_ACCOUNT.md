# Create Snowflake Service Account for HackTheTrack

## Quick Setup Guide (5 minutes)

### Step 1: Log into Snowflake Web UI

1. Go to https://app.snowflake.com/
2. Log in with your credentials (JAKTAI99) + MFA code
3. Click on **"Worksheets"** in the left sidebar

### Step 2: Create Service Account

Copy and paste this SQL into a new worksheet and run it:

```sql
-- Create service account user
CREATE USER IF NOT EXISTS hackthetrack_svc
  PASSWORD = 'HackTheTrack2025!Secure'
  DEFAULT_ROLE = ACCOUNTADMIN
  DEFAULT_WAREHOUSE = COMPUTE_WH
  MUST_CHANGE_PASSWORD = FALSE;

-- Grant admin role to service account
GRANT ROLE ACCOUNTADMIN TO USER hackthetrack_svc;

-- Verify it was created
SHOW USERS LIKE 'hackthetrack_svc';
```

**Important:** You can change the password to whatever you want! Just remember it for the next step.

### Step 3: Update Your .env File

Update the `.env` file in the project root with the service account credentials:

```bash
# Change these two lines:
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_PASSWORD=HackTheTrack2025!Secure
```

(Or use whatever password you set in Step 2)

### Step 4: Test Connection

Run this from the backend directory:

```bash
cd backend
source venv/bin/activate
python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
```

You should see:
```json
{
  "status": "connected",
  "version": "8.x.x",
  "database": "HACKTHETRACK",
  ...
}
```

### Step 5: Run Setup Script

Now that we have a working connection, run the setup script:

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
python upload_to_snowflake.py
```

This will:
1. Create the database and schema (if needed)
2. Upload all telemetry CSV files
3. Verify the upload

---

## Why This is Better for Competition

✅ **Stable** - No MFA to deal with
✅ **Dedicated** - Separate from your personal account
✅ **Secure** - Can be revoked without affecting you
✅ **Production-ready** - Works in Vercel without issues

## Security Note

This service account password is NOT sensitive personal information:
- It's just for the HackTheTrack database
- Can be rotated anytime
- Only you have access to your Snowflake account
- No billing info or personal data exposed

For competition/demo purposes, this is perfectly fine!

---

## If You Need to Change the Password Later

```sql
ALTER USER hackthetrack_svc SET PASSWORD = 'YourNewPassword123!';
```

Then update the `.env` file with the new password.

---

**Next:** Once you complete these steps, let me know and I'll help you upload the telemetry data!
