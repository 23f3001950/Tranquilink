#!/usr/bin/env python3
"""
TranquiLink - Mental Wellness Platform
Run:  python run.py
Then: http://localhost:5050

Demo accounts
─────────────────────────────────────────────────
Admin      admin@tranquilink.in     / admin123
Counsellor (register at /counsellor/register, then admin approves)
Student    (register at /register)
"""
from app import app, init_db

if __name__ == '__main__':
    print("=" * 52)
    print("  TranquiLink · Mental Wellness Platform")
    print("=" * 52)
    print("Initialising database...")
    init_db()
    print("Ready.\n")
    print("  Admin login : admin@tranquilink.in / admin123")
    print("  Counsellor  : register at /counsellor/register")
    print("  Student     : register at /register\n")
    print("  Open → http://localhost:5050")
    print("=" * 52)
    app.run(debug=True, port=5050)
