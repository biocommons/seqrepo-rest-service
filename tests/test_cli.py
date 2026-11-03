import pathlib

from seqrepo_rest_service.cli import DEFAULT_SEQREPO_INSTANCE_DIR, _parse_opts


def test_instance_dir_defaults_to_latest(monkeypatch):
    monkeypatch.setattr("sys.argv", ["seqrepo-rest-service"])
    assert _parse_opts().SEQREPO_INSTANCE_DIR == DEFAULT_SEQREPO_INSTANCE_DIR
    assert DEFAULT_SEQREPO_INSTANCE_DIR.name == "latest"


def test_instance_dir_explicit(monkeypatch):
    instance_dir = pathlib.Path("/data/seqrepo/2024-12-20")
    monkeypatch.setattr("sys.argv", ["seqrepo-rest-service", str(instance_dir)])
    assert instance_dir == _parse_opts().SEQREPO_INSTANCE_DIR
