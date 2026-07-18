"""The web dashboard (feature 015, ROADMAP B7) — one face for any brain.

A pure consumer of the B6 surface: the documented ``pra.v1`` subjects, the
three control commands, and discovery — through the existing transport seam,
nothing else. ``DashboardModel`` turns received payloads into per-run state;
``start_dashboard`` serves the page and the JSON endpoints; ``pra-dash`` is
the console entry point.
"""

from pra.dash.model import DashboardModel, RunModel
from pra.dash.server import start_dashboard

__all__ = ["DashboardModel", "RunModel", "start_dashboard"]
