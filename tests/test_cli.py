import os
import tempfile

from sirocco.cli import load_config


def test_load_config_reads_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("location: London\nlat: 51.5\n")
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg["location"] == "London"
        assert cfg["lat"] == 51.5
    finally:
        os.unlink(path)


def test_load_config_empty_file_returns_empty_dict():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        path = f.name
    try:
        cfg = load_config(path)
        assert cfg == {}
    finally:
        os.unlink(path)
