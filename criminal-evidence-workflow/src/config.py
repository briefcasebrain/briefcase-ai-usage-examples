"""Centralized Briefcase AI SDK configuration.

Single initialization point for the SDK runtime, storage backend, and event bus.
All modules import from here instead of creating their own instances.
"""

import briefcase
from briefcase.storage import SqliteBackend
from briefcase.config import setup
from briefcase.events.types import BriefcaseEvent


class InMemoryEventBus:
    """Collects events in memory for offline operation."""

    def __init__(self):
        self.events = []

    def publish(self, event: BriefcaseEvent):
        self.events.append(event)

    def clear(self):
        self.events.clear()


# Initialize the Briefcase AI runtime (once)
if not briefcase.is_initialized():
    briefcase.init()

storage = SqliteBackend("decisions.db")
event_bus = InMemoryEventBus()
config = setup(storage=storage, event_bus=event_bus)
