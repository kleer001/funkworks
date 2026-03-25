#!/usr/bin/env python3
"""
Screenshot runner for the Funkworks tutorial pipeline.

Each shot in the manifest has a mode:
  auto    — runner executes setup[] commands via the app client, then captures
  manual  — runner prints a prompt, waits for the operator to set up the app,
            then captures on Enter

Usage:
  # MCP mode (app already running):
  python -m src.tutorials.screenshot_runner data/tutorial_manifests/fluid_domain_visibility.json

  # Retake one shot (skips pre_run, scene already set up):
  python -m src.tutorials.screenshot_runner data/tutorial_manifests/fluid_domain_visibility.json --shot 02_panel_preview

  # Launch Blender headlessly:
  python -m src.tutorials.screenshot_runner data/tutorial_manifests/fluid_domain_visibility.json \\
    --launch /usr/bin/blender --headless
"""

import argparse
import base64
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

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
            payload = json.dumps({"type": cmd_type, "params": params})
            s.sendall((payload + "\n").encode())
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
# Window capture (universal — works for any app)
# ---------------------------------------------------------------------------

def _find_window_id(app_name: str) -> str:
    """Return the X11 window ID of a running app window (hex string)."""
    result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        if app_name in line:
            return line.split()[0]
    raise RuntimeError(f"No window containing '{app_name}' found via wmctrl.")


def capture_window(filepath: str, app_name: str = "Blender") -> None:
    """Capture an app window at its natural X11 pixel size using xwd."""
    win_id = _find_window_id(app_name)
    subprocess.run(["wmctrl", "-ia", win_id], check=True, capture_output=True)
    time.sleep(0.5)
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        f"xwd -id {win_id} -silent | convert xwd:- {filepath}",
        shell=True, check=True, capture_output=True,
    )


# ---------------------------------------------------------------------------
# App command execution (extensible per-client)
# ---------------------------------------------------------------------------

def execute_commands(client, commands: list[str]) -> None:
    """Execute a list of setup commands via the app client."""
    if not commands or client is None:
        return
    code = "\n".join(commands)
    if isinstance(client, BlenderMCPClient):
        client.execute(code)
    # Future clients: elif isinstance(client, HoudiniMCPClient): ...


# ---------------------------------------------------------------------------
# Pixel QA
# ---------------------------------------------------------------------------

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
# Optional Claude crop pass (requires ANTHROPIC_API_KEY in .env)
# ---------------------------------------------------------------------------

def get_crop_bbox(image_path: Path, description: str, crop_subject: str, area_type: str) -> dict:
    import anthropic
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


def apply_crop(image_path: Path, region: list[int]) -> None:
    x, y, w, h = region
    img = Image.open(image_path)
    img.crop((x, y, x + w, y + h)).save(image_path)


# ---------------------------------------------------------------------------
# Per-shot execution
# ---------------------------------------------------------------------------

def run_shot(shot: dict, client, app_name: str = "Blender") -> dict:
    """Process one shot: setup or prompt → capture → QA. Returns a result dict."""
    shot_id = shot["id"]
    filepath = PROJECT_ROOT / shot["capture"]["filepath"]
    filepath.parent.mkdir(parents=True, exist_ok=True)

    mode = shot.get("mode", "auto")

    if mode == "manual":
        print(f"\n  [{shot_id}] Manual setup required:")
        print(f"  → {shot.get('prompt', shot['description'])}")
        try:
            response = input("  Press Enter to capture, or 's' to skip: ").strip().lower()
        except EOFError:
            response = ""
        if response == "s":
            return {"id": shot_id, "status": "skipped"}
    else:
        if shot.get("setup"):
            try:
                execute_commands(client, shot["setup"])
            except Exception as e:
                return {"id": shot_id, "status": "failed", "error": f"Setup: {e}"}

    # Capture
    try:
        capture_method = shot.get("capture", {}).get("method", "window")
        if capture_method == "viewport" and isinstance(client, BlenderMCPClient):
            client._send("frame_all", {})
            client.capture_viewport(str(filepath))
        else:
            capture_window(str(filepath), app_name=app_name)
    except Exception as e:
        return {"id": shot_id, "status": "failed", "error": f"Capture: {e}"}

    # Pixel QA
    passed, reason = qa_check(filepath, allow_blank=shot.get("allow_blank", False))
    entry = {"id": shot_id, "status": "pass" if passed else "needs_review"}
    if not passed:
        entry["reason"] = reason

    # Optional Claude crop pass
    if entry["status"] == "pass" and shot.get("crop", {}).get("method") == "pending":
        try:
            bbox = get_crop_bbox(
                filepath,
                shot["description"],
                shot.get("crop_subject", ""),
                shot["capture"].get("area_type", ""),
            )
            if bbox["confidence"] == "low":
                entry.update(status="needs_review", reason=f"Low crop confidence: {bbox['rationale']}")
            else:
                apply_crop(filepath, bbox["region"])
                entry["crop"] = bbox
        except Exception as e:
            entry.update(status="failed", error=f"Crop pass: {e}")

    return entry


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run(manifest: dict, client, shot_ids: list[str] | None = None) -> list[dict]:
    app_name = manifest.get("app_window", "Blender")

    # One-time setup (skipped when --shot targets specific shots)
    if shot_ids is None and manifest.get("pre_run"):
        try:
            execute_commands(client, manifest["pre_run"])
        except Exception as e:
            print(f"  WARNING: pre_run failed: {e}", file=sys.stderr)

    shots = manifest["screenshots"]
    if shot_ids:
        shots = [s for s in shots if s["id"] in shot_ids]

    sym = {"pass": "✓", "failed": "✗", "needs_review": "?", "skipped": "—"}
    results = []
    for shot in shots:
        result = run_shot(shot, client, app_name=app_name)
        tail = f" — {result.get('error') or result.get('reason', '')}" if result.get("error") or result.get("reason") else ""
        print(f"  {sym.get(result['status'], '?')} {result['id']}: {result['status']}{tail}")
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(description="Tutorial screenshot runner")
    parser.add_argument("manifest", help="Path to screenshot manifest JSON")
    parser.add_argument("--shot", metavar="SHOT_ID", action="append", dest="shots",
                        help="Retake only this shot ID (repeatable). Skips pre_run.")
    parser.add_argument("--mcp-host", default="localhost")
    parser.add_argument("--mcp-port", type=int, default=9334)
    parser.add_argument("--no-mcp", action="store_true",
                        help="Skip MCP connection entirely (manual shots only)")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text())

    if args.no_mcp:
        client = None
    else:
        client = BlenderMCPClient(host=args.mcp_host, port=args.mcp_port)
        if not client.ping():
            print(f"WARNING: Cannot connect to MCP at {args.mcp_host}:{args.mcp_port}. Auto shots will fail; manual shots still work.")
            client = None

    results = run(manifest, client, shot_ids=args.shots)

    counts = {s: sum(1 for r in results if r.get("status") == s)
              for s in ("pass", "failed", "needs_review", "skipped")}
    print(f"\n{counts['pass']} passed, {counts['failed']} failed, "
          f"{counts['needs_review']} need review, {counts['skipped']} skipped")
    sys.exit(0 if counts["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
