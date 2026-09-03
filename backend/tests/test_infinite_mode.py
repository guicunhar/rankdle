"""Modo infinito: chuta sem limite de vidas até cravar a posição ou desistir."""

DEVICE_HEADERS = {"X-Device-Id": "infinite-device"}
INF = {"mode": "infinite"}


def _item_id_for_rank(client, challenge_id, rank):
    resp = client.get(
        f"/api/v1/daily/{challenge_id}/search", params={"q": f"Item {rank}", "limit": 50}
    )
    for item in resp.json():
        if item["name"] == f"Item {rank}":
            return item["id"]
    raise AssertionError(f"rank {rank} not found in search results")


def test_infinite_mode_ignores_life_limit(client, sample_challenge):
    cid = sample_challenge.id
    resp = client.get(
        "/api/v1/daily", params={"theme": "musica", "date": "2026-08-26", **INF}, headers=DEVICE_HEADERS
    )
    assert resp.status_code == 200
    assert resp.json()["mode"] == "infinite"

    # oito palpites errados (bem além das 5 vidas do modo normal) e o jogo segue vivo
    for rank in range(1, 9):
        item_id = _item_id_for_rank(client, cid, rank)
        resp = client.post(
            f"/api/v1/daily/{cid}/guess", params=INF, json={"item_id": item_id}, headers=DEVICE_HEADERS
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["is_over"] is False
    assert body["attempts_used"] == 8

    # cravar a posição encerra o jogo
    item_id = _item_id_for_rank(client, cid, 34)
    resp = client.post(
        f"/api/v1/daily/{cid}/guess", params=INF, json={"item_id": item_id}, headers=DEVICE_HEADERS
    )
    body = resp.json()
    assert body["exact_hit"] is True
    assert body["is_over"] is True
    assert body["best_score"] == 100


def test_infinite_mode_give_up_reveals_answer(client, sample_challenge):
    cid = sample_challenge.id
    item_id = _item_id_for_rank(client, cid, 30)  # rank 30 vs 34 -> score 96
    client.post(
        f"/api/v1/daily/{cid}/guess", params=INF, json={"item_id": item_id}, headers=DEVICE_HEADERS
    )

    resp = client.post(f"/api/v1/daily/{cid}/giveup", params=INF, headers=DEVICE_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["gave_up"] is True
    assert body["is_over"] is True

    resp = client.get(f"/api/v1/daily/{cid}/result", params=INF, headers=DEVICE_HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "infinite"
    assert data["answer"]["name"] == "Item 34"
    assert data["player_gave_up"] is True
    assert data["player_attempts"] == 1
    assert data["player_best_score"] == 96


def test_giveup_rejected_for_lives_mode(client, sample_challenge):
    resp = client.post(f"/api/v1/daily/{sample_challenge.id}/giveup", headers=DEVICE_HEADERS)
    assert resp.status_code == 400


def test_infinite_attempts_excluded_from_community_stats(client, sample_challenge):
    cid = sample_challenge.id

    # jogador A: crava no modo infinito depois de muitos palpites
    for rank in (1, 2, 3, 4, 5, 6, 7, 34):
        item_id = _item_id_for_rank(client, cid, rank)
        client.post(
            f"/api/v1/daily/{cid}/guess",
            params=INF,
            json={"item_id": item_id},
            headers={"X-Device-Id": "player-a"},
        )

    # jogador B: joga o modo normal e erra tudo (best_score baixo)
    for rank in (1, 2, 3, 4, 5):
        item_id = _item_id_for_rank(client, cid, rank)
        client.post(
            f"/api/v1/daily/{cid}/guess",
            json={"item_id": item_id},
            headers={"X-Device-Id": "player-b"},
        )

    resp = client.get(
        f"/api/v1/daily/{cid}/result", headers={"X-Device-Id": "player-b"}
    )
    data = resp.json()
    # só o jogador B (modo 5 vidas) entra na contagem da comunidade
    assert data["players_count"] == 1
    assert data["exact_hit_count"] == 0


def test_infinite_mode_continues_from_lives_game(client, sample_challenge):
    cid = sample_challenge.id

    # o jogador esgota as 5 vidas sem cravar (ranks 12, 30, 1, 2, 3)
    for rank in (12, 30, 1, 2, 3):
        item_id = _item_id_for_rank(client, cid, rank)
        client.post(
            f"/api/v1/daily/{cid}/guess", json={"item_id": item_id}, headers=DEVICE_HEADERS
        )

    # abrir o modo infinito: começa como continuação, com os 5 palpites e a melhor
    # pontuação já preenchidos, mas ainda em jogo
    resp = client.get(
        "/api/v1/daily",
        params={"theme": "musica", "date": "2026-08-26", **INF},
        headers=DEVICE_HEADERS,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_over"] is False
    assert data["attempts_used"] == 5
    assert len(data["guesses"]) == 5
    assert data["best_score"] == 96  # rank 30 vs 34

    # e o jogador segue tentando a partir daí até cravar
    item_id = _item_id_for_rank(client, cid, 34)
    resp = client.post(
        f"/api/v1/daily/{cid}/guess", params=INF, json={"item_id": item_id}, headers=DEVICE_HEADERS
    )
    body = resp.json()
    assert body["is_over"] is True
    assert body["exact_hit"] is True
    assert body["attempts_used"] == 6


def test_infinite_mode_starts_empty_without_a_lives_game(client, sample_challenge):
    # sem ter jogado o modo 5 vidas, o infinito começa do zero
    resp = client.get(
        "/api/v1/daily",
        params={"theme": "musica", "date": "2026-08-26", **INF},
        headers={"X-Device-Id": "never-played-lives"},
    )
    assert resp.status_code == 200
    assert resp.json()["attempts_used"] == 0
    assert resp.json()["is_over"] is False
