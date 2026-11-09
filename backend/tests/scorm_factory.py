"""Generatori di pacchetti SCORM minimi per i test (e per demo locali)."""

import io
import zipfile

MANIFEST_12 = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="demo12" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="org1">
    <organization identifier="org1">
      <title>Corso Demo SCORM 1.2</title>
      <item identifier="item1" identifierref="res1"><title>Lezione 1</title></item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="res1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
    </resource>
  </resources>
</manifest>"""

MANIFEST_2004 = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="demo2004" version="1"
  xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3">
  <metadata><schema>ADL SCORM</schema><schemaversion>2004 4th Edition</schemaversion></metadata>
  <organizations default="ORG">
    <organization identifier="ORG">
      <title>Corso Demo SCORM 2004</title>
      <item identifier="I1">
        <title>Modulo</title>
        <item identifier="I1a" identifierref="R1" parameters="?lang=it">
          <title>Lezione</title>
        </item>
      </item>
    </organization>
  </organizations>
  <resources xml:base="content/">
    <resource identifier="R1" type="webcontent" adlcp:scormType="sco" href="launch.html">
      <file href="launch.html"/>
    </resource>
  </resources>
</manifest>"""

SCO_12_HTML = """<!doctype html><html><head><meta charset="utf-8"><title>SCO demo</title></head>
<body><h1>SCO demo SCORM 1.2</h1>
<button id="done">Completa lezione</button>
<script>
  var api = window.parent && window.parent.API;
  if (api) { api.LMSInitialize(""); }
  document.getElementById("done").onclick = function () {
    api.LMSSetValue("cmi.core.lesson_status", "completed");
    api.LMSSetValue("cmi.core.score.raw", "90");
    api.LMSCommit("");
    api.LMSFinish("");
    document.body.insertAdjacentHTML("beforeend", "<p>Completato ✔</p>");
  };
</script></body></html>"""


def build_zip(files: dict[str, str | bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def scorm12_zip() -> bytes:
    return build_zip({"imsmanifest.xml": MANIFEST_12, "index.html": SCO_12_HTML})


def scorm2004_zip() -> bytes:
    return build_zip(
        {"imsmanifest.xml": MANIFEST_2004, "content/launch.html": "<html>SCO 2004</html>"}
    )
