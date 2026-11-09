"""Parsing di imsmanifest.xml (SCORM 1.2 e SCORM 2004).

Il parser lavora per *local-name* degli elementi, così da essere tollerante
rispetto alle varianti di namespace prodotte dai diversi authoring tool
(Articulate, iSpring, Adobe Captivate, ...).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any
from xml.etree.ElementTree import Element

from defusedxml import ElementTree as SafeET

from app.models.scorm import ScormVersion


class ManifestError(ValueError):
    """Manifest assente, malformato o non conforme."""


@dataclass(slots=True)
class ManifestItem:
    identifier: str
    title: str
    identifierref: str | None = None
    parameters: str | None = None
    children: list[ManifestItem] = field(default_factory=list)


@dataclass(slots=True)
class ManifestResource:
    identifier: str
    href: str | None
    scorm_type: str | None  # "sco" | "asset"
    base: str | None = None


@dataclass(slots=True)
class ManifestOrganization:
    identifier: str
    title: str
    items: list[ManifestItem]


@dataclass(slots=True)
class ParsedManifest:
    identifier: str
    title: str
    version: ScormVersion
    launch_path: str
    organizations: list[dict[str, Any]]
    resources: list[dict[str, Any]]

    def to_json(self) -> dict[str, Any]:
        data = asdict(self)
        data["version"] = self.version.value
        return data


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _attr(el: Element, name: str) -> str | None:
    """Legge un attributo ignorando il namespace (es. adlcp:scormtype / adlcp:scormType)."""
    for key, value in el.attrib.items():
        if _local(key).lower() == name.lower():
            return value
    return None


def _children(el: Element, name: str) -> list[Element]:
    return [c for c in el if _local(c.tag) == name]


def _child(el: Element, name: str) -> Element | None:
    found = _children(el, name)
    return found[0] if found else None


def _text(el: Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _detect_version(root: Element) -> ScormVersion:
    metadata = _child(root, "metadata")
    schemaversion = _text(_child(metadata, "schemaversion")) if metadata is not None else ""
    if schemaversion:
        if schemaversion.startswith("1.2"):
            return ScormVersion.SCORM_12
        if "2004" in schemaversion or "1.3" in schemaversion:
            return ScormVersion.SCORM_2004

    # Fallback: namespace adlcp dichiarati nel documento
    raw_tags = " ".join(el.tag for el in root.iter()) + " ".join(
        k for el in root.iter() for k in el.attrib
    )
    if "adlcp_v1p3" in raw_tags or "adlseq" in raw_tags or "imsss" in raw_tags:
        return ScormVersion.SCORM_2004
    if "adlcp_rootv1p2" in raw_tags:
        return ScormVersion.SCORM_12
    raise ManifestError("Impossibile determinare la versione SCORM del pacchetto")


def _parse_item(el: Element) -> ManifestItem:
    return ManifestItem(
        identifier=_attr(el, "identifier") or "",
        title=_text(_child(el, "title")),
        identifierref=_attr(el, "identifierref"),
        parameters=_attr(el, "parameters"),
        children=[_parse_item(c) for c in _children(el, "item")],
    )


def _first_launchable(items: list[ManifestItem]) -> ManifestItem | None:
    for item in items:
        if item.identifierref:
            return item
        nested = _first_launchable(item.children)
        if nested:
            return nested
    return None


def _join_url(*parts: str | None) -> str:
    return "".join(p for p in parts if p)


def parse_manifest(xml_bytes: bytes) -> ParsedManifest:
    try:
        root = SafeET.fromstring(xml_bytes)
    except SafeET.ParseError as exc:
        raise ManifestError(f"imsmanifest.xml non valido: {exc}") from exc

    if _local(root.tag) != "manifest":
        raise ManifestError("Il root element non è <manifest>")

    version = _detect_version(root)

    orgs_el = _child(root, "organizations")
    resources_el = _child(root, "resources")
    if orgs_el is None or resources_el is None:
        raise ManifestError("Manifest privo di <organizations> o <resources>")

    resources_base = _attr(resources_el, "base")
    resources = {
        r.identifier: r
        for r in (
            ManifestResource(
                identifier=_attr(res, "identifier") or "",
                href=_attr(res, "href"),
                scorm_type=(_attr(res, "scormtype") or "").lower() or None,
                base=_attr(res, "base"),
            )
            for res in _children(resources_el, "resource")
        )
    }

    organizations = [
        ManifestOrganization(
            identifier=_attr(org, "identifier") or "",
            title=_text(_child(org, "title")),
            items=[_parse_item(i) for i in _children(org, "item")],
        )
        for org in _children(orgs_el, "organization")
    ]
    if not organizations:
        raise ManifestError("Nessuna <organization> definita")

    default_id = _attr(orgs_el, "default")
    default_org = next((o for o in organizations if o.identifier == default_id), organizations[0])

    item = _first_launchable(default_org.items)
    if item is None or item.identifierref not in resources:
        raise ManifestError("Nessun item lanciabile collegato a una risorsa")

    resource = resources[item.identifierref]
    if not resource.href:
        raise ManifestError(f"La risorsa {resource.identifier} non ha href")

    launch_path = _join_url(resources_base, resource.base, resource.href)
    if item.parameters:
        params = item.parameters
        # Regole SCORM CAM: rimuove "?"/"&" iniziali e concatena correttamente
        params = params.lstrip("?&")
        launch_path += ("&" if "?" in launch_path else "?") + params

    title = default_org.title or item.title or _attr(root, "identifier") or "Pacchetto SCORM"

    return ParsedManifest(
        identifier=_attr(root, "identifier") or "",
        title=title,
        version=version,
        launch_path=launch_path,
        organizations=[asdict(o) for o in organizations],
        resources=[asdict(r) for r in resources.values()],
    )
