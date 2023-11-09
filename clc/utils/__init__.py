"""Utilities for charmed-openstack-upgrader."""


import os
from pathlib import Path

CLC_DATA = Path(os.getenv("CLC_DATA", "."))
