"""
Integration tests for Trips API endpoints
"""
import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models.trip import Trip, TripStatus


@pytest.mark.integration
class TestCreateTripEndpoint:
    """Integration tests for POST /api/trips/ endpoint"""

    def test_create_trip_success(self, client, test_user_id, db_session):
        """Test successful trip creation"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Barcelona, Spain",
            "start_date": "2024-07-15T00:00:00",
            "end_date": "2024-07-22T00:00:00",
            "budget": 3000,
            "preferences": {
                "interests": ["culture", "food", "beaches"],
                "travel_style": "moderate",
                "accommodation": "hotel"
            }
        }

        response = client.post("/api/trips/", json=trip_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert data["destination"] == "Barcelona, Spain"
        assert data["user_id"] == test_user_id
        assert data["budget"] == 3000
        assert data["status"] == TripStatus.GATHERING.value
        assert "id" in data
        assert "created_at" in data

        # Verify trip was stored in database
        trip = db_session.query(Trip).filter_by(id=data["id"]).first()
        assert trip is not None
        assert trip.destination == "Barcelona, Spain"
        assert trip.preferences["interests"] == ["culture", "food", "beaches"]

    def test_create_trip_without_budget(self, client, test_user_id, db_session):
        """Test creating a trip without specifying budget"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Rome, Italy",
            "start_date": "2024-08-01T00:00:00",
            "end_date": "2024-08-10T00:00:00"
        }

        response = client.post("/api/trips/", json=trip_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["budget"] is None

    def test_create_trip_without_preferences(self, client, test_user_id):
        """Test creating a trip without preferences"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "London, UK",
            "start_date": "2024-09-01T00:00:00",
            "end_date": "2024-09-07T00:00:00",
            "budget": 2500
        }

        response = client.post("/api/trips/", json=trip_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["destination"] == "London, UK"

    def test_create_trip_with_past_dates(self, client, test_user_id):
        """Test creating a trip with dates in the past"""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        trip_data = {
            "user_id": test_user_id,
            "destination": "Amsterdam",
            "start_date": past_date,
            "end_date": past_date,
            "budget": 1500
        }

        response = client.post("/api/trips/", json=trip_data)

        # Should still create the trip (no validation for past dates)
        assert response.status_code == status.HTTP_200_OK

    def test_create_trip_missing_required_fields(self, client, test_user_id):
        """Test that missing required fields are rejected"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Paris"
            # Missing start_date and end_date
        }

        response = client.post("/api/trips/", json=trip_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_multiple_trips_same_user(self, client, test_user_id, db_session):
        """Test that a user can create multiple trips"""
        destinations = ["Tokyo", "Seoul", "Bangkok"]

        trip_ids = []
        for destination in destinations:
            trip_data = {
                "user_id": test_user_id,
                "destination": destination,
                "start_date": "2024-10-01T00:00:00",
                "end_date": "2024-10-10T00:00:00",
                "budget": 5000
            }
            response = client.post("/api/trips/", json=trip_data)
            assert response.status_code == status.HTTP_200_OK
            trip_ids.append(response.json()["id"])

        # Verify all trips were created
        trips = db_session.query(Trip).filter(Trip.user_id == test_user_id).all()
        assert len(trips) >= len(destinations)


@pytest.mark.integration
class TestGetTripsEndpoint:
    """Integration tests for GET /api/trips/ endpoint"""

    def test_get_all_trips_empty(self, client, db_session):
        """Test getting trips when none exist"""
        # Clear all trips
        db_session.query(Trip).delete()
        db_session.commit()

        response = client.get("/api/trips/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_trips(self, client, test_user_id, db_session):
        """Test getting all trips"""
        # Create multiple trips
        for i in range(3):
            trip = Trip(
                user_id=test_user_id,
                destination=f"Destination {i}",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 10),
                budget=1000 * (i + 1),
                status=TripStatus.GATHERING
            )
            db_session.add(trip)
        db_session.commit()

        response = client.get("/api/trips/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 3

    def test_get_trips_with_pagination(self, client, test_user_id, db_session):
        """Test pagination parameters"""
        # Create 10 trips
        for i in range(10):
            trip = Trip(
                user_id=test_user_id,
                destination=f"City {i}",
                start_date=datetime(2024, 6, 1),
                end_date=datetime(2024, 6, 10),
                budget=1000,
                status=TripStatus.GATHERING
            )
            db_session.add(trip)
        db_session.commit()

        # Test limit
        response = client.get("/api/trips/?limit=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 5

        # Test skip
        response = client.get("/api/trips/?skip=5&limit=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 5


@pytest.mark.integration
class TestGetTripEndpoint:
    """Integration tests for GET /api/trips/{trip_id} endpoint"""

    def test_get_trip_by_id_success(self, client, test_trip):
        """Test getting a specific trip by ID"""
        response = client.get(f"/api/trips/{test_trip.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == test_trip.id
        assert data["destination"] == test_trip.destination
        assert data["user_id"] == test_trip.user_id
        assert data["budget"] == test_trip.budget
        assert data["status"] == test_trip.status.value

    def test_get_trip_nonexistent_id(self, client):
        """Test getting a trip that doesn't exist"""
        response = client.get("/api/trips/99999")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_trip_invalid_id_format(self, client):
        """Test getting a trip with invalid ID format"""
        response = client.get("/api/trips/invalid")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_trip_includes_all_fields(self, client, test_trip):
        """Test that all trip fields are returned"""
        response = client.get(f"/api/trips/{test_trip.id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        required_fields = [
            "id", "user_id", "destination", "start_date",
            "end_date", "budget", "status", "created_at"
        ]
        for field in required_fields:
            assert field in data


@pytest.mark.integration
class TestUpdateTripEndpoint:
    """Integration tests for PUT /api/trips/{trip_id} endpoint"""

    def test_update_trip_destination(self, client, test_trip, db_session):
        """Test updating trip destination"""
        update_data = {
            "user_id": test_trip.user_id,
            "destination": "Lyon, France",
            "start_date": test_trip.start_date.isoformat(),
            "end_date": test_trip.end_date.isoformat(),
            "budget": test_trip.budget
        }

        response = client.put(f"/api/trips/{test_trip.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["destination"] == "Lyon, France"

        # Verify update in database
        db_session.refresh(test_trip)
        assert test_trip.destination == "Lyon, France"

    def test_update_trip_budget(self, client, test_trip, db_session):
        """Test updating trip budget"""
        update_data = {
            "user_id": test_trip.user_id,
            "destination": test_trip.destination,
            "start_date": test_trip.start_date.isoformat(),
            "end_date": test_trip.end_date.isoformat(),
            "budget": 7500
        }

        response = client.put(f"/api/trips/{test_trip.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["budget"] == 7500

        db_session.refresh(test_trip)
        assert test_trip.budget == 7500

    def test_update_trip_dates(self, client, test_trip, db_session):
        """Test updating trip dates"""
        new_start = datetime(2024, 8, 1).isoformat()
        new_end = datetime(2024, 8, 15).isoformat()

        update_data = {
            "user_id": test_trip.user_id,
            "destination": test_trip.destination,
            "start_date": new_start,
            "end_date": new_end,
            "budget": test_trip.budget
        }

        response = client.put(f"/api/trips/{test_trip.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert new_start in data["start_date"]
        assert new_end in data["end_date"]

    def test_update_trip_preferences(self, client, test_trip):
        """Test updating trip preferences"""
        update_data = {
            "user_id": test_trip.user_id,
            "destination": test_trip.destination,
            "start_date": test_trip.start_date.isoformat(),
            "end_date": test_trip.end_date.isoformat(),
            "budget": test_trip.budget,
            "preferences": {
                "interests": ["adventure", "hiking"],
                "travel_style": "budget"
            }
        }

        response = client.put(f"/api/trips/{test_trip.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK

    def test_update_nonexistent_trip(self, client, test_user_id):
        """Test updating a trip that doesn't exist"""
        update_data = {
            "user_id": test_user_id,
            "destination": "Test",
            "start_date": datetime.now().isoformat(),
            "end_date": datetime.now().isoformat(),
            "budget": 1000
        }

        response = client.put("/api/trips/99999", json=update_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_trip_multiple_fields(self, client, test_trip, db_session):
        """Test updating multiple fields at once"""
        update_data = {
            "user_id": test_trip.user_id,
            "destination": "Venice, Italy",
            "start_date": datetime(2024, 9, 1).isoformat(),
            "end_date": datetime(2024, 9, 10).isoformat(),
            "budget": 4500,
            "preferences": {
                "interests": ["art", "architecture"],
                "travel_style": "luxury"
            }
        }

        response = client.put(f"/api/trips/{test_trip.id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["destination"] == "Venice, Italy"
        assert data["budget"] == 4500

        db_session.refresh(test_trip)
        assert test_trip.destination == "Venice, Italy"
        assert test_trip.budget == 4500


@pytest.mark.integration
class TestTripsDatabaseIntegration:
    """Integration tests for trips database operations"""

    def test_trip_default_status(self, client, test_user_id, db_session):
        """Test that new trips have default status of GATHERING"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Test City",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "budget": 2000
        }

        response = client.post("/api/trips/", json=trip_data)
        trip_id = response.json()["id"]

        trip = db_session.query(Trip).filter_by(id=trip_id).first()
        assert trip.status == TripStatus.GATHERING

    def test_trip_timestamps(self, client, test_user_id, db_session):
        """Test that created_at timestamp is set automatically"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Test City",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "budget": 1000
        }

        response = client.post("/api/trips/", json=trip_data)
        trip_id = response.json()["id"]

        trip = db_session.query(Trip).filter_by(id=trip_id).first()
        assert trip.created_at is not None

    def test_trip_with_json_fields(self, client, test_user_id, db_session):
        """Test storing JSON fields (preferences, itinerary)"""
        trip_data = {
            "user_id": test_user_id,
            "destination": "Test City",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "budget": 3000,
            "preferences": {
                "dietary": ["vegetarian"],
                "activities": ["museums", "walking tours"],
                "pace": "relaxed"
            }
        }

        response = client.post("/api/trips/", json=trip_data)
        trip_id = response.json()["id"]

        trip = db_session.query(Trip).filter_by(id=trip_id).first()
        assert trip.preferences is not None
        assert trip.preferences["dietary"] == ["vegetarian"]
        assert trip.preferences["pace"] == "relaxed"
