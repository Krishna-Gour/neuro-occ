from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./neuro_occ.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Pilot(Base):
    __tablename__ = "pilots"

    id = Column(Integer, primary_key=True, index=True)
    pilot_id = Column(String, unique=True, index=True)
    name = Column(String)
    base = Column(String)
    total_hours = Column(Float)
    fatigue_score = Column(Float)
    last_rest_end = Column(DateTime)
    consecutive_night_duties = Column(Integer)

class Aircraft(Base):
    __tablename__ = "aircraft"

    id = Column(Integer, primary_key=True, index=True)
    tail_number = Column(String, unique=True, index=True)
    type = Column(String)
    base = Column(String)
    health_score = Column(Float)

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String, unique=True, index=True)
    origin = Column(String)
    destination = Column(String)
    scheduled_departure = Column(DateTime)
    scheduled_arrival = Column(DateTime)
    aircraft_tail = Column(String)
    pilot_id = Column(String)
    status = Column(String)

class Airport(Base):
    __tablename__ = "airports"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)