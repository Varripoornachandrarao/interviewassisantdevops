import pytest
from app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_start_interview_missing_subject(client):
    """Test start interview with default subject"""
    response = client.post('/start-interview', 
                          data=json.dumps({}),
                          content_type='application/json')
    # Since it streams audio, we check if it returns a 200 and some data
    assert response.status_code == 200
    assert response.mimetype == 'text/plain'

def test_get_feedback_no_session(client):
    """Test get feedback with invalid session"""
    response = client.post('/get-feedback',
                          data=json.dumps({"session_id": "invalid"}),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
