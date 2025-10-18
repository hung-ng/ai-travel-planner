"""
Initialize database tables
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import engine, Base
from app.models.trip import Trip
from app.models.conversation import Conversation

def init_db():
    """Create all tables"""
    print("Creating database tables...")
    
    # Import all models to register them
    # This ensures Base.metadata knows about all tables
    
    # Drop all tables (careful in production!)
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized successfully!")
    print(f"Tables created: {list(Base.metadata.tables.keys())}")

if __name__ == "__main__":
    init_db()