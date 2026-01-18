"""
Database migration script to add user_id columns to existing tables.
Run this once after updating to the authentication version.
"""
from app import app, db, User, Overlay, StreamSettings
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        print("Starting database migration...")
        
        # Create users table if it doesn't exist
        db.create_all()
        print("[OK] Users table created/verified")
        
        # Check if user_id column exists in overlays table
        try:
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='overlays' AND column_name='user_id'
            """))
            overlay_has_user_id = result.fetchone() is not None
        except:
            overlay_has_user_id = False
        
        # Check if user_id column exists in stream_settings table
        try:
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='stream_settings' AND column_name='user_id'
            """))
            settings_has_user_id = result.fetchone() is not None
        except:
            settings_has_user_id = False
        
        # Add user_id to overlays if it doesn't exist
        if not overlay_has_user_id:
            print("Adding user_id column to overlays table...")
            try:
                db.session.execute(text("""
                    ALTER TABLE overlays 
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                print("[OK] Added user_id to overlays table")
            except Exception as e:
                print(f"Error adding user_id to overlays: {e}")
                db.session.rollback()
        else:
            print("[OK] overlays table already has user_id column")
        
        # Add user_id to stream_settings if it doesn't exist
        if not settings_has_user_id:
            print("Adding user_id column to stream_settings table...")
            try:
                # First add as nullable
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ADD COLUMN user_id INTEGER REFERENCES users(id)
                """))
                db.session.commit()
                print("[OK] Added user_id to stream_settings table")
                
                # Delete existing stream_settings that don't have user_id
                # (they won't work with the new auth system anyway)
                db.session.execute(text("""
                    DELETE FROM stream_settings WHERE user_id IS NULL
                """))
                db.session.commit()
                print("[OK] Cleaned up orphaned stream_settings")
                
                # Now make it NOT NULL and UNIQUE
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ALTER COLUMN user_id SET NOT NULL
                """))
                db.session.execute(text("""
                    ALTER TABLE stream_settings 
                    ADD CONSTRAINT stream_settings_user_id_unique UNIQUE (user_id)
                """))
                db.session.commit()
                print("[OK] Made user_id NOT NULL and UNIQUE in stream_settings")
            except Exception as e:
                print(f"Error adding user_id to stream_settings: {e}")
                db.session.rollback()
        else:
            print("[OK] stream_settings table already has user_id column")
        
        # Clean up overlays without user_id
        try:
            result = db.session.execute(text("""
                DELETE FROM overlays WHERE user_id IS NULL
            """))
            db.session.commit()
            deleted_count = result.rowcount
            if deleted_count > 0:
                print(f"[OK] Cleaned up {deleted_count} orphaned overlays")
        except Exception as e:
            print(f"Note: Could not clean up overlays: {e}")
        
        # Make user_id NOT NULL in overlays if it's nullable
        try:
            db.session.execute(text("""
                ALTER TABLE overlays 
                ALTER COLUMN user_id SET NOT NULL
            """))
            db.session.commit()
            print("[OK] Made user_id NOT NULL in overlays")
        except Exception as e:
            # Column might already be NOT NULL or have NULL values
            print(f"Note: Could not set user_id to NOT NULL in overlays: {e}")
            db.session.rollback()
        
        print("\n[SUCCESS] Database migration completed!")
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Register a new user account")
        print("3. Start using the application")

if __name__ == '__main__':
    migrate_database()
