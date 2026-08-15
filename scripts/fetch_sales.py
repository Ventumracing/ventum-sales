#!/usr/bin/env python3
"""Fetch the full /sales node from Firebase using an Admin SDK service account.

Replaces the old plain `curl .../sales.json` used by the daily sync Action.
That approach stopped working once the Realtime Database rules required a
signed-in user to read /sales (a Round-4 security fix) -- the Action had no
way to sign in, so it was silently writing {"error":"Permission denied"}
into sales.json instead of real data. A service account bypasses the
security rules entirely (the same way the Firebase Admin SDK always does
for trusted server-side code), so this fetch works regardless of what the
client-facing read rules require.

Expects the service account JSON key in the FIREBASE_SERVICE_ACCOUNT_KEY
environment variable (set from a GitHub Actions secret -- never committed
to the repo).
"""
import json
import os
import sys

import firebase_admin
from firebase_admin import credentials, db

DATABASE_URL = 'https://ventum-sales-default-rtdb.firebaseio.com'


def main():
    dest = sys.argv[1] if len(sys.argv) > 1 else 'sales.json'
    key_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY')
    if not key_json:
        print('FIREBASE_SERVICE_ACCOUNT_KEY is not set -- add it as a GitHub Actions secret.', file=sys.stderr)
        sys.exit(1)
    cred = credentials.Certificate(json.loads(key_json))
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
    data = db.reference('sales').get() or {}
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f'Fetched {len(data)} sales record(s) to {dest}')


if __name__ == '__main__':
    main()
