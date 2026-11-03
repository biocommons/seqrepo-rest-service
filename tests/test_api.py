"""End-to-end tests of the seqrepo and refget APIs against the test seqrepo"""

import pathlib

import pytest
from biocommons.seqrepo import SeqRepo

from seqrepo_rest_service.cli import create_app

SEQREPO_DIR = pathlib.Path(__file__).parent / "data" / "seqrepo" / "master"
SEQ_ID = "IIXILYBQCpHdC4qpI3sOQ_HAeAm9bmeF"  # phiX174 (seqrepo internal id)
GA4GH_ID = f"ga4gh:SQ.{SEQ_ID}"


@pytest.fixture(scope="module")
def client():
    with create_app(SEQREPO_DIR).test_client() as c:
        yield c


@pytest.fixture(scope="module")
def sr():
    return SeqRepo(SEQREPO_DIR.as_posix())


def test_root_redirects(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "/seqrepo/1/ui/"


def test_seqrepo_ping(client):
    resp = client.get("/seqrepo/1/ping")
    assert resp.status_code == 200
    assert resp.json()["dependencies"]["seqrepo"]["root"] == str(SEQREPO_DIR)


def test_refget_service_info(client):
    resp = client.get("/refget/1/sequence/service-info")
    assert resp.status_code == 200
    assert resp.json()["x-config"]["seqrepo"]["root"] == str(SEQREPO_DIR)


def test_refget_sequence(client, sr):
    resp = client.get(f"/refget/1/sequence/{GA4GH_ID}", params={"start": 0, "end": 10})
    assert resp.status_code == 200
    assert resp.text == sr.sequences.fetch(SEQ_ID, 0, 10)


def test_refget_sequence_not_found(client):
    resp = client.get("/refget/1/sequence/ga4gh:SQ.bogus")
    assert resp.status_code == 404


def test_refget_metadata(client, sr):
    resp = client.get(f"/refget/1/sequence/{GA4GH_ID}/metadata")
    assert resp.status_code == 200
    assert resp.json()["metadata"]["length"] == len(sr.sequences.fetch(SEQ_ID))


@pytest.mark.parametrize(
    ("range_header", "start", "end"),
    [
        ("bytes=0-9", 0, 10),
        ("bytes=10-10", 10, 11),
        ("bytes=5380-5999", 5380, 5386),  # past end: truncated to sequence length
    ],
)
def test_refget_sequence_range(client, sr, range_header, start, end):
    resp = client.get(f"/refget/1/sequence/{GA4GH_ID}", headers={"Range": range_header})
    assert resp.status_code == 206
    assert resp.text == sr.sequences.fetch(SEQ_ID, start, end)


@pytest.mark.parametrize(
    ("range_header", "params", "status"),
    [
        ("bytes=5-4", {}, 416),  # first byte > last byte
        ("bytes=5386-5390", {}, 416),  # starts at/after sequence end
        ("bytes=0-", {}, 400),  # unsupported/malformed
        ("bytes=0-9", {"start": 0}, 400),  # conflicts with query params
    ],
)
def test_refget_sequence_range_errors(client, range_header, params, status):
    resp = client.get(
        f"/refget/1/sequence/{GA4GH_ID}", headers={"Range": range_header}, params=params
    )
    assert resp.status_code == status
