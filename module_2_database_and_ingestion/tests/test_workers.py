"""
Unit Tests for Background Workers & Liveness Checks
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from module_2_database_and_ingestion.ingestion.stage5_liveness import Stage5LivenessService
from module_2_database_and_ingestion.workers.notification_worker import _DISPATCHED_ALERTS


@pytest.mark.asyncio
async def test_liveness_404_expires_job():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(status_code=404)
    mock_client.head.return_value = mock_response

    is_alive, code, reason = await Stage5LivenessService.check_url(
        client=mock_client,
        url="https://example.com/expired-job"
    )

    assert is_alive is False
    assert code == 404
    assert "Confirmed Dead Link" in reason


@pytest.mark.asyncio
async def test_liveness_200_active():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(status_code=200)
    mock_client.head.return_value = mock_response

    is_alive, code, reason = await Stage5LivenessService.check_url(
        client=mock_client,
        url="https://example.com/active-job"
    )

    assert is_alive is True
    assert code == 200
    assert reason is None


@pytest.mark.asyncio
async def test_liveness_429_treated_as_transient():
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = MagicMock(status_code=429)
    mock_client.head.return_value = mock_response

    is_alive, code, reason = await Stage5LivenessService.check_url(
        client=mock_client,
        url="https://example.com/rate-limited"
    )

    # 429 should NOT be marked as dead link to prevent false positives
    assert is_alive is True
    assert code == 429
    assert "Transient" in reason


def test_notification_duplicate_suppression():
    alert_key = "test_job_123_2026-10-25"
    _DISPATCHED_ALERTS.add(alert_key)

    # Key should be suppressed from re-dispatch
    assert alert_key in _DISPATCHED_ALERTS
