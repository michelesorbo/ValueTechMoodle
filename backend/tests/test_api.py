from httpx import AsyncClient

from tests.scorm_factory import scorm12_zip


async def test_health_live(client: AsyncClient) -> None:
    r = await client.get("/api/health/live")
    assert r.status_code == 200


async def test_health_ready(client: AsyncClient) -> None:
    r = await client.get("/api/health/ready")
    assert r.json()["database"] == "ok"


async def test_course_crud_and_conflict(client: AsyncClient) -> None:
    payload = {"code": "AI-AGENT-01", "title": "AI Agentiche nella programmazione"}
    r = await client.post("/api/courses", json=payload)
    assert r.status_code == 201, r.text
    course_id = r.json()["id"]

    assert (await client.post("/api/courses", json=payload)).status_code == 409

    r = await client.patch(f"/api/courses/{course_id}", json={"is_published": True})
    assert r.json()["is_published"] is True

    r = await client.get("/api/courses")
    assert any(c["id"] == course_id for c in r.json())


async def test_scorm_upload_launch_commit(client: AsyncClient) -> None:
    course = (await client.post("/api/courses", json={"code": "SCORM-01", "title": "T"})).json()

    r = await client.post(
        "/api/scorm/packages",
        data={"course_id": course["id"]},
        files={"file": ("demo.zip", scorm12_zip(), "application/zip")},
    )
    assert r.status_code == 201, r.text
    pkg = r.json()
    assert pkg["version"] == "1.2"

    launch = (await client.get(f"/api/scorm/packages/{pkg['id']}/launch")).json()
    assert launch["launch_url"].endswith("/index.html")

    # Il contenuto SCORM è servito dallo stesso origin
    content = await client.get(launch["launch_url"])
    assert content.status_code == 200
    assert "SCO demo" in content.text

    core = {"lesson_status": "passed", "score": {"raw": "85"}, "total_time": "0000:05:00"}
    commit = {"cmi": {"core": core}}
    r = await client.post(launch["commit_url"], json=commit)
    assert r.json() == {"result": True, "errorCode": 0}

    attempt = (await client.get(f"/api/scorm/attempts/{launch['attempt_id']}")).json()
    assert attempt["completion_status"] == "passed"
    assert attempt["success_status"] == "passed"
    assert attempt["score_raw"] == 85.0

    # Rilancio: stesso tentativo, CMI ripristinato
    relaunch = (await client.get(f"/api/scorm/packages/{pkg['id']}/launch")).json()
    assert relaunch["attempt_id"] == launch["attempt_id"]
    assert relaunch["cmi"]["core"]["lesson_status"] == "passed"


async def test_upload_invalid_package(client: AsyncClient) -> None:
    course = (await client.post("/api/courses", json={"code": "BAD-01", "title": "T"})).json()
    r = await client.post(
        "/api/scorm/packages",
        data={"course_id": course["id"]},
        files={"file": ("x.zip", b"garbage", "application/zip")},
    )
    assert r.status_code == 422
