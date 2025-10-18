from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=TripResponse)
async def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    """Create a new trip"""
    db_trip = Trip(**trip.dict())
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

@router.get("/", response_model=List[TripResponse])
async def get_trips(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all trips"""
    trips = db.query(Trip).offset(skip).limit(limit).all()
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get a specific trip"""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.put("/{trip_id}", response_model=TripResponse)
async def update_trip(trip_id: int, trip: TripCreate, db: Session = Depends(get_db)):
    """Update a trip"""
    db_trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    for key, value in trip.dict().items():
        setattr(db_trip, key, value)
    
    db.commit()
    db.refresh(db_trip)
    return db_trip