"""API tests for POST /api/v1/analyze and GET /healthz."""
import pytest
import os
import tempfile
import shutil
from PIL import Image
import numpy as np
from unittest.mock import patch, MagicMock
from io import BytesIO

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, CLASS_LABELS


class TestApiV1Analyze:
    """Tests for POST /api/v1/analyze"""

    @pytest.fixture
    def client(self):
        app.config["TESTING"] = True
        app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
        with app.test_client() as client:
            yield client
        shutil.rmtree(app.config["UPLOAD_FOLDER"])

    @pytest.fixture
    def sample_image(self):
        img = Image.new("RGB", (200, 200), color="red")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return buf

    @pytest.fixture
    def small_image(self):
        """Image too small for QA (min 150 required)."""
        img = Image.new("RGB", (50, 50), color="blue")
        buf = BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        return buf

    @patch("app.model", MagicMock(predict=lambda x: np.array([[0.1, 0.2, 0.6, 0.1]])))
    def test_successful_analyze_response_shape(self, client, sample_image):
        """Test successful /api/v1/analyze returns expected response shape."""
        response = client.post(
            "/api/v1/analyze",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "request_id" in data
        assert "qa" in data
        assert "vision" in data
        assert "report" in data
        assert "artifacts" in data
        assert "latency_ms" in data
        assert data["qa"]["safe_to_infer"] is True
        assert data["vision"] is not None
        assert data["vision"]["label"] == "no_tumor"
        assert data["vision"]["confidence"] == 0.6
        assert "uploaded_image_url" in data["artifacts"]
        assert isinstance(data["latency_ms"], (int, float))

    @patch("app.model", MagicMock(predict=lambda x: np.array([[0.1, 0.2, 0.6, 0.1]])))
    def test_qa_fail_path_returns_vision_none(self, client, small_image):
        """Test QA fail path returns vision is None with HTTP 200."""
        response = client.post(
            "/api/v1/analyze",
            data={"image": (small_image, "tiny.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["qa"]["safe_to_infer"] is False
        assert data["vision"] is None
        assert "report" in data
        assert data["report"]["impression"] == "Inconclusive due to image quality"

    def test_missing_file_returns_400_standardized_error(self, client):
        """Test missing file returns 400 with standardized error JSON."""
        response = client.post("/api/v1/analyze")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "MISSING_FILE"

    def test_empty_filename_returns_400_standardized_error(self, client):
        """Test empty filename returns 400 with standardized error JSON."""
        response = client.post(
            "/api/v1/analyze",
            data={"image": (BytesIO(b""), "")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"]["code"] == "EMPTY_FILENAME"

    def test_bad_extension_returns_400_standardized_error(self, client):
        """Test bad extension returns 400 with standardized error JSON."""
        response = client.post(
            "/api/v1/analyze",
            data={"image": (BytesIO(b"fake image"), "test.gif")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"]["code"] == "UNSUPPORTED_EXTENSION"

    @patch("app.model", None)
    def test_model_unavailable_returns_503(self, client, sample_image):
        """Test model unavailable returns 503 with MODEL_UNAVAILABLE."""
        response = client.post(
            "/api/v1/analyze",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 503
        data = response.get_json()
        assert "error" in data
        assert data["error"]["code"] == "MODEL_UNAVAILABLE"


class TestHealthz:
    """Tests for GET /healthz"""

    @pytest.fixture
    def client(self):
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_healthz_returns_expected_fields(self, client):
        """Test /healthz returns ok, model_loaded, model_path."""
        response = client.get("/healthz")
        data = response.get_json()
        assert "ok" in data
        assert "model_loaded" in data
        assert "model_path" in data
        assert isinstance(data["ok"], bool)
        assert isinstance(data["model_loaded"], bool)
        assert isinstance(data["model_path"], str)

    def test_healthz_200_when_healthy(self, client):
        """Test /healthz returns 200 when model is loaded."""
        import app as app_module
        if app_module.model is not None:
            response = client.get("/healthz")
            assert response.status_code == 200
            assert response.get_json()["ok"] is True

    def test_healthz_500_when_model_unavailable(self, client):
        """Test /healthz returns 500 when model is unavailable."""
        with patch("app.model", None):
            response = client.get("/healthz")
            assert response.status_code == 500
            assert response.get_json()["ok"] is False
            assert response.get_json()["model_loaded"] is False
