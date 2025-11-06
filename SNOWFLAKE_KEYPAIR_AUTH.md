# Snowflake Key-Pair Authentication Setup

## Problem

Your Snowflake account has MFA enforced at the account level, which affects even service accounts. Key-pair authentication bypasses MFA while maintaining security.

## Solution: RSA Key-Pair Authentication

This is actually MORE secure than passwords and is Snowflake's recommended approach for programmatic access.

### Step 1: Generate RSA Key Pair (On your local machine)

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Generate private key (2048-bit RSA)
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt

# Generate public key from private key
openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub

echo "✅ Keys generated!"
```

### Step 2: Assign Public Key to Service Account

Log into Snowflake Web UI and run:

```sql
-- Copy the contents of rsa_key.pub (without BEGIN/END lines)
-- Then run:

ALTER USER hackthetrack_svc SET RSA_PUBLIC_KEY='MIIBIjANBg...YOUR_PUBLIC_KEY_HERE...AQAB';

-- Verify it was set:
DESC USER hackthetrack_svc;
```

### Step 3: Update Backend to Use Key-Pair Auth

Update `backend/app/services/snowflake_service.py`:

```python
def get_connection(self):
    """Create and return a Snowflake connection with key-pair auth."""
    if not all([self.account, self.user]):
        raise ValueError("Missing Snowflake credentials")

    # Read private key
    with open(os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH", "rsa_key.p8"), "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    pkb = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    return snowflake.connector.connect(
        account=self.account,
        user=self.user,
        private_key=pkb,
        warehouse=self.warehouse,
        database=self.database,
        schema=self.schema,
        role=self.role
    )
```

### Step 4: Update .env

```env
# Remove password, add key path
SNOWFLAKE_PRIVATE_KEY_PATH=rsa_key.p8
# No SNOWFLAKE_PASSWORD needed
```

### Step 5: Test Connection

```bash
cd backend
source venv/bin/activate
python -c "from app.services.snowflake_service import snowflake_service; print(snowflake_service.check_connection())"
```

## Quick Fix Alternative (Less Secure, But Works)

If you need this working ASAP for the competition, you can temporarily disable MFA enforcement:

### In Snowflake Web UI (as ACCOUNTADMIN):

```sql
-- Option A: Allow MFA bypass for service account
ALTER USER hackthetrack_svc SET MINS_TO_BYPASS_MFA = 999999;

-- Option B: Disable account-level MFA enforcement (affects all users)
ALTER ACCOUNT SET SAML_IDENTITY_PROVIDER = NULL;
ALTER ACCOUNT SET ALLOW_CLIENT_MFA_CACHING = TRUE;
```

Then the password authentication will work without MFA.

## Recommendation

For **competition/demo**: Use the quick fix (MINS_TO_BYPASS_MFA)
For **production**: Use key-pair authentication (more secure, no MFA needed)

Let me know which approach you prefer and I'll help you implement it!
