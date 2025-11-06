#!/bin/bash
# Script to prepare Snowflake private key for Vercel environment variable
# Usage: ./prepare_private_key_for_vercel.sh path/to/rsa_key.p8

set -e

# Check if file path provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_private_key.p8>"
    echo "Example: $0 ../rsa_key.p8"
    exit 1
fi

KEY_FILE="$1"

# Check if file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "Error: File not found: $KEY_FILE"
    exit 1
fi

echo "=================================================="
echo "Snowflake Private Key to Vercel Environment Variable"
echo "=================================================="
echo ""
echo "Processing: $KEY_FILE"
echo ""

# Convert private key to single-line format
# This replaces newlines with \n for environment variable storage
ONELINE_KEY=$(cat "$KEY_FILE" | tr '\n' '\\n')

# Create temporary file with instructions
TEMP_FILE="snowflake_key_for_vercel.txt"

cat > "$TEMP_FILE" << EOF
================================================
SNOWFLAKE PRIVATE KEY FOR VERCEL
================================================

Copy the content below and add it to Vercel as an environment variable:

Variable Name:  SNOWFLAKE_PRIVATE_KEY
Variable Value:
$ONELINE_KEY

INSTRUCTIONS:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Click "Add New"
3. Name: SNOWFLAKE_PRIVATE_KEY
4. Value: Copy the entire key above (including -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY-----)
5. Select environments: Production, Preview, Development
6. Click "Save"

IMPORTANT:
- The key is in one-line format with \\n representing newlines
- The backend code will convert \\n back to actual newlines
- Never commit this file to git
- Delete this file after adding to Vercel

VERIFICATION:
After adding to Vercel, test with:
  vercel env pull .env.vercel
  grep SNOWFLAKE_PRIVATE_KEY .env.vercel

================================================
EOF

echo "✓ Private key converted to environment variable format"
echo "✓ Instructions saved to: $TEMP_FILE"
echo ""
echo "Next steps:"
echo "1. Open $TEMP_FILE"
echo "2. Copy the key value"
echo "3. Add to Vercel Dashboard → Environment Variables"
echo "4. Delete $TEMP_FILE after use (contains sensitive data)"
echo ""
echo "SECURITY: Do not commit $TEMP_FILE to git!"
echo "=================================================="

# Set restrictive permissions on output file
chmod 600 "$TEMP_FILE"

# Offer to display the key
echo ""
read -p "Display the key now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "=================================================="
    cat "$TEMP_FILE"
    echo "=================================================="
fi
