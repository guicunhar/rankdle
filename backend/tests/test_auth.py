def test_register_login_and_upgrade_guest_merges_history(client, sample_challenge, db_session):
    device_headers = {"X-Device-Id": "guest-device-1"}

    # play as guest first so there is history to merge
    item = db_session.query(sample_challenge.items[0].__class__).filter_by(
        daily_challenge_id=sample_challenge.id, rank=34
    ).first()
    client.post(
        f"/api/v1/daily/{sample_challenge.id}/guess",
        json={"item_id": item.id},
        headers=device_headers,
    )

    resp = client.post(
        "/api/v1/auth/upgrade-guest",
        json={"device_id": "guest-device-1", "email": "player@example.com", "password": "hunter2"},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == "player@example.com"
    assert body["games_played"] == 1  # merged from the guest session
    assert body["exact_hits"] == 1

    # can also log in normally afterwards
    login = client.post("/api/v1/auth/login", json={"email": "player@example.com", "password": "hunter2"})
    assert login.status_code == 200

    bad_login = client.post("/api/v1/auth/login", json={"email": "player@example.com", "password": "wrong"})
    assert bad_login.status_code == 401


def test_upgrade_guest_without_history_returns_404(client):
    resp = client.post(
        "/api/v1/auth/upgrade-guest",
        json={"device_id": "unknown-device", "email": "nope@example.com", "password": "hunter2"},
    )
    assert resp.status_code == 404
