import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from apps.accounts.models import User
from apps.subscriptions.models import Plan, Subscription

@pytest.fixture
def api_client(): return APIClient()

@pytest.fixture
def free_user(db):
    user = User.objects.create_user(email="test@test.com",
                                    username="tester", password="pass1234")
    return user

@pytest.fixture
def pro_user(db, free_user):
    plan = Plan.objects.create(name="Pro", limit_type="unlimited",
                                max_file_size=500*1024*1024,
                                storage_quota=50*1024*1024*1024)
    Subscription.objects.create(user=free_user, plan=plan, status="active")
    return free_user


@pytest.mark.django_db
def test_upload_success(api_client, pro_user):
    api_client.force_authenticate(user=pro_user)
    file = SimpleUploadedFile("hello.txt", b"hello world", content_type="text/plain")
    resp = api_client.post("/api/files/upload/", {"file": file}, format="multipart")
    assert resp.status_code == 201
    assert resp.data["original_name"] == "hello.txt"


@pytest.mark.django_db
def test_upload_free_limit(api_client, free_user, db):
    Plan.objects.create(name="Free", limit_type="count", upload_limit=2)
    # simulate 2 existing uploads
    from apps.files.models import File
    for _ in range(2):
        File.objects.create(owner=free_user, original_name="f.txt",
                            size=100, mime_type="text/plain",
                            slug=f"sl{_}", status="ready",
                            file="files/fake.txt")
    api_client.force_authenticate(user=free_user)
    file = SimpleUploadedFile("new.txt", b"data", content_type="text/plain")
    resp = api_client.post("/api/files/upload/", {"file": file}, format="multipart")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_search_returns_results(api_client, pro_user):
    api_client.force_authenticate(user=pro_user)
    resp = api_client.get("/api/search/?q=report")
    assert resp.status_code == 200
    assert "results" in resp.data