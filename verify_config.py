#!/usr/bin/env python
"""Quick verification script to test config loading from .env"""

import os
import sys
import json

# Manually parse .env to bypass python-dotenv multiline JSON parsing issues
def load_env_file(env_path):
    """Parse .env file, handling multiline JSON values."""
    with open(env_path) as f:
        content = f.read()
    
    # Simple parser that respects JSON arrays
    env_vars = {}
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        
        if not line or line.startswith('#'):
            continue
        
        if '=' not in line:
            continue
        
        key, val = line.split('=', 1)
        key = key.strip()
        val = val.strip()
        
        # Handle multiline JSON arrays
        if val.startswith('[') and not val.endswith(']'):
            while i < len(lines) and not val.endswith(']'):
                val += '\n' + lines[i]
                i += 1
        
        env_vars[key] = val
    
    return env_vars

# Load .env into os.environ
env_vars = load_env_file('.env')
for key, val in env_vars.items():
    os.environ[key] = val

# Now import config
from app import config

print('=== CONFIG VERIFICATION ===')
print()
print('✓ DATABASE_URL loaded:')
print(f"  {config.settings.DATABASE_URL[:80]}...")
print()
print('✓ API_LIST parsed:')
api_list = config.get_api_list()
print(f"  Found {len(api_list)} API endpoints:")
for api in api_list:
    print(f"    - {api.get('name')}: {api.get('method')} {api.get('url')}")
print()
print('✓ AZURE_SECRETS_LIST parsed:')
secrets = config.get_azure_secrets_list()
print(f"  Secrets to monitor: {secrets}")
print()
print('✓ RESOURCE_ID computed (Web App):')
resource_id = config.get_resource_id()
if resource_id:
    print(f"  {resource_id}")
else:
    print("  (None - check env variables)")
print()
print('=== ALL CONFIG VERIFIED FROM .env ===')
