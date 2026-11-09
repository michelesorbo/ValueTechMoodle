"""Estrazione sicura dei pacchetti SCORM (zip) su filesystem.

Protezioni implementate:
- Zip Slip (path traversal tramite "../" o path assoluti)
- symlink dentro l'archivio
- zip bomb (limite su dimensione decompressa totale e numero di entry)
"""

from __future__ import annotations

import shutil
import stat
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from app.services.scorm.manifest import ManifestError, ParsedManifest, parse_manifest

MAX_ENTRIES = 20_000
MAX_UNCOMPRESSED_BYTES = 2 * 1024**3  # 2 GiB


class PackageError(ValueError):
    pass


def _safe_member_path(name: str) -> PurePosixPath:
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or (p.parts and ":" in p.parts[0]):
        raise PackageError(f"Percorso non consentito nell'archivio: {name!r}")
    return p


def extract_package(fileobj: BinaryIO, storage_root: Path) -> tuple[uuid.UUID, ParsedManifest]:
    """Valida ed estrae lo zip in ``storage_root/<uuid>``. Ritorna (package_id, manifest)."""
    try:
        zf = zipfile.ZipFile(fileobj)
    except zipfile.BadZipFile as exc:
        raise PackageError("Il file caricato non è uno zip valido") from exc

    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_ENTRIES:
            raise PackageError("Troppi file nell'archivio")
        if sum(i.file_size for i in infos) > MAX_UNCOMPRESSED_BYTES:
            raise PackageError("Dimensione decompressa eccessiva")

        names = {i.filename for i in infos}
        if "imsmanifest.xml" not in names:
            raise PackageError("imsmanifest.xml mancante nella root del pacchetto")

        try:
            manifest = parse_manifest(zf.read("imsmanifest.xml"))
        except ManifestError as exc:
            raise PackageError(str(exc)) from exc

        launch_file = manifest.launch_path.split("?", 1)[0].split("#", 1)[0]
        if launch_file not in names:
            raise PackageError(f"File di lancio non presente nell'archivio: {launch_file}")

        package_id = uuid.uuid4()
        target = storage_root / str(package_id)
        target.mkdir(parents=True, exist_ok=False)

        try:
            for info in infos:
                rel = _safe_member_path(info.filename)
                if stat.S_ISLNK(info.external_attr >> 16):
                    raise PackageError(f"Symlink non consentito: {info.filename!r}")
                dest = target.joinpath(*rel.parts)
                if info.is_dir():
                    dest.mkdir(parents=True, exist_ok=True)
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(info) as src, dest.open("wb") as out:
                    shutil.copyfileobj(src, out, length=1024 * 1024)
        except Exception:
            shutil.rmtree(target, ignore_errors=True)
            raise

    return package_id, manifest


def remove_package(storage_root: Path, package_id: uuid.UUID) -> None:
    shutil.rmtree(storage_root / str(package_id), ignore_errors=True)
