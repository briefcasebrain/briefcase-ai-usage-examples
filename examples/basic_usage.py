#!/usr/bin/env python3
"""
Basic usage example for Briefcase AI Telemetry SDK.

This example demonstrates how to:
- Create a telemetry client
- Track various types of events
- Use different event levels
- Add metadata and custom data
"""

import time
from briefcase_ai_telemetry import (
    create_client,
    create_event,
    EventLevel,
    EventBuilder,
    Session,
)


def main():
    # Create a client with your API key (disabled for demo)
    client = create_client("demo-api-key", enabled=False)

    # Start background flushing (optional)
    client.start_background_flush()

    # Create a custom session
    session = Session()
    session.with_user_id("demo-user-123")
    session.add_metadata("app_version", "1.0.0")
    session.add_metadata("environment", "demo")

    client.with_session(session)

    print("🚀 Briefcase AI Telemetry SDK Demo")
    print("=" * 40)

    # Example 1: Simple event tracking
    print("\n1. Tracking a simple event...")
    simple_event = create_event(
        name="app_started",
        level=EventLevel.info(),
        message="Application started successfully",
    )
    client.track_event(simple_event)
    print(f"   ✓ Tracked event: {simple_event.name}")

    # Example 2: Event with metadata and tags
    print("\n2. Tracking event with metadata...")
    user_event = create_event(
        name="user_login",
        level=EventLevel.info(),
        message="User logged in",
        user_id="demo-user-123",
        tags={"component": "auth", "method": "oauth"},
        custom_data={
            "login_time": time.time(),
            "user_agent": "Demo Browser 1.0",
            "ip_address": "127.0.0.1",
        },
    )
    client.track_event(user_event)
    print(f"   ✓ Tracked event: {user_event.name}")

    # Example 3: Performance monitoring
    print("\n3. Performance monitoring...")
    start_time = time.time()

    # Simulate some work
    time.sleep(0.1)

    duration_ms = int((time.time() - start_time) * 1000)

    perf_builder = EventBuilder("data_processing")
    perf_builder.level(EventLevel.info())
    perf_builder.message("Data processing completed")
    perf_builder.user_id("demo-user-123")
    perf_builder.tag("operation", "batch_process")
    perf_builder.tag("dataset", "user_interactions")
    perf_builder.custom_data("records_processed", "1000")
    perf_builder.custom_data("processing_time_ms", str(duration_ms))
    perf_builder.duration_ms(duration_ms)
    perf_event = perf_builder.build()

    client.track_event(perf_event)
    print(f"   ✓ Tracked performance event: {perf_event.name} ({duration_ms}ms)")

    # Example 4: Error tracking
    print("\n4. Error tracking...")
    try:
        # Simulate an error
        raise ValueError("This is a demo error")
    except Exception as e:
        error_builder = EventBuilder("operation_failed")
        error_builder.level(EventLevel.error())
        error_builder.message("Demo operation failed")
        error_builder.user_id("demo-user-123")
        error_builder.tag("component", "demo")
        error_builder.tag("operation", "example_task")
        error_builder.custom_data("error_type", type(e).__name__)
        error_builder.error(str(e))
        error_event = error_builder.build()
        client.track_event(error_event)
        print(f"   ✓ Tracked error event: {error_event.name}")

    # Example 5: Different event levels
    print("\n5. Different event levels...")
    levels = [
        (EventLevel.debug(), "debug_info", "Debug information"),
        (EventLevel.info(), "info_message", "Information message"),
        (EventLevel.warning(), "warning_alert", "Warning alert"),
        (EventLevel.critical(), "critical_issue", "Critical issue"),
    ]

    for level, name, message in levels:
        event = create_event(name=name, level=level, message=message)
        client.track_event(event)
        print(f"   ✓ Tracked {str(level).lower()} event: {name}")

    # Example 6: Batch operations
    print("\n6. Batch operations...")
    batch_events = []
    for i in range(5):
        event = create_event(
            name=f"batch_operation_{i}",
            level=EventLevel.info(),
            message=f"Batch operation {i} completed",
            tags={"batch_id": "demo-batch-001", "operation_index": str(i)},
            custom_data={"items_processed": str((i + 1) * 10)},
        )
        batch_events.append(event)
        client.track_event(event)

    print(f"   ✓ Tracked {len(batch_events)} batch events")

    # Flush all events
    print("\n7. Flushing events...")
    client.flush()
    buffer_size = client.buffer_size()
    print(f"   ✓ Flushed events, buffer size: {buffer_size}")

    print("\n" + "=" * 40)
    print("✨ Demo completed successfully!")
    print(
        "💡 In production, set enabled=True and provide a real API key to send events."
    )


if __name__ == "__main__":
    main()