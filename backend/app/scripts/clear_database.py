import psycopg2

DB_HOST = "localhost"
DB_NAME = "cycling_lineage"
DB_USER = "cycling"
DB_PASSWORD = "cycling"
DB_PORT = 5432

def clear_database():
    """Clear all team and lineage data from the database."""
    conn = psycopg2.connect(
        host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    cur = conn.cursor()
    
    try:
        print("Clearing database tables...")
        
        # List of tables to clear (in order to respect foreign key constraints)
        tables = [
            "lineage_link",
            "lineage_event", 
            "team_era",
            "team_node",
            "sponsors",
            "edits"
        ]
        
        for table in tables:
            try:
                cur.execute(f"DELETE FROM {table};")
                print(f"  ✓ Cleared {table}")
            except psycopg2.errors.UndefinedTable:
                print(f"  ⊘ Table {table} does not exist, skipping")
                conn.rollback()
        
        conn.commit()
        print("\n✅ Database cleared successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error clearing database: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    clear_database()
