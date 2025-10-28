from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to the static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test retrieving the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0
    
    # Check structure of an activity
    first_activity = next(iter(activities.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity
    assert isinstance(first_activity["participants"], list)

def test_signup_for_activity():
    """Test signing up for an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # Test successful signup
    response = client.post(f"/activities/{activity_name}/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "test@mergington.edu" in response.json()["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities[activity_name]["participants"]

def test_signup_duplicate():
    """Test that students cannot sign up for the same activity twice"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # First signup should succeed
    response = client.post(f"/activities/{activity_name}/signup?email=duplicate@mergington.edu")
    assert response.status_code == 200
    
    # Second signup should fail
    response = client.post(f"/activities/{activity_name}/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # First sign up a test participant
    client.post(f"/activities/{activity_name}/signup?email=unregister@mergington.edu")
    
    # Test successful unregistration
    response = client.delete(f"/activities/{activity_name}/unregister?email=unregister@mergington.edu")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "unregister@mergington.edu" in response.json()["message"]
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert "unregister@mergington.edu" not in activities[activity_name]["participants"]

def test_unregister_not_registered():
    """Test unregistering a student who is not registered"""
    # Get first activity name
    activities = client.get("/activities").json()
    activity_name = next(iter(activities.keys()))
    
    # Attempt to unregister a non-registered student
    response = client.delete(f"/activities/{activity_name}/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()