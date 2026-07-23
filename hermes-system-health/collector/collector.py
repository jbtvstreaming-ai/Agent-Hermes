"""
system-health collector — cross-platform (Windows/wmic + Linux/macOS/psutil), CLI-configurable.

J2B WSP — Web Solutions & Projects
https://j2b.live  |  hermes@j2b.live
"L'élégance n'est pas une option, c'est une signature."
License: MIT
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"


def default_cache_dir() -> Path:
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA", "")
    else:
        base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "hermes" / "cache"


def default_wiki_path() -> Path:
    return Path.home() / "wiki"


def default_hermes_paths():
    if IS_WINDOWS:
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "hermes" / "hermes-agent"
        return base / "venv" / "Scripts" / "python.exe", base / "hermes"
    base = Path.home() / ".hermes" / "hermes-agent"
    return base / "venv" / "bin" / "python", base / "hermes"


def parse_args():
    hermes_py, hermes_cli = default_hermes_paths()
    p = argparse.ArgumentParser(description="Hermes system-health collector")
    p.add_argument("--wiki", type=Path, default=default_wiki_path(), help="Path to the LLM wiki")
    p.add_argument("--output", type=Path, default=default_cache_dir(), help="Output cache directory")
    p.add_argument("--hermes-python", type=Path, default=hermes_py, help="Path to the hermes-agent venv python")
    p.add_argument("--hermes-cli", type=Path, default=hermes_cli, help="Path to the hermes CLI entrypoint")
    p.add_argument("--plugin", type=Path, default=None, help="Path to the installed plugin.js to inject into")
    p.add_argument("--verbose", action="store_true", help="Print errors instead of swallowing them")
    return p.parse_args()


def _log(verbose, msg):
    if verbose:
        print(f"[collector] {msg}", file=sys.stderr)


# ── System metrics ───────────────────────────────────────────────────
def _wmic(cls, prop, verbose=False):
    try:
        r = subprocess.run(
            ["wmic", "path", cls, "get", prop, "/format:value"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATION_FLAGS') else 0,  # noqa
        )
        for l in r.stdout.splitlines():
            if l.strip().startswith(prop + "="):
                return l.split("=", 1)[1].strip()
    except Exception as e:
        _log(verbose, f"wmic({cls},{prop}) failed: {e}")
    return None


def get_system_windows(verbose=False):
    cpu = _wmic("Win32_Processor", "LoadPercentage", verbose)
    mt = _wmic("Win32_ComputerSystem", "TotalPhysicalMemory", verbose)
    mf = _wmic("Win32_OperatingSystem", "FreePhysicalMemory", verbose)
    tb = int(mt) if mt else 0
    fk = int(mf) if mf else 0
    ram = {"used_gb": 0, "total_gb": 0, "percent": 0}
    if tb:
        ram = {
            "used_gb": round((tb - fk * 1024) / 1073741824, 1),
            "total_gb": round(tb / 1073741824, 1),
            "percent": round((tb - fk * 1024) / tb * 100, 1),
        }
    try:
        r = subprocess.run(
            ["wmic", "logicaldisk", "where", "DeviceID='C:'", "get", "Size,FreeSpace", "/format:value"],
            capture_output=True, text=True, timeout=5,
        )
        ds, df = None, None
        for l in r.stdout.splitlines():
            s = l.strip()
            if s.startswith("Size="):
                ds = s.split("=", 1)[1].strip()
            elif s.startswith("FreeSpace="):
                df = s.split("=", 1)[1].strip()
        disk = (
            {
                "used_gb": round((int(ds) - int(df)) / 1073741824, 1),
                "total_gb": round(int(ds) / 1073741824, 1),
                "percent": round((int(ds) - int(df)) / int(ds) * 100, 1),
            }
            if ds and df
            else {"used_gb": 0, "total_gb": 0, "percent": 0}
        )
    except Exception as e:
        _log(verbose, f"wmic disk failed: {e}")
        disk = {"used_gb": 0, "total_gb": 0, "percent": 0}
    return {"cpu": round(float(cpu), 1) if cpu else 0, "ram": ram, "disk": disk}


def get_system_psutil(verbose=False):
    try:
        import psutil  # noqa
    except ImportError:
        _log(verbose, "psutil not installed — run `pip install psutil`")
        return {"cpu": 0, "ram": {"used_gb": 0, "total_gb": 0, "percent": 0},
                "disk": {"used_gb": 0, "total_gb": 0, "percent": 0}}
    cpu = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    ram = {"used_gb": round(vm.used / 1073741824, 1), "total_gb": round(vm.total / 1073741824, 1), "percent": vm.percent}
    du = psutil.disk_usage(str(Path.home().anchor or "/"))
    disk = {"used_gb": round(du.used / 1073741824, 1), "total_gb": round(du.total / 1073741824, 1), "percent": du.percent}
    return {"cpu": cpu, "ram": ram, "disk": disk}


def get_system(verbose=False):
    return get_system_windows(verbose) if IS_WINDOWS else get_system_psutil(verbose)


# ── Wiki stats ────────────────────────────────────────────────────────
def get_wiki(wiki_path: Path, verbose=False):
    if not wiki_path.exists():
        _log(verbose, f"Wiki path not found: {wiki_path}")
        return {"exists": False, "path": str(wiki_path)}
    c = {"entities": 0, "concepts": 0, "comparisons": 0, "queries": 0, "raw": 0, "total_wiki_pages": 0, "total_files": 0}
    nw = 0
    for f in wiki_path.rglob("*.md"):
        c["total_files"] += 1
        try:
            rel = f.relative_to(wiki_path).parts[0]
            if rel in ("entities", "concepts", "comparisons", "queries"):
                c[rel] += 1
                c["total_wiki_pages"] += 1
            elif rel == "raw":
                c["raw"] += 1
        except Exception:
            pass
        try:
            m = f.stat().st_mtime
            if m > nw:
                nw = m
        except Exception:
            pass
    for m in ("index.md", "SCHEMA.md", "log.md"):
        if (wiki_path / m).exists():
            c["total_files"] += 1
    return {
        "exists": True,
        "path": str(wiki_path),
        "enabled": True,
        **c,
        "last_updated": time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(nw)) if nw else "N/A",
    }


# ── Hermes CLI insights ───────────────────────────────────────────────
def get_hermes(hermes_py: Path, hermes_cli: Path, verbose=False):
    h = {
        "insights": {
            "sessions": 0, "messages": 0, "tool_calls": 0,
            "input_tokens": 0, "output_tokens": 0, "total_tokens": 0,
            "models": [], "tools": [],
        },
        "skills": {"total": 0, "enabled": 0},
    }
    try:
        r = subprocess.run([str(hermes_py), str(hermes_cli), "insights"], capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            t = r.stdout
            i = h["insights"]
            for key, pattern in (
                ("sessions", r"Sessions:\s+([\d,]+)"),
                ("messages", r"Messages:\s+([\d,]+)"),
                ("tool_calls", r"Tool calls:\s+([\d,]+)"),
                ("input_tokens", r"Input tokens:\s+([\d,]+)"),
                ("output_tokens", r"Output tokens:\s+([\d,]+)"),
                ("total_tokens", r"Total tokens:\s+([\d,]+)"),
            ):
                m = re.search(pattern, t)
                if m:
                    i[key] = int(m.group(1).replace(",", ""))
            in_m = False
            for l in t.splitlines():
                if "Model" in l and "Sessions" in l:
                    in_m = True
                    continue
                if in_m:
                    if not l.strip() or l.strip().startswith(("──", "📱", "🔧")):
                        in_m = False
                        continue
                    p = l.strip().split()
                    if len(p) >= 2 and p[1].replace(",", "").isdigit():
                        i["models"].append({"name": p[0], "sessions": int(p[1].replace(",", ""))})
            in_tt = False
            for l in t.splitlines():
                if "Tool" in l and "Calls" in l:
                    in_tt = True
                    continue
                if in_tt:
                    if not l.strip() or l.strip().startswith(("──", "Platform")):
                        in_tt = False
                        continue
                    p = l.strip().split()
                    if len(p) >= 2 and p[-1].replace(",", "").isdigit():
                        i["tools"].append({"name": " ".join(p[:-1]), "calls": int(p[-1].replace(",", ""))})
        else:
            _log(verbose, f"hermes insights exited {r.returncode}: {r.stderr.strip()}")
    except Exception as e:
        _log(verbose, f"hermes insights failed: {e}")

    try:
        r2 = subprocess.run([str(hermes_py), str(hermes_cli), "skills", "list"], capture_output=True, text=True, timeout=10)
        if r2.returncode == 0:
            sk_t = sk_e = 0
            for l in r2.stdout.splitlines():
                if l.strip().startswith("│") and l.strip().count("│") >= 4:
                    parts = [p.strip() for p in l.strip().split("│") if p.strip()]
                    if len(parts) >= 4 and parts[-1] in ("enabled", "disabled"):
                        sk_t += 1
                        if parts[-1] == "enabled":
                            sk_e += 1
            h["skills"] = {"total": sk_t, "enabled": sk_e}
        else:
            _log(verbose, f"hermes skills list exited {r2.returncode}: {r2.stderr.strip()}")
    except Exception as e:
        _log(verbose, f"hermes skills list failed: {e}")
    return h


# ── Injection into the installed plugin.js ─────────────────────────────
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


def inject_plugin(cache_file: Path, plugin_path, verbose=False):
    plugin_path = plugin_path or find_plugin_path()
    if not plugin_path or not plugin_path.exists() or not cache_file.exists():
        _log(verbose, "plugin.js or cache file not found — skipping injection")
        return
    data = json.loads(cache_file.read_text("utf-8"))
    data["_injected_at"] = time.strftime("%H:%M:%S")
    data_str = json.dumps(data, indent=2)
    plugin = plugin_path.read_text("utf-8")
    ms, me = "// __INJECTED_DATA_START__", "// __INJECTED_DATA_END__"
    injection = f"{ms}\nconst __HEALTH_DATA__ = {data_str};\n{me}"
    if ms in plugin:
        old_start = plugin.index(ms)
        old_end = plugin.index(me) + len(me)
        plugin = plugin[:old_start] + injection + plugin[old_end:]
    else:
        plugin = plugin.replace("const ID = 'system-health'", f"{injection}\n\nconst ID = 'system-health'")
    import shutil
    shutil.copy2(str(plugin_path), str(plugin_path) + ".bak")
    plugin_path.write_text(plugin, "utf-8")
    _log(verbose, f"Injected into {plugin_path}")


def main():
    args = parse_args()
    cache_dir = args.output
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / "system-health.json"

    data = {
        "system": get_system(args.verbose),
        "wiki": get_wiki(args.wiki, args.verbose),
        "hermes": get_hermes(args.hermes_python, args.hermes_cli, args.verbose),
        "timestamp": time.time() * 1000,
    }
    cache_file.write_text(json.dumps(data, indent=2))
    print(f"OK ({len(json.dumps(data))}b) -> {cache_file}")
    inject_plugin(cache_file, args.plugin, args.verbose)


if __name__ == "__main__":
    main()
