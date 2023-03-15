"""Application Configurations."""

from pathlib import Path

BASEDIR = Path(__file__).parent.parent

BACKEND = BASEDIR.joinpath("backend")
DATABASE = BACKEND.joinpath("database")
