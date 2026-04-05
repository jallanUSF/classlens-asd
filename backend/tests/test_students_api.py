"""Tests for student CRUD API endpoints."""


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_students(client):
    resp = client.get("/api/students")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # maya, jaylen, sofia
    # Check summary shape
    student = data[0]
    assert "student_id" in student
    assert "name" in student
    assert "grade" in student
    assert "goal_count" in student


def test_get_student(client):
    resp = client.get("/api/students/maya_2026")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Maya"
    assert "iep_goals" in data
    assert len(data["iep_goals"]) >= 1


def test_get_student_not_found(client):
    resp = client.get("/api/students/nonexistent_student")
    assert resp.status_code == 404


def test_create_and_delete_student(client):
    new_student = {
        "student_id": "test_api_student",
        "name": "Test Student",
        "grade": 3,
        "asd_level": 2,
        "communication_level": "verbal",
        "interests": ["coding"],
        "iep_goals": [],
    }
    # Create
    resp = client.post("/api/students", json=new_student)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Test Student"

    # Verify exists
    resp = client.get("/api/students/test_api_student")
    assert resp.status_code == 200

    # Delete
    resp = client.delete("/api/students/test_api_student")
    assert resp.status_code == 200

    # Verify gone
    resp = client.get("/api/students/test_api_student")
    assert resp.status_code == 404


def test_create_duplicate_student(client):
    resp = client.post("/api/students", json={
        "student_id": "maya_2026",
        "name": "Duplicate Maya",
        "grade": 3,
    })
    assert resp.status_code == 409


def test_update_student(client):
    # First create a test student
    client.post("/api/students", json={
        "student_id": "test_update_student",
        "name": "Original Name",
        "grade": 2,
    })

    # Update
    resp = client.put("/api/students/test_update_student", json={
        "name": "Updated Name",
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"
    assert resp.json()["grade"] == 2  # unchanged field preserved

    # Cleanup
    client.delete("/api/students/test_update_student")


def test_list_alerts(client):
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_chat_without_student(client):
    resp = client.post("/api/chat", json={
        "message": "Hello, what can you do?",
        "conversation_history": [],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert data["role"] == "assistant"


def test_chat_with_student(client):
    resp = client.post("/api/chat", json={
        "message": "How is this student doing?",
        "student_id": "maya_2026",
        "conversation_history": [],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert "Maya" in data["content"] or "maya" in data["content"].lower()
