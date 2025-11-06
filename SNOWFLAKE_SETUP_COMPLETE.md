# Snowflake Setup - Complete! ✅

## Summary

Successfully configured Snowflake integration with RSA key-pair authentication, bypassing MFA requirements.

## What Was Done

### 1. RSA Key-Pair Authentication
- Generated `rsa_key.p8` (private key) and `rsa_key.pub` (public key)
- Assigned public key to `hackthetrack_svc` service account
- Updated `snowflake_service.py` to support both key-pair and password auth
- Keys added to `.gitignore` for security

### 2. Database Schema
Database: `HACKTHETRACK`
Schema: `TELEMETRY`
Table: `telemetry_data` with columns:
- track_id, race_num, vehicle_number, lap
- sample_time, distance, speed, rpm, gear
- throttle, brake, steering
- lateral_g, longitudinal_g
- gps_lat, gps_long, gps_alt
- created_at timestamp

### 3. Data Upload Script
Located at: `backend/scripts/upload_telemetry_to_snowflake.py`

**Features:**
- Reads all `*_r[12]_wide.csv` files from `data/telemetry/`
- Maps CSV columns to Snowflake schema
- Handles NaN values (converts to NULL)
- Batch uploads with progress tracking
- Provides upload verification summary

## Files Modified/Created

### Modified:
- `backend/app/services/snowflake_service.py` - Added key-pair auth support
- `backend/.env` - Added `SNOWFLAKE_PRIVATE_KEY_PATH`
- `.gitignore` - Added RSA keys

### Created:
- `rsa_key.p8` - Private key (⚠️ DO NOT COMMIT)
- `rsa_key.pub` - Public key
- `backend/scripts/snowflake_setup.sql` - Database schema SQL
- `backend/scripts/setup_snowflake_schema.py` - Python setup script
- `backend/scripts/upload_telemetry_to_snowflake.py` - Data upload script

## How to Upload Telemetry Data

```bash
cd backend
source venv/bin/activate
python scripts/upload_telemetry_to_snowflake.py
```

**Note:** Upload will take ~15-30 minutes for all 10 files (~12M rows total)

## Verifying Connection

```bash
cd backend
source venv/bin/activate
python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
```

Expected output:
```
{'status': 'connected', 'version': '9.34.0', 'database': None, 'warehouse': 'COMPUTE_WH', 'schema': 'TELEMETRY'}
```

## For Vercel Deployment

When deploying to Vercel, you'll need to add the private key as an environment variable:

**Option 1: Base64 encode the key**
```bash
base64 rsa_key.p8 | tr -d '\n' > rsa_key_base64.txt
```

Then in Vercel:
```
SNOWFLAKE_PRIVATE_KEY_BASE64=<contents of rsa_key_base64.txt>
```

Update `snowflake_service.py` to decode from base64 if the env var is set.

**Option 2: Multi-line secret**
Copy the entire contents of `rsa_key.p8` and paste into Vercel environment variables.

## Security Notes

- ✅ RSA keys are in `.gitignore` - they will NOT be committed
- ✅ Key-pair auth is more secure than passwords
- ✅ No MFA prompt required for automated deployments
- ⚠️ Keep `rsa_key.p8` secret - it provides full database access
- ⚠️ For production, consider using Snowflake's secret management

## Testing the Integration

1. **Check connection:**
   ```bash
   python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
   ```

2. **Test query:**
   ```bash
   python -c "
   from app.services.snowflake_service import snowflake_service
   drivers = snowflake_service.get_drivers_with_telemetry()
   print(f'Drivers with data: {drivers}')
   "
   ```

3. **Test telemetry fetch:**
   ```bash
   python -c "
   from app.services.snowflake_service import snowflake_service
   df = snowflake_service.get_telemetry_data('barber', 1, 13)
   print(f'Rows for driver 13: {len(df)}')
   "
   ```

## Next Steps

1. ✅ **Run data upload** (when ready - takes 15-30 min)
2. ⏳ Update API endpoints to use Snowflake instead of CSV files
3. ⏳ Deploy to Vercel with Snowflake credentials
4. ⏳ Test production deployment

## Support

If you encounter issues:
- Check Snowflake connection: `python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"`
- Verify key permissions: Ensure `rsa_key.p8` has correct permissions (should be readable)
- Check Snowflake UI: Verify database/schema/table exist
