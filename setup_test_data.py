#!/usr/bin/env python3
"""
Test data setup script for ChainLines moderation queue testing.
This script:
1. Creates a test user (NEW_USER role)
2. Creates pending edits for that user
3. Optionally sets the logged-in user as ADMIN
"""

import psycopg2
from psycopg2.extras import Json
import uuid
from datetime import datetime
import json
import sys

# Database connection parameters
DB_HOST = "localhost"
DB_NAME = "cycling_lineage"
DB_USER = "cycling"
DB_PASSWORD = "cycling"
DB_PORT = 5432

def connect_db():
    """Connect to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)

def setup_test_data(admin_email=None):
    """Setup test data for moderation testing."""
    conn = connect_db()
    cur = conn.cursor()
    
    try:
        print("🚀 Setting up test data for moderation queue...\n")
        
        # 1. Create test user (NEW_USER)
        test_user_id = str(uuid.uuid4())
        test_email = "testuser@example.com"
        test_google_id = "test-google-id-" + str(uuid.uuid4())[:8]
        test_display_name = "Test User"
        
        cur.execute("""
            INSERT INTO users (user_id, google_id, email, display_name, role, approved_edits_count, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET role = 'NEW_USER'
            RETURNING user_id;
        """, (test_user_id, test_google_id, test_email, test_display_name, "NEW_USER", 0))
        result = cur.fetchone()
        test_user_id = result[0]
        print(f"✅ Created test user: {test_email} (NEW_USER)")
        print(f"   User ID: {test_user_id}\n")
        
        # 2. Get sample era for metadata edit
        cur.execute("SELECT era_id, registered_name, season_year FROM team_era LIMIT 1;")
        era_data = cur.fetchone()
        if not era_data:
            print("❌ No team eras found in database. Please seed the database first.")
            return
        
        era_id, era_name, era_year = era_data
        print(f"📋 Using sample era: {era_name} ({era_year})")
        print(f"   Era ID: {era_id}\n")
        
        # 3. Create METADATA edit (pending)
        metadata_edit_id = str(uuid.uuid4())
        metadata_changes = {
            "registered_name": f"{era_name} - UPDATED",
            "tier_level": 1
        }
        
        cur.execute("""
            INSERT INTO edits (edit_id, user_id, edit_type, target_era_id, changes, reason, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (
            metadata_edit_id,
            test_user_id,
            "METADATA",
            era_id,
            Json(metadata_changes),
            "Test: Updated team metadata",
            "PENDING"
        ))
        print(f"✅ Created METADATA edit (PENDING)")
        print(f"   Edit ID: {metadata_edit_id}")
        print(f"   Changes: {json.dumps(metadata_changes, indent=2)}\n")
        
        # 4. Create another METADATA edit
        metadata_edit_id_2 = str(uuid.uuid4())
        metadata_changes_2 = {
            "uci_code": "TST"
        }
        
        cur.execute("""
            INSERT INTO edits (edit_id, user_id, edit_type, target_era_id, changes, reason, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING;
        """, (
            metadata_edit_id_2,
            test_user_id,
            "METADATA",
            era_id,
            Json(metadata_changes_2),
            "Test: Updated UCI code",
            "PENDING"
        ))
        print(f"✅ Created another METADATA edit (PENDING)")
        print(f"   Edit ID: {metadata_edit_id_2}")
        print(f"   Changes: {json.dumps(metadata_changes_2, indent=2)}\n")
        
        # 5. If admin_email provided, set that user as ADMIN
        if admin_email:
            cur.execute("""
                UPDATE users SET role = 'ADMIN', updated_at = NOW()
                WHERE email = %s
                RETURNING user_id, email, role;
            """, (admin_email,))
            result = cur.fetchone()
            if result:
                print(f"✅ Set {admin_email} as ADMIN")
                print(f"   User ID: {result[0]}")
                print(f"   Role: {result[2]}\n")
            else:
                print(f"⚠️  User {admin_email} not found in database.")
                print(f"   Please login first to create the account, then run this script again.\n")
        
        # Commit all changes
        conn.commit()
        print("✅ All test data committed successfully!\n")
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SETUP SUMMARY")
        print("=" * 60)
        print(f"Test User Email:  {test_email}")
        print(f"Test User Role:   NEW_USER")
        print(f"Pending Edits:    2 (both METADATA type)")
        if admin_email:
            print(f"Admin User Email: {admin_email}")
            print(f"Admin User Role: ADMIN")
        print("\n🎯 Next steps:")
        print("1. Login as your Google account (you should be ADMIN)")
        print("2. Navigate to http://localhost:5173/moderation")
        print("3. You'll see 2 pending edits from 'testuser@example.com'")
        print("4. Click on an edit to review and approve/reject it")
        print("=" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error setting up test data: {e}")
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    admin_email = None
    if len(sys.argv) > 1:
        admin_email = sys.argv[1]
        print(f"ℹ️  Setting admin email: {admin_email}\n")
    else:
        print("ℹ️  No admin email provided. Only creating test user and edits.")
        print("   Usage: python setup_test_data.py <your-google-email>\n")
    
    setup_test_data(admin_email)
