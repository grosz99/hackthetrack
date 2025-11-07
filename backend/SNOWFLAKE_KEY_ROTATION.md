# Snowflake RSA Key Rotation Policy

## Overview
This document outlines the RSA keypair rotation schedule and procedures for the HackTheTrack Snowflake integration on Heroku.

## Current Key Information
- **Generation Date**: November 6, 2025
- **Key Type**: RSA 2048-bit
- **Algorithm**: PKCS#8 format
- **Authentication Method**: Keypair (MFA-compatible)
- **User**: `hackthetrack_svc`
- **Deployment**: Heroku environment variable (`SNOWFLAKE_PRIVATE_KEY_BASE64`)

## Rotation Schedule
**Key rotation is required every 90 days** to maintain security best practices.

### Next Rotation Due: **February 4, 2026**

## Rotation Procedure

### 1. Generate New Keypair

```bash
# Generate new private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key_new.p8 -nocrypt

# Extract public key
openssl rsa -in rsa_key_new.p8 -pubout -out rsa_key_new.pub

# Set secure permissions
chmod 600 rsa_key_new.p8
chmod 644 rsa_key_new.pub
```

### 2. Register Public Key in Snowflake

```bash
# Extract public key content (remove headers/footers)
tail -n +2 rsa_key_new.pub | head -n -1 | tr -d '\n'

# In Snowflake, run:
ALTER USER hackthetrack_svc SET RSA_PUBLIC_KEY='<paste_key_here>';

# Verify key was set:
DESC USER hackthetrack_svc;
```

### 3. Convert Private Key to Base64

```bash
# Convert to base64
base64 -i rsa_key_new.p8 -o rsa_key_base64_new.txt

# Copy to clipboard (macOS):
pbcopy < rsa_key_base64_new.txt
```

### 4. Update Heroku Environment Variable

```bash
# Set new key on Heroku
heroku config:set SNOWFLAKE_PRIVATE_KEY_BASE64="<paste_base64_key>" -a hackthetrack-api

# Verify it was set (shows first few characters):
heroku config:get SNOWFLAKE_PRIVATE_KEY_BASE64 -a hackthetrack-api | head -c 50
```

### 5. Test Connection

```bash
# Check Heroku logs for successful connection
heroku logs --tail -a hackthetrack-api | grep "Snowflake"

# Test telemetry endpoint
curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/telemetry/drivers

# Should return: {"drivers_with_telemetry":[...],"count":35}
```

### 6. Replace Old Keys

```bash
# Backup old keys (optional)
mv rsa_key.p8 rsa_key.p8.backup.$(date +%Y%m%d)
mv rsa_key.pub rsa_key.pub.backup.$(date +%Y%m%d)

# Replace with new keys
mv rsa_key_new.p8 rsa_key.p8
mv rsa_key_new.pub rsa_key.pub

# Clean up temporary files
rm rsa_key_base64_new.txt
```

### 7. Update Git (if needed for local development)

```bash
# Ensure keys are in .gitignore
echo "*.p8" >> .gitignore
echo "*.pub" >> .gitignore

# Commit .gitignore changes only
git add .gitignore
git commit -m "chore: ensure RSA keys are in .gitignore"
```

## Security Best Practices

### Key Storage
- ✅ **Heroku**: Private key stored as base64 in environment variable
- ✅ **Local Dev**: Private key stored in `backend/rsa_key.p8` with 600 permissions
- ✅ **Git**: Keys excluded via `.gitignore`
- ❌ **Never**: Store keys in code, logs, or version control

### Access Control
- Only authorized team members should have access to:
  - Heroku production environment (`hackthetrack-api`)
  - Snowflake `ACCOUNTADMIN` role
  - Local key files on development machines

### Monitoring
- Monitor Heroku logs for authentication failures:
  ```bash
  heroku logs --tail -a hackthetrack-api | grep "JWT token is invalid"
  ```
- Set up alerts for repeated authentication failures

## Troubleshooting

### Connection Failures After Rotation

**Error**: `JWT token is invalid`

**Solution**: Verify public key is registered in Snowflake:
```sql
DESC USER hackthetrack_svc;
-- Check RSA_PUBLIC_KEY column
```

**Error**: `250001 (08001): Failed to connect to DB`

**Solution**:
1. Check private key is correctly base64 encoded
2. Verify Heroku environment variable is set correctly
3. Ensure key format is PKCS#8 (not PKCS#1)

### Column Name Issues

**Error**: `'VEHICLE_NUMBER' not found`

**Solution**: Snowflake returns uppercase column names. Code handles both:
```python
column_name = 'VEHICLE_NUMBER' if 'VEHICLE_NUMBER' in df.columns else 'vehicle_number'
```

## Current Deployment Status

### ✅ Successfully Configured
- RSA keypair authentication (MFA-compatible)
- Heroku environment variables set
- Connection to `HACKTHETRACK.TELEMETRY` database
- Queries to `TELEMETRY_DATA_ALL` table
- Telemetry drivers endpoint returning 35 drivers

### Environment Variables (Heroku)
```bash
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_PRIVATE_KEY_BASE64=<base64_encoded_key>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true
```

### Database Schema
```sql
Database: HACKTHETRACK
Schema: TELEMETRY
Table: TELEMETRY_DATA_ALL

-- Table contains telemetry data for 35 drivers
-- Key columns: VEHICLE_NUMBER, TRACK_ID, RACE_NUM, LAP, DISTANCE_INTO_LAP
```

## Changelog

### November 6, 2025
- ✅ Initial RSA keypair generated
- ✅ Public key registered in Snowflake for `hackthetrack_svc`
- ✅ Private key deployed to Heroku as base64
- ✅ Snowflake connection verified
- ✅ Telemetry queries updated to use `TELEMETRY_DATA_ALL` table
- ✅ Column name handling fixed for Snowflake uppercase conventions
- ✅ Successfully tested: 35 drivers with telemetry data returned

### Next Review: February 4, 2026
- Perform 90-day key rotation
- Review and update this document
- Test all telemetry endpoints after rotation
