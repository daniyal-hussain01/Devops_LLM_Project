"""Unit tests for the DevOps LLM application."""

import json
import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import TestingConfig  # noqa: E402
from app.database import get_all_prompts, get_prompt_by_id, init_db  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(config=TestingConfig)
    yield app

    # Cleanup test database
    if os.path.exists("test_prompts.db"):
        os.remove("test_prompts.db")


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert "status" in data
        assert "checks" in data
        assert "version" in data

    def test_health_checks_database(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["checks"]["database"] == "connected"


class TestPromptsAPI:
    """Tests for prompt-related endpoints."""

    def test_list_prompts_returns_200(self, client):
        response = client.get("/api/prompts")
        assert response.status_code == 200

    def test_list_prompts_returns_data(self, client):
        response = client.get("/api/prompts")
        data = json.loads(response.data)
        assert data["status"] == "success"
        assert data["count"] > 0
        assert isinstance(data["data"], list)

    def test_get_prompt_valid_id(self, client):
        response = client.get("/api/prompts/1")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"

    def test_get_prompt_invalid_id(self, client):
        response = client.get("/api/prompts/9999")
        assert response.status_code == 404

    def test_list_categories(self, client):
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data["data"], list)


class TestGenerateEndpoint:
    """Tests for the /api/generate endpoint."""

    def test_generate_requires_json(self, client):
        response = client.post("/api/generate", data="not json")
        assert response.status_code == 400

    def test_generate_requires_id(self, client):
        response = client.post(
            "/api/generate",
            data=json.dumps({}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_rejects_invalid_id(self, client):
        response = client.post(
            "/api/generate",
            data=json.dumps({"id": "abc"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_generate_returns_404_for_missing_prompt(self, client):
        response = client.post(
            "/api/generate",
            data=json.dumps({"id": 9999}),
            content_type="application/json",
        )
        assert response.status_code == 404


class TestIndexPage:
    """Tests for the main page."""

    def test_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_contains_html(self, client):
        response = client.get("/")
        assert b"DevOps LLM" in response.data


class TestDatabase:
    """Tests for database operations."""

    def test_get_all_prompts_returns_list(self):
        init_db()
        prompts = get_all_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_get_prompt_by_valid_id(self):
        init_db()
        prompt = get_prompt_by_id(1)
        assert prompt is not None
        assert isinstance(prompt, str)

    def test_get_prompt_by_invalid_id(self):
        init_db()
        prompt = get_prompt_by_id(9999)
        assert prompt is None


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_route(self, client):
        response = client.get("/nonexistent")
        assert response.status_code == 404
