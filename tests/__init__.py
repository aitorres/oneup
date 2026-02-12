"""
Sets FORCE_COLOR so that termcolor always emits ANSI escape codes,
even when stdout is not a real terminal (e.g. during test capture).
"""

import os

os.environ["FORCE_COLOR"] = "1"
