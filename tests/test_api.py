"""
Tests for the Mergington High School API using pytest and FastAPI TestClient
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball league and training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis singles and doubles matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Stage acting, improvisation, and theatrical productions",
            "schedule": "Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["grace@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, sculpture and visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate and public speaking",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["marcus@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through experiments",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["rachel@mergington.edu", "tyler@mergington.edu"]
        }
    }
    
    # Import and reset
    from app import activities
    activities.clear()
    activities.update(original)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original)


class TestRootEndpoint:
    def test_root_redirects_to_static(self):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivities:
    def test_get_activities_returns_all(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_has_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_chess_club_has_participants(self, reset_activities):
        """Test that Chess Club has the expected participants"""
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        assert "michael@mergington.edu" in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]
        assert len(chess["participants"]) == 2


class TestSignupEndpoint:
    def test_signup_new_participant(self, reset_activities):
        """Test signing up a new participant to an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        chess = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess["participants"]

    def test_signup_duplicate_participant(self, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, reset_activities):
        """Test that signup fails for nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestRemoveParticipantEndpoint:
    def test_remove_participant(self, reset_activities):
        """Test removing a participant from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        chess = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess["participants"]
        assert "daniel@mergington.edu" in chess["participants"]

    def test_remove_nonexistent_participant(self, reset_activities):
        """Test removing a participant that doesn't exist"""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=notinlist@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_from_nonexistent_activity(self, reset_activities):
        """Test removing from activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Club/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_all_and_verify_list(self, reset_activities):
        """Test removing all participants from an activity"""
        # Remove both Chess Club participants
        client.delete("/activities/Chess%20Club/participants?email=michael@mergington.edu")
        client.delete("/activities/Chess%20Club/participants?email=daniel@mergington.edu")
        
        # Verify the list is now empty
        activities_response = client.get("/activities")
        chess = activities_response.json()["Chess Club"]
        assert len(chess["participants"]) == 0


class TestActivityIntegration:
    def test_full_signup_and_remove_flow(self, reset_activities):
        """Test the complete flow: signup, verify, remove, verify again"""
        new_email = "integration@test.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Programming%20Class/signup?email={new_email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert new_email in activities_data["Programming Class"]["participants"]
        original_count = len(activities_data["Programming Class"]["participants"])
        
        # Remove
        remove_response = client.delete(
            f"/activities/Programming%20Class/participants?email={new_email}"
        )
        assert remove_response.status_code == 200
        
        # Verify removal
        get_response = client.get("/activities")
        activities_data = get_response.json()
        assert new_email not in activities_data["Programming Class"]["participants"]
        assert len(activities_data["Programming Class"]["participants"]) == original_count - 1

    def test_multiple_participants_signup(self, reset_activities):
        """Test multiple students signing up for the same activity"""
        emails = [f"student{i}@test.edu" for i in range(3)]
        
        for email in emails:
            response = client.post(
                f"/activities/Drama%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        get_response = client.get("/activities")
        drama = get_response.json()["Drama Club"]
        for email in emails:
            assert email in drama["participants"]
        
        # Verify original participant still exists
        assert "grace@mergington.edu" in drama["participants"]
