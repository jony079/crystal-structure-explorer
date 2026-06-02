# config.py – centralized configuration for Crystal Visualizer

"""Application‑wide constants, theme settings, default parameters, and asset helpers.

All modules import this singleton to guarantee a single source of truth.
"""

import pathlib
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = pathlib.Path(__file__).parent.resolve()
STYLE_CSS_PATH = BASE_DIR / "style.css"  # Fixed: look directly in the root directory
ASSETS_DIR = BASE_DIR / "assets"

# ---------------------------------------------------------------------------
# Theme (dark mode + glass‑morphism)
# ---------------------------------------------------------------------------
PRIMARY_COLOR = "hsl(210, 60%, 55%)"   # deep blue‑gray
ACCENT_COLOR = "hsl(28, 95%, 52%)"     # vivid orange for KPI values
BACKGROUND_COLOR = "hsl(220, 15%, 10%)"  # very dark background
CARD_BG = "rgba(255, 255, 255, 0.08)"   # translucent glass card

# Streamlit page configuration (used in main.py)
APP_TITLE = "Crystal Structure Explorer"
PAGE_ICON = "🧊"
THEME = {
    "primaryColor": PRIMARY_COLOR,
    "backgroundColor": BACKGROUND_COLOR,
    "secondaryBackgroundColor": "hsl(220, 20%, 15%)",
    "textColor": "#fafafa",
    "font": "sans serif",
}

# ---------------------------------------------------------------------------
# Supported lattice types and human‑readable names
# ---------------------------------------------------------------------------
LATTICE_TYPES = {
    "cubic": "Cubic",
    "hcp": "Hexagonal Close‑Packed",
    "fcc": "Face‑Centered Cubic",
    "tetragonal": "Tetragonal",
    "orthorhombic": "Orthorhombic",
    "monoclinic": "Monoclinic",
    "triclinic": "Triclinic",
}

# ---------------------------------------------------------------------------
# Default lattice parameters (Å, degrees)
# ---------------------------------------------------------------------------
DEFAULT_PARAMS = {
    "a": 5.0,
    "b": 5.0,
    "c": 5.0,
    "alpha": 90.0,
    "beta": 90.0,
    "gamma": 90.0,
    "lattice_type": "cubic",
}

# ---------------------------------------------------------------------------
# Cache settings
# ---------------------------------------------------------------------------
CACHE_MAXSIZE = 128  # for LRU caches inside cache.py

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def load_css() -> str:
    """Read the CSS stylesheet and return its content."""
    if not STYLE_CSS_PATH.is_file():
        raise FileNotFoundError(f"CSS file not found at {STYLE_CSS_PATH}")
    return STYLE_CSS_PATH.read_text(encoding="utf-8")


def asset_path(relative_path: str) -> str:
    """Resolve a path inside the assets folder."""
    return str(ASSETS_DIR / relative_path)
