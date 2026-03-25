#!/usr/bin/env python3
"""
Screenshot runner for the Funkworks tutorial pipeline.

Two modes:
  MCP (default)  — connect to a running Blender with MCP plugin active
  Launch         — spawn Blender as a subprocess (add --headless for xvfb)

Usage:
  # MCP mode (Blender already running, MCP on port 9334):
  python -m src.tutorials.screenshot_runner data/tutorial_manifests/fluid_domain_visibility.json

  # Launch mode (headless):
  python -m src.tutorials.screenshot_runner data/tutorial_manifests/fluid_domain_visibility.json \
    --launch /usr/bin/blender --headless
"""

import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from PIL import Image

PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")


# ---------------------------------------------------------------------------
# Blender MCP client (TCP socket, blender-mcp protocol)
# ---------------------------------------------------------------------------

class BlenderMCPClient:
    def __init__(self, host: str = "localhost", port: int = 9334):
        self.host = host
        self.port = port

    def _send(self, cmd_type: str, params: dict) -> dict:
        """Send one command, reading the handshake first. Returns the response dict."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)
            s.connect((self.host, self.port))
            # Consume the handshake the server sends on connect
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    json.loads(data.decode())
                    break
                except json.JSONDecodeError:
                    continue
            # Send the actual command
            payload = json.dumps({"type": cmd_type, "params": params})
            s.sendall((payload + "\n").encode())
            # Read the response
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                try:
                    json.loads(data.decode())
                    break
                except json.JSONDecodeError:
                    continue
        return json.loads(data.decode())

    def execute(self, code: str) -> str:
        """Execute Python in Blender. Returns result or raises on error."""
        resp = self._send("execute_python", {"code": code})
        if resp.get("status") == "error":
            raise RuntimeError(f"Blender: {resp.get('message', resp)}")
        return str(resp.get("result", {}).get("result", ""))

    def capture_viewport(self, filepath: str) -> dict:
        """Use Blender's OpenGL render to capture the 3D viewport."""
        resp = self._send("capture_viewport", {"filepath": filepath})
        if resp.get("status") == "error":
            raise RuntimeError(f"capture_viewport: {resp.get('message', resp)}")
        return resp.get("result", {})

    def ping(self) -> bool:
        try:
            self._send("execute_python", {"code": "result = 'ok'"})
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Blender launch client (subprocess, uses --python)
# ---------------------------------------------------------------------------

# This script runs inside Blender (has access to bpy).
_BLENDER_CAPTURE_SCRIPT = '''\
import bpy, json, os, sys

results_path, manifest_path = sys.argv[sys.argv.index("--") + 1:]
with open(manifest_path) as f:
    manifest = json.load(f)

root = os.environ["FUNKWORKS_ROOT"]


def abs_path(rel):
    return os.path.join(root, rel)


def get_area(area_type):
    return next((a for a in bpy.context.screen.areas if a.type == area_type), None)


# Install plugin
bpy.ops.preferences.addon_install(filepath=abs_path(manifest["plugin_file"]))
bpy.ops.preferences.addon_enable(module=manifest["plugin"])

# Set up demo scene (generate if .blend doesn\'t exist yet)
scene_path = abs_path(manifest["scene_file"])
if os.path.exists(scene_path):
    bpy.ops.wm.open_mainfile(filepath=scene_path)
else:
    for cmd in manifest.get("scene_setup", []):
        exec(cmd)
    os.makedirs(os.path.dirname(scene_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=scene_path)

results = []
for shot in manifest["screenshots"]:
    try:
        for cmd in shot.get("setup", []):
            exec(cmd)
        filepath = abs_path(shot["capture"]["filepath"])
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        area = get_area(shot["capture"]["area_type"])
        if area is None:
            raise RuntimeError(f"No {shot[\'capture\'][\'area_type\']} area found")
        with bpy.context.temp_override(area=area):
            bpy.ops.screen.screenshot_area(filepath=filepath)
        results.append({"id": shot["id"], "success": True, "filepath": filepath})
    except Exception as e:
        results.append({"id": shot["id"], "success": False, "error": str(e)})

with open(results_path, "w") as f:
    json.dump(results, f)

bpy.ops.wm.quit_blender()
'''


class BlenderLaunchClient:
    def __init__(self, blender_path: str = "blender", headless: bool = False):
        self.blender_path = blender_path
        self.headless = headless

    def run_captures(self, manifest: dict) -> list[dict]:
        results_file = Path(tempfile.mktemp(suffix=".json"))
        manifest_file = Path(tempfile.mktemp(suffix=".json"))
        script_file = Path(tempfile.mktemp(suffix=".py"))
        try:
            manifest_file.write_text(json.dumps(manifest))
            script_file.write_text(_BLENDER_CAPTURE_SCRIPT)

            prefix = []
            if self.headless:
                prefix = ["xvfb-run", "-a", "-s", "-screen 0 1920x1080x24"]

            cmd = prefix + [
                self.blender_path,
                "--factory-startup",
                "--window-geometry", "0", "0", "1920", "1080",
                "--python", str(script_file),
                "--", str(results_file), str(manifest_file),
            ]
            env = {**os.environ, "FUNKWORKS_ROOT": str(PROJECT_ROOT)}
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180, env=env)
            if not results_file.exists():
                raise RuntimeError(f"Blender exited without results.\nstderr:\n{proc.stderr[-2000:]}")
            return json.loads(results_file.read_text())
        finally:
            for p in (results_file, manifest_file, script_file):
                p.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# MCP capture path
# ---------------------------------------------------------------------------

def _blender_window_id() -> str:
    """Return the X11 window ID of the running Blender instance (hex string)."""
    import subprocess
    result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        if "Blender" in line:
            return line.split()[0]  # e.g. "0x05800002"
    raise RuntimeError("No Blender window found via wmctrl. Is Blender running?")


def _spectacle_screenshot(filepath: str) -> None:
    """Maximize the Blender window, capture full screen, then restore."""
    import subprocess, time
    win_id = _blender_window_id()
    subprocess.run(["wmctrl", "-ia", win_id], check=True, capture_output=True)
    subprocess.run(["wmctrl", "-ir", win_id, "-b", "add,maximized_vert,maximized_horz"],
                   check=True, capture_output=True)
    time.sleep(1.0)  # let maximize animation settle and Blender redraw
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["spectacle", "-b", "-n", "-f", "-o", filepath], check=True, capture_output=True)
    subprocess.run(["wmctrl", "-ir", win_id, "-b", "remove,maximized_vert,maximized_horz"],
                   check=True, capture_output=True)
    # HiDPI: Spectacle captures at physical pixels; scale back to logical resolution
    img = Image.open(filepath)
    if img.width > 1920:
        img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
        img.save(filepath)


def _mcp_capture(client: BlenderMCPClient, manifest: dict) -> list[dict]:
    root = PROJECT_ROOT

    # Install plugin
    plugin_file = str(root / manifest["plugin_file"])
    client.execute(
        f"import bpy\n"
        f"bpy.ops.preferences.addon_install(filepath={plugin_file!r})\n"
        f"bpy.ops.preferences.addon_enable(module={manifest['plugin']!r})"
    )

    # Set up demo scene
    scene_path = root / manifest["scene_file"]
    if scene_path.exists():
        client.execute(f"import bpy\nbpy.ops.wm.open_mainfile(filepath={str(scene_path)!r})")
    else:
        scene_path.parent.mkdir(parents=True, exist_ok=True)
        setup = (
            "import bpy, bmesh\n"
            + "\n".join(manifest.get("scene_setup", []))
            + f"\nbpy.context.scene.render.resolution_x = 1920"
            + f"\nbpy.context.scene.render.resolution_y = 1080"
            + f"\nbpy.context.scene.render.resolution_percentage = 100"
            + f"\nbpy.ops.wm.save_as_mainfile(filepath={str(scene_path)!r})"
        )
        client.execute(setup)

    results = []
    for shot in manifest["screenshots"]:
        try:
            if shot.get("setup"):
                client.execute("import bpy, bmesh\n" + "\n".join(shot["setup"]))
            filepath = str(root / shot["capture"]["filepath"])
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            area_type = shot["capture"]["area_type"]
            if area_type == "VIEW_3D":
                client._send("frame_all", {})
                client.capture_viewport(filepath)
            else:
                _spectacle_screenshot(filepath)
            results.append({"id": shot["id"], "success": True, "filepath": filepath})
        except Exception as e:
            results.append({"id": shot["id"], "success": False, "error": str(e)})

    return results


# ---------------------------------------------------------------------------
# Phase 2: Claude crop pass
# ---------------------------------------------------------------------------

def get_crop_bbox(image_path: Path, description: str, crop_subject: str, area_type: str) -> dict:
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode()

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
                {"type": "text", "text": (
                    f"This is a screenshot of the {area_type} area from Blender.\n"
                    f"Tutorial step: \"{description}\"\n\n"
                    f"Crop to show only: \"{crop_subject}\"\n\n"
                    "Return JSON with:\n"
                    "- \"region\": [x, y, width, height] in pixels\n"
                    "- \"rationale\": one sentence\n"
                    "- \"confidence\": \"high\" / \"medium\" / \"low\""
                )},
            ],
        }],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


# ---------------------------------------------------------------------------
# Phase 3: Pillow crop + QA
# ---------------------------------------------------------------------------

def apply_crop(image_path: Path, region: list[int]) -> None:
    x, y, w, h = region
    img = Image.open(image_path)
    img.crop((x, y, x + w, y + h)).save(image_path)


def qa_check(image_path: Path, allow_blank: bool = False) -> tuple[bool, str]:
    if not image_path.exists():
        return False, "File not found"
    img = Image.open(image_path)
    w, h = img.size
    if w < 100 or h < 100:
        return False, f"Too small: {w}x{h}"
    if not allow_blank:
        from collections import Counter
        pixels = list(img.convert("RGB").getdata())
        most_common_count = Counter(pixels).most_common(1)[0][1]
        if most_common_count / len(pixels) > 0.95:
            return False, "Image is mostly blank"
    if not (0.3 <= w / h <= 4.0):
        return False, f"Unusual aspect ratio {w/h:.2f}"
    return True, "ok"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run(manifest: dict, client) -> list[dict]:
    if isinstance(client, BlenderMCPClient):
        capture_results = _mcp_capture(client, manifest)
    else:
        capture_results = client.run_captures(manifest)

    shot_by_id = {s["id"]: s for s in manifest["screenshots"]}
    final = []

    for cap in capture_results:
        shot = shot_by_id[cap["id"]]
        entry = {"id": cap["id"]}

        if not cap["success"]:
            entry.update(status="failed", error=cap.get("error"))
            final.append(entry)
            continue

        filepath = PROJECT_ROOT / shot["capture"]["filepath"]
        crop_method = shot.get("crop", {}).get("method", "area_only")

        if crop_method == "pending":
            try:
                bbox = get_crop_bbox(
                    filepath,
                    shot["description"],
                    shot["crop_subject"],
                    shot["capture"]["area_type"],
                )
                if bbox["confidence"] == "low":
                    entry.update(status="needs_review", reason=f"Low crop confidence: {bbox['rationale']}")
                    final.append(entry)
                    continue
                apply_crop(filepath, bbox["region"])
                entry["crop"] = bbox
            except Exception as e:
                entry.update(status="failed", error=f"Crop pass: {e}")
                final.append(entry)
                continue

        passed, reason = qa_check(filepath, allow_blank=shot.get("allow_blank", False))
        entry["status"] = "pass" if passed else "needs_review"
        if not passed:
            entry["reason"] = reason
        final.append(entry)

    return final


def main():
    parser = argparse.ArgumentParser(description="Funkworks tutorial screenshot runner")
    parser.add_argument("manifest", help="Path to screenshot manifest JSON")
    parser.add_argument("--mcp-host", default="localhost")
    parser.add_argument("--mcp-port", type=int, default=9334)
    parser.add_argument("--launch", metavar="BLENDER_PATH",
                        help="Launch Blender at this path instead of connecting via MCP")
    parser.add_argument("--headless", action="store_true",
                        help="Wrap Blender launch in xvfb-run (requires --launch)")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())

    if args.launch:
        client = BlenderLaunchClient(blender_path=args.launch, headless=args.headless)
    else:
        client = BlenderMCPClient(host=args.mcp_host, port=args.mcp_port)
        if not client.ping():
            sys.exit(f"ERROR: Cannot connect to Blender MCP at {args.mcp_host}:{args.mcp_port}")

    results = run(manifest, client)

    sym = {"pass": "✓", "failed": "✗", "needs_review": "?"}
    for r in results:
        tail = f" — {r.get('error') or r.get('reason', '')}" if r.get("error") or r.get("reason") else ""
        print(f"  {sym.get(r['status'], '?')} {r['id']}: {r['status']}{tail}")

    counts = {s: sum(1 for r in results if r["status"] == s) for s in ("pass", "failed", "needs_review")}
    print(f"\n{counts['pass']} passed, {counts['failed']} failed, {counts['needs_review']} need review")
    sys.exit(0 if counts["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
