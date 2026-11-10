"""Rockyx Auto-Clipper — free, local, no watermark, no minute limits.

Combines the best free open-source clipping tools (see CREDITS.md):
OpenClip Studio (foundation, MIT) + AutoClip (MIT) + SupoClip (AGPL,
ideas only) + Video Wizard (MIT) + OpenShorts (MIT), plus paid tools'
features re-implemented with open components.
"""
from .config import VERSION

__version__ = VERSION
__all__ = ["__version__"]
