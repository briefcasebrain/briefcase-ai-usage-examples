"""
Basic tests for the Briefcase AI Telemetry SDK.
"""

import pytest
from briefcase_ai_telemetry import (
    EventBuilder,
    EventLevel,
    Session,
    TelemetryConfig,
    create_client,
    create_event,
)


def test_telemetry_config_creation():
    """Test creating a TelemetryConfig."""
    config = TelemetryConfig("test-api-key")
    assert config.api_key == "test-api-key"
    assert config.enabled is True


def test_telemetry_config_with_custom_settings():
    """Test creating a TelemetryConfig with custom settings."""
    config = TelemetryConfig("test-api-key")
    config.with_endpoint("https://custom.endpoint.com/telemetry")
    config.with_timeout_seconds(30)
    config.with_enabled(False)

    assert config.endpoint == "https://custom.endpoint.com/telemetry"
    assert config.enabled is False


def test_event_levels():
    """Test EventLevel creation."""
    debug = EventLevel.debug()
    info = EventLevel.info()
    warning = EventLevel.warning()
    error = EventLevel.error()
    critical = EventLevel.critical()

    assert str(debug) == "Debug"
    assert str(info) == "Info"
    assert str(warning) == "Warning"
    assert str(error) == "Error"
    assert str(critical) == "Critical"


def test_event_builder():
    """Test EventBuilder functionality."""
    builder = EventBuilder("test_event")
    builder.level(EventLevel.info())
    builder.message("Test message")
    builder.user_id("user123")
    builder.tag("component", "test")
    builder.custom_data("key", "value")
    builder.duration_ms(100)
    event = builder.build()

    assert event.name == "test_event"
    assert event.message == "Test message"
    assert event.duration_ms == 100
    assert event.id is not None
    assert event.timestamp is not None


def test_session():
    """Test Session functionality."""
    session = Session()
    session.with_user_id("user123")
    session.add_metadata("app", "test-app")

    assert session.id is not None
    assert session.started_at is not None
    assert session.user_id == "user123"


def test_create_client():
    """Test the create_client convenience function."""
    client = create_client(
        "test-api-key",
        timeout_seconds=30,
        batch_size=50,
        enabled=False
    )

    session = client.session()
    assert session.id is not None


def test_create_event():
    """Test the create_event convenience function."""
    event = create_event(
        "test_event",
        level=EventLevel.warning(),
        message="Test message",
        user_id="user123",
        tags={"component": "test", "version": "1.0"},
        custom_data={"metric": 42, "status": "success"},
        duration_ms=150
    )

    assert event.name == "test_event"
    assert event.message == "Test message"
    assert event.duration_ms == 150
    assert str(event.level) == "Warning"


def test_telemetry_client_basic():
    """Test basic TelemetryClient functionality."""
    config = TelemetryConfig("test-api-key")
    config.with_enabled(False)  # Disable to avoid actual network calls

    client = create_client("test-api-key", enabled=False)
    session = Session()
    session.with_user_id("test-user")
    client.with_session(session)

    # Test tracking an event
    event = create_event("test_event", level=EventLevel.info())
    client.track_event(event)

    # Test buffer size
    buffer_size = client.buffer_size()
    assert isinstance(buffer_size, int)

    # Test flush
    client.flush()


def test_error_event():
    """Test creating an error event."""
    builder = EventBuilder("error_event")
    builder.error("Something went wrong")
    event = builder.build()

    assert event.name == "error_event"
    assert event.error == "Something went wrong"
    assert str(event.level) == "Error"


@pytest.mark.asyncio
async def test_client_operations():
    """Test client operations that might be async in nature."""
    client = create_client("test-api-key", enabled=False)

    # Create and track multiple events
    events = [
        create_event(f"event_{i}", level=EventLevel.info())
        for i in range(5)
    ]

    for event in events:
        client.track_event(event)

    # Test flush
    client.flush()

    # Test buffer size after flush
    buffer_size = client.buffer_size()
    assert isinstance(buffer_size, int)