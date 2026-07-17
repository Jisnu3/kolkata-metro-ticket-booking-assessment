from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import datetime

Base = declarative_base()

class SystemConfig(Base):
    __tablename__ = "system_config"
    key = Column(String(100), primary_key=True)
    config_value = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeat"
    id = Column(Integer, primary_key=True)
    last_run_timestamp = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50))

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number = Column(String(100), unique=True, nullable=False)
    source_station = Column(String(100), nullable=False)
    destination_station = Column(String(100), nullable=False)
    fare = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="ACTIVE", nullable=False) # 'ACTIVE', 'EXPIRED', 'USED'
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    expires_at = Column(DateTime(timezone=True), nullable=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

# Database Engine initialization
import os
db_url = settings.DATABASE_URL
engine = None
try:
    engine = create_engine(db_url, pool_pre_ping=True)
    with engine.connect() as conn:
        pass
    print("Successfully connected to PostgreSQL database!")
except Exception as e:
    print(f"Failed to connect to PostgreSQL database ({db_url}) due to: {e}")
    print("Falling back to local SQLite database for transactional operations...")
    # Store the database inside the backend/app/db directory for consistency
    fallback_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kolkata_metro_fallback.db")
    fallback_db = f"sqlite:///{fallback_path}"
    engine = create_engine(fallback_db, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_and_seed_db():
    """
    Creates tables if they don't exist and seeds required configuration data.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        config_a = db.query(SystemConfig).filter(SystemConfig.key == "system_a").first()
        if not config_a:
            config_a = SystemConfig(
                key="system_a",
                config_value="Alpha77X#",
                created_at=datetime.datetime.now(datetime.timezone.utc),
                updated_at=datetime.datetime.now(datetime.timezone.utc)
            )
            db.add(config_a)
        
        heartbeat = db.query(WorkerHeartbeat).filter(WorkerHeartbeat.id == 1).first()
        if not heartbeat:
            heartbeat = WorkerHeartbeat(
                id=1,
                last_run_timestamp=datetime.datetime.now(datetime.timezone.utc),
                status="INITIALIZED"
            )
            db.add(heartbeat)
        
        db.commit()
        print("Database initialized and seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

def get_db():
    """
    FastAPI dependency that provides a transactional scope.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

