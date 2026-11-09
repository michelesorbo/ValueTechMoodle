import io
import zipfile
from pathlib import Path

import pytest

from app.models.scorm import ScormVersion
from app.services.scorm.manifest import ManifestError, parse_manifest
from app.services.scorm.storage import PackageError, extract_package
from tests.scorm_factory import MANIFEST_12, MANIFEST_2004, build_zip, scorm12_zip


def test_parse_scorm12() -> None:
    m = parse_manifest(MANIFEST_12.encode())
    assert m.version is ScormVersion.SCORM_12
    assert m.launch_path == "index.html"
    assert m.title == "Corso Demo SCORM 1.2"


def test_parse_scorm2004_nested_item_base_and_parameters() -> None:
    m = parse_manifest(MANIFEST_2004.encode())
    assert m.version is ScormVersion.SCORM_2004
    assert m.launch_path == "content/launch.html?lang=it"
    assert m.resources[0]["scorm_type"] == "sco"


def test_invalid_xml() -> None:
    with pytest.raises(ManifestError):
        parse_manifest(b"<manifest><broken>")


def test_xml_entity_expansion_is_blocked() -> None:
    bomb = b"""<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol">]>
    <manifest>&lol;</manifest>"""
    with pytest.raises(Exception):  # noqa: B017 - defusedxml solleva EntitiesForbidden
        parse_manifest(bomb)


def test_extract_valid_package(tmp_path: Path) -> None:
    pkg_id, manifest = extract_package(io.BytesIO(scorm12_zip()), tmp_path)
    assert (tmp_path / str(pkg_id) / "index.html").is_file()
    assert manifest.version is ScormVersion.SCORM_12


def test_extract_rejects_zip_slip(tmp_path: Path) -> None:
    data = build_zip(
        {"imsmanifest.xml": MANIFEST_12, "index.html": "ok", "../../evil.sh": "rm -rf /"}
    )
    with pytest.raises(PackageError, match="Percorso non consentito"):
        extract_package(io.BytesIO(data), tmp_path)
    assert not any(tmp_path.iterdir()), "la cartella parziale deve essere rimossa"


def test_extract_requires_manifest(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match=r"imsmanifest\.xml mancante"):
        extract_package(io.BytesIO(build_zip({"index.html": "x"})), tmp_path)


def test_extract_requires_launch_file(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match="File di lancio"):
        extract_package(io.BytesIO(build_zip({"imsmanifest.xml": MANIFEST_12})), tmp_path)


def test_not_a_zip(tmp_path: Path) -> None:
    with pytest.raises(PackageError, match="zip valido"):
        extract_package(io.BytesIO(b"not a zip"), tmp_path)


def test_zipfile_module_sanity() -> None:
    assert zipfile.is_zipfile(io.BytesIO(scorm12_zip()))
