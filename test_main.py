"""
Test suite for the KittenConnect API.

Covers authentication, input validation, protected routes, and CRUD flows.
"""
import auth


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------
def test_signup_success(client):
    resp = client.post("/signup", json={
        "name": "Grace",
        "email": "grace@example.com",
        "password": "hunter2",
        "location": "Nairobi",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "grace@example.com"
    assert body["name"] == "Grace"
    assert "id" in body


def test_signup_never_returns_password(client):
    resp = client.post("/signup", json={
        "name": "Grace",
        "email": "grace2@example.com",
        "password": "hunter2",
    })
    # The response model must not leak the password or its hash.
    assert "password" not in resp.json()
    assert "hashed_password" not in resp.json()


def test_signup_duplicate_email_rejected(client, signed_up_user):
    resp = client.post("/signup", json={
        "name": "Impostor",
        "email": signed_up_user["email"],
        "password": "different",
    })
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"


def test_signup_invalid_email_rejected(client):
    resp = client.post("/signup", json={
        "name": "Bad",
        "email": "not-an-email",
        "password": "pw",
    })
    assert resp.status_code == 422  # Pydantic validation error


def test_signup_missing_required_field_rejected(client):
    resp = client.post("/signup", json={"email": "x@example.com", "password": "pw"})
    assert resp.status_code == 422  # name is required


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def test_password_is_hashed_not_plaintext():
    hashed = auth.hash_password("plaintext-pw")
    assert hashed != "plaintext-pw"
    assert auth.verify_password("plaintext-pw", hashed) is True
    assert auth.verify_password("wrong-pw", hashed) is False


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def test_login_success_returns_bearer_token(client, signed_up_user):
    resp = client.post("/login", json={
        "email": signed_up_user["email"],
        "password": signed_up_user["password"],
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_rejected(client, signed_up_user):
    resp = client.post("/login", json={
        "email": signed_up_user["email"],
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_login_unknown_email_rejected(client):
    resp = client.post("/login", json={
        "email": "nobody@example.com",
        "password": "whatever",
    })
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Protected route: /me
# ---------------------------------------------------------------------------
def test_me_requires_authentication(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    resp = client.get("/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "ada@example.com"


def test_me_rejects_garbage_token(client):
    resp = client.get("/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Kittens
# ---------------------------------------------------------------------------
def test_create_kitten_requires_authentication(client):
    resp = client.post("/kittens", json={"name": "Mittens", "location": "Addis"})
    assert resp.status_code == 401


def test_create_kitten_success(client, auth_headers):
    resp = client.post("/kittens", json={
        "name": "Mittens",
        "age": 2,
        "location": "Addis Ababa",
        "notes": "Very fluffy",
    }, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Mittens"
    assert body["status"] == "available"      # default applied server-side
    assert body["owner_id"] == 1              # linked to the creating user


def test_create_kitten_missing_location_rejected(client, auth_headers):
    resp = client.post("/kittens", json={"name": "Mittens"}, headers=auth_headers)
    assert resp.status_code == 422  # location is required


def test_kitten_list_empty_by_default(client):
    resp = client.get("/kitten_list")
    assert resp.status_code == 200
    assert resp.json() == []


def test_kitten_list_returns_created_kittens(client, auth_headers):
    client.post("/kittens", json={"name": "A", "location": "X"}, headers=auth_headers)
    client.post("/kittens", json={"name": "B", "location": "Y"}, headers=auth_headers)
    resp = client.get("/kitten_list")
    assert resp.status_code == 200
    names = {k["name"] for k in resp.json()}
    assert names == {"A", "B"}


# ---------------------------------------------------------------------------
# Get a single kitten
# ---------------------------------------------------------------------------
def test_get_one_kitten_success(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "Solo", "location": "X"}, headers=auth_headers
    ).json()
    resp = client.get(f"/kittens/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Solo"


def test_get_one_kitten_not_found(client):
    resp = client.get("/kittens/999")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Update a listing (ownership enforced)
# ---------------------------------------------------------------------------
def test_update_own_kitten_success(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "Old", "location": "X"}, headers=auth_headers
    ).json()
    resp = client.put(
        f"/kittens/{created['id']}",
        json={"name": "New", "status": "adopted"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "New"
    assert body["status"] == "adopted"
    assert body["location"] == "X"  # untouched fields preserved


def test_update_kitten_requires_authentication(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "X", "location": "X"}, headers=auth_headers
    ).json()
    resp = client.put(f"/kittens/{created['id']}", json={"name": "Nope"})
    assert resp.status_code == 401


def test_cannot_update_someone_elses_kitten(client, auth_headers):
    # user 1 creates a kitten
    created = client.post(
        "/kittens", json={"name": "Mine", "location": "X"}, headers=auth_headers
    ).json()
    # user 2 signs up and logs in
    client.post("/signup", json={
        "name": "Mallory", "email": "mal@example.com", "password": "pw",
    })
    token = client.post(
        "/login", json={"email": "mal@example.com", "password": "pw"}
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}
    # user 2 tries to edit user 1's kitten -> forbidden
    resp = client.put(f"/kittens/{created['id']}", json={"name": "Hijacked"}, headers=other)
    assert resp.status_code == 403


def test_update_nonexistent_kitten_not_found(client, auth_headers):
    resp = client.put("/kittens/999", json={"name": "Ghost"}, headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Delete a listing (ownership enforced)
# ---------------------------------------------------------------------------
def test_delete_own_kitten_success(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "Bye", "location": "X"}, headers=auth_headers
    ).json()
    resp = client.delete(f"/kittens/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
    # confirm it's really gone
    assert client.get(f"/kittens/{created['id']}").status_code == 404


def test_delete_kitten_requires_authentication(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "X", "location": "X"}, headers=auth_headers
    ).json()
    resp = client.delete(f"/kittens/{created['id']}")
    assert resp.status_code == 401


def test_cannot_delete_someone_elses_kitten(client, auth_headers):
    created = client.post(
        "/kittens", json={"name": "Mine", "location": "X"}, headers=auth_headers
    ).json()
    client.post("/signup", json={
        "name": "Mallory", "email": "mal2@example.com", "password": "pw",
    })
    token = client.post(
        "/login", json={"email": "mal2@example.com", "password": "pw"}
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}
    resp = client.delete(f"/kittens/{created['id']}", headers=other)
    assert resp.status_code == 403
    # and it should still exist
    assert client.get(f"/kittens/{created['id']}").status_code == 200


def test_delete_nonexistent_kitten_not_found(client, auth_headers):
    resp = client.delete("/kittens/999", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Photo upload
# ---------------------------------------------------------------------------
# 1x1 transparent PNG
_PNG_BYTES = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000d49444154789c63f8cfc0f01f0004fb03fdd9c3a7b70000000049454e44ae426082"
)


def test_upload_requires_authentication(client):
    resp = client.post("/upload", files={"file": ("cat.png", _PNG_BYTES, "image/png")})
    assert resp.status_code == 401


def test_upload_rejects_non_image(client, auth_headers):
    resp = client.post(
        "/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 400


def test_upload_image_returns_url(client, auth_headers):
    resp = client.post(
        "/upload",
        files={"file": ("cat.png", _PNG_BYTES, "image/png")},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    url = resp.json()["url"]
    assert "/uploads/" in url
    assert url.endswith(".png")
