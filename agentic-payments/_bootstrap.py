"""
Import-time shim for running the walkthrough against a source checkout.

The bitemporal / routing / compliance primitives used in this walkthrough
are pure Python and do not touch ``briefcase._native``. However, the
top-level ``briefcase/__init__.py`` imports ``_native`` eagerly, so a
source checkout without the compiled wheel raises ModuleNotFoundError
the moment anything under ``briefcase`` is imported.

Importing this module before anything from ``briefcase`` installs a
minimal stub for ``briefcase._native`` sufficient to make the package
import cleanly. If a real wheel is installed, the stub is never needed
because ``briefcase._native`` will already be in ``sys.modules``.

Production users install ``briefcase-ai`` from PyPI and never touch this
file.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock


def _install_native_stub() -> None:
    if "briefcase._native" in sys.modules:
        return
    try:
        import briefcase._native  # noqa: F401
        return
    except ModuleNotFoundError:
        pass

    stub = MagicMock()
    stub.__version__ = "3.2.0-walkthrough-stub"
    stub.DecisionSnapshot = MagicMock
    stub.ExecutionContext = MagicMock
    stub.HardwareMetadata = MagicMock
    stub.Input = MagicMock
    stub.ModelParameters = MagicMock
    stub.Output = MagicMock
    stub.Snapshot = MagicMock
    stub.SnapshotQuery = MagicMock
    stub.init = MagicMock()
    stub.init_with_config = MagicMock()
    stub.is_initialized = MagicMock(return_value=True)
    sys.modules["briefcase._native"] = stub


_install_native_stub()
