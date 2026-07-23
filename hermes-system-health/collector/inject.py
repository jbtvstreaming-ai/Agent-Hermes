"""
Injects system-health data into the installed Hermes desktop plugin.js.
Reads from the cache file, replaces the __HEALTH_DATA__ block.

J2B WSP — Web Solutions & Projects
https://j2b.live  |  hermes@j2b.live
License: MIT
"""

import json, os, shutil, sys, time
from pathlib import Path

MARKER_START = "// __INJECTED_DATA_START__"
MARKER_END = "// __INJECTED_DATA_END__"


def find_plugin_path():
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "desktop-plugins",
        Path(os.environ.get("APPDATA", "")) / "hermes" / "desktop-plugins",
        Path.home() / ".hermes" / "desktop-plugins",
        Path.home() / ".local" / "share" / "hermes" / "desktop-plugins",
    ]
    for c in candidates:
        p = c / "system-health" / "plugin.js"
        if p.exists():
            return p
    return None


def find_cache_file():
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", ""))
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    candidates = [
        base / "hermes" / "cache" / "system-health.json",
        Path.home() / ".hermes" / "cache" / "system-health.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def inject(plugin_path, cache_path):
    data = json.loads(cache_path.read_text("utf-8"))
    data["_injected_at"] = time.strftime("%H:%M:%S")
    data_str = json.dumps(data, indent=2)
    plugin = plugin_path.read_text("utf-8")
    injection = f"{MARKER_START}\nconst __HEALTH_DATA__ = {data_str};\n{MARKER_END}"
    if MARKER_START in plugin:
        old_start = plugin.index(MARKER_START)
        old_end = plugin.index(MARKER_END) + len(MARKER_END)
        plugin = plugin[:old_start] + injection + plugin[old_end:]
    else:
        plugin = plugin.replace("const ID = 'system-health'", f"{injection}\n\nconst ID = 'system-health'")
    shutil.copy2(str(plugin_path), str(plugin_path) + ".bak")
    plugin_path.write_text(plugin, "utf-8")
    s = data.get("system", {})
    w = data.get("wiki", {})
    print(f"Injected: CPU {s.get('cpu', '?')}% | Wiki {w.get('total_wiki_pages', '?')} pages | {data['_injected_at']}")


def main():
    plugin = find_plugin_path()
    cache = find_cache_file()
    args = iter(sys.argv[1:])
    for arg in args:
        if arg == "--plugin": plugin = Path(next(args, ""))
        elif arg == "--cache": cache = Path(next(args, ""))
        elif arg in ("--help", "-h"): print(__doc__); return
    if not plugin or not plugin.exists():
        print("Plugin not found. Use --plugin /path/to/plugin.js"); return 1
    if not cache or not cache.exists():
        print("Cache not found. Use --cache /path/to/system-health.json"); return 1
    inject(plugin, cache)
    return 0


if __name__ == "__main__":
    sys.exit(main())
