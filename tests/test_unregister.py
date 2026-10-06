import importlib.util
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient


module_path = Path(__file__).resolve().parents[1] / "src" / "app.py"
spec = importlib.util.spec_from_file_location("app_module", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

client = TestClient(module.app)


def test_unregister_participant_removes_email():
    activity_name = "Chess Club"
    original = module.activities[activity_name]["participants"][:]
    email = "teststudent@mergington.edu"
    module.activities[activity_name]["participants"].append(email)

    try:
        response = client.delete(f"/activities/{quote(activity_name)}/participants/{quote(email)}")

        assert response.status_code == 200
        assert email not in module.activities[activity_name]["participants"]
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
    finally:
        module.activities[activity_name]["participants"] = original


def test_unregister_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants/missing@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
