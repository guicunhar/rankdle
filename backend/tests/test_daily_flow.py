DEVICE_HEADERS = {"X-Device-Id": "test-device-123"}


def test_get_daily_creates_progress_for_new_player(client, sample_challenge):
    resp = client.get("/api/v1/daily", params={"theme": "musica", "date": "2026-08-26"}, headers=DEVICE_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtheme_title"] == "Músicas mais ouvidas em 2010"
    assert data["target_rank"] == 34
    assert data["lives_total"] == 5  # default_lives fallback
    assert data["lives_remaining"] == 5
    assert data["attempts_used"] == 0
    assert data["is_over"] is False


def test_search_scoped_to_challenge(client, sample_challenge):
    # limit=50 so the (now randomly-ordered) results aren't truncated below the match count
    resp = client.get(
        f"/api/v1/daily/{sample_challenge.id}/search", params={"q": "Item 3", "limit": 50}
    )
    assert resp.status_code == 200
    names = {item["name"] for item in resp.json()}
    assert "Item 3" in names
    assert "Item 34" in names  # "Item 34" also matches substring "Item 3"


def test_search_without_query_browses_all_items_shuffled(client, sample_challenge):
    resp = client.get(f"/api/v1/daily/{sample_challenge.id}/search", params={"limit": 100})
    assert resp.status_code == 200
    names = [item["name"] for item in resp.json()]
    assert len(names) == 50  # every item in the challenge, not just a name-sorted slice
    assert set(names) == {f"Item {r}" for r in range(1, 51)}


def _item_id_for_rank(client, challenge_id, rank):
    resp = client.get(f"/api/v1/daily/{challenge_id}/search", params={"q": f"Item {rank}", "limit": 50})
    for item in resp.json():
        if item["name"] == f"Item {rank}":
            return item["id"]
    raise AssertionError(f"rank {rank} not found in search results")


def test_guess_flow_best_score_and_life_exhaustion(client, sample_challenge):
    cid = sample_challenge.id

    # first (wrong) guess: rank 12 vs target 34 -> score 100-22=78
    # guessed rank (12) is numerically lower than the target (34), so the hint
    # tells the player their guess was "lower" than the answer (needs to go up)
    item_id = _item_id_for_rank(client, cid, 12)
    resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["guess"]["score"] == 78
    assert body["guess"]["direction"] == "lower"
    assert body["lives_remaining"] == 4
    assert body["best_score"] == 78
    assert body["is_over"] is False

    # second (better) guess: rank 30 vs target 34 -> score 96, best_score should update
    item_id = _item_id_for_rank(client, cid, 30)
    resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)
    body = resp.json()
    assert body["guess"]["score"] == 96
    assert body["best_score"] == 96

    # third (worse) guess: rank 1 vs target 34 -> score 67, best_score must NOT regress
    item_id = _item_id_for_rank(client, cid, 1)
    resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)
    body = resp.json()
    assert body["guess"]["score"] == 67
    assert body["best_score"] == 96  # unchanged, best-of-all-attempts semantics

    # exhaust remaining 2 lives with more wrong guesses
    for rank in (2, 3):
        item_id = _item_id_for_rank(client, cid, rank)
        resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)

    body = resp.json()
    assert body["lives_remaining"] == 0
    assert body["is_over"] is True

    # further guesses are rejected once the game is over
    item_id = _item_id_for_rank(client, cid, 34)
    resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)
    assert resp.status_code == 400


def test_exact_guess_ends_game_immediately(client, sample_challenge):
    cid = sample_challenge.id
    item_id = _item_id_for_rank(client, cid, 34)
    resp = client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)
    body = resp.json()
    assert body["guess"]["score"] == 100
    assert body["exact_hit"] is True
    assert body["is_over"] is True
    assert body["lives_remaining"] == 4  # lives don't matter once solved


def test_result_endpoint_reveals_answer_and_stats(client, sample_challenge):
    cid = sample_challenge.id
    item_id = _item_id_for_rank(client, cid, 34)
    client.post(f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS)

    resp = client.get(f"/api/v1/daily/{cid}/result", headers=DEVICE_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["answer"]["name"] == "Item 34"
    assert data["source_url"] == "https://example.com/fonte"
    assert data["player_best_score"] == 100
    assert data["player_exact_hit"] is True
    assert data["players_count"] == 1
    assert data["exact_hit_count"] == 1


def test_result_before_game_over_is_rejected(client, sample_challenge):
    resp = client.get(f"/api/v1/daily/{sample_challenge.id}/result", headers=DEVICE_HEADERS)
    assert resp.status_code == 400


def test_guess_rejects_item_from_other_challenge(client, sample_challenge, db_session):
    from datetime import date

    from app.models.daily_challenge import DailyChallenge
    from app.models.ranking_item import RankingItem

    other = DailyChallenge(
        date=date(2026, 8, 25),
        theme_id=sample_challenge.theme_id,
        subtheme_title="Outro dia",
        target_rank=1,
    )
    db_session.add(other)
    db_session.commit()
    db_session.refresh(other)
    other_item = RankingItem(daily_challenge_id=other.id, rank=1, name="Outro item")
    db_session.add(other_item)
    db_session.commit()
    db_session.refresh(other_item)

    resp = client.post(
        f"/api/v1/daily/{sample_challenge.id}/guess",
        json={"item_id": other_item.id},
        headers=DEVICE_HEADERS,
    )
    assert resp.status_code == 400
