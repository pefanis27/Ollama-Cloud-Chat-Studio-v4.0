#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import ast
import importlib.metadata
import importlib.util
import os
import re
import shutil
import site
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


FORCED_EXCLUDES = {
    "IPython",
    "PyQt5",
    "PyQt6",
    "PySide2",
    "PySide6",
    "cv2",
    "fontTools",
    "jupyter",
    "notebook",
    "pygame",
    "qt_material",
    "requests",
    "scipy",
    "sklearn",
    "tensorflow",
    "torch",
    "torchvision",
}

PACKAGE_RULES: Dict[str, Dict[str, object]] = {
    "fitz": {
        "pip": "PyMuPDF",
        "hidden": ["fitz"],
        "collect_submodules": [],
        "copy_metadata": ["PyMuPDF"],
        "optional": False,
        "bundle": True,
    },
    "pymupdf": {
        "pip": "PyMuPDF",
        "hidden": ["fitz"],
        "collect_submodules": [],
        "copy_metadata": ["PyMuPDF"],
        "optional": False,
        "bundle": True,
    },
    "pypdf": {
        "pip": "pypdf",
        "hidden": ["pypdf"],
        "collect_submodules": ["pypdf"],
        "copy_metadata": ["pypdf"],
        "optional": False,
        "bundle": True,
    },
    "docx": {
        "pip": "python-docx",
        "hidden": ["docx", "lxml", "lxml.etree", "lxml._elementpath"],
        "collect_submodules": ["docx", "lxml"],
        "copy_metadata": ["python-docx", "lxml"],
        "optional": False,
        "bundle": True,
    },
    "lxml": {
        "pip": "lxml",
        "hidden": ["lxml", "lxml.etree", "lxml._elementpath"],
        "collect_submodules": ["lxml"],
        "copy_metadata": ["lxml"],
        "optional": False,
        "bundle": True,
    },
    "bs4": {
        "pip": "beautifulsoup4",
        "hidden": ["bs4", "soupsieve"],
        "collect_submodules": ["bs4", "soupsieve"],
        "copy_metadata": ["beautifulsoup4", "soupsieve"],
        "optional": False,
        "bundle": True,
    },
    "PIL": {
        "pip": "Pillow",
        "hidden": ["PIL"],
        "collect_submodules": ["PIL"],
        "copy_metadata": ["Pillow"],
        "optional": False,
        "bundle": True,
    },
    "cairosvg": {
        "pip": "CairoSVG",
        "hidden": ["cairosvg", "cssselect2", "tinycss2", "defusedxml"],
        "collect_submodules": [],
        "copy_metadata": ["CairoSVG", "cssselect2", "tinycss2", "defusedxml"],
        "optional": True,
        "bundle": True,
    },
    "pygments": {
        "pip": "Pygments",
        "hidden": ["pygments"],
        "collect_submodules": ["pygments"],
        "copy_metadata": ["Pygments"],
        "optional": False,
        "bundle": True,
    },
    "matplotlib": {
        "pip": "matplotlib",
        "hidden": [
            "matplotlib",
            "matplotlib.pyplot",
            "matplotlib.backends.backend_agg",
            "matplotlib.backends.backend_svg",
        ],
        "collect_submodules": [],
        "copy_metadata": ["matplotlib"],
        "optional": False,
        "bundle": False,
    },
    "mpl_toolkits": {
        "pip": "matplotlib",
        "hidden": ["mpl_toolkits", "mpl_toolkits.mplot3d"],
        "collect_submodules": [],
        "copy_metadata": ["matplotlib"],
        "optional": False,
        "bundle": False,
    },
    "numpy": {
        "pip": "numpy",
        "hidden": ["numpy"],
        "collect_submodules": [],
        "copy_metadata": ["numpy"],
        "optional": False,
        "bundle": False,
    },
    "pandas": {
        "pip": "pandas",
        "hidden": ["pandas"],
        "collect_submodules": [],
        "copy_metadata": ["pandas"],
        "optional": False,
        "bundle": False,
    },
    "pathlib": {
        "pip": None,
        "hidden": [],
        "collect_submodules": [],
        "copy_metadata": [],
        "optional": False,
        "bundle": False,
    },
}

STD_LIB_FALLBACK = {
    "__future__",
    "argparse",
    "ast",
    "base64",
    "concurrent",
    "copy",
    "dataclasses",
    "datetime",
    "html",
    "http",
    "io",
    "json",
    "logging",
    "math",
    "multiprocessing",
    "os",
    "pathlib",
    "queue",
    "re",
    "shlex",
    "shutil",
    "socket",
    "subprocess",
    "sys",
    "tempfile",
    "threading",
    "time",
    "tokenize",
    "typing",
    "urllib",
    "uuid",
    "webbrowser",
    "xml",
}

SOURCE_GLOB_PATTERNS = [
    "Ollama_Cloud_Chat_Studio_v6.py",
    "Ollama_Cloud_Chat_Studio_v*_UPDATED_v*.py",
    "Ollama_Cloud_Chat_Studio_v*_UPDATED.py",
    "Ollama_Cloud_Chat_Studio_v*.py",
    "Ollama_Cloud_Chat_Studio*.py",
]
SOURCE_EXCLUDE_NAMES = {
    "build_ollama_cloud_chat_studio_exe.py",
    "build_ollama_cloud_chat_studio_exe_UPDATED.py",
}

RUNTIME_IMPORT_HINTS: Dict[str, Sequence[str]] = {
    "matplotlib": [r"\bimport\s+matplotlib\b", r"\bfrom\s+matplotlib\b"],
    "mpl_toolkits": [r"\bfrom\s+mpl_toolkits\b", r"\bimport\s+mpl_toolkits\b"],
    "numpy": [r"\bimport\s+numpy\b", r"\bfrom\s+numpy\b"],
    "pandas": [r"\bimport\s+pandas\b", r"\bfrom\s+pandas\b"],
}


def eprint(*parts: object) -> None:
    print(*parts, file=sys.stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Builder για το Ollama Cloud Chat Studio με έλεγχο source, dependencies και PyInstaller.",
    )
    parser.add_argument("--source", default="", help="Κύριο .py αρχείο. Αν μείνει κενό, γίνεται αυτόματος εντοπισμός.")
    parser.add_argument("--name", default="", help="Όνομα executable. Αν μείνει κενό, χρησιμοποιείται το stem του source.")
    parser.add_argument("--icon", default="", help="Προαιρετικό .ico αρχείο.")
    parser.add_argument("--onefile", action="store_true", help="Δημιουργία ενός μόνο .exe αντί για onedir build.")
    parser.add_argument("--keep-spec", action="store_true", help="Να κρατηθεί το .spec μετά το build.")
    parser.add_argument("--no-clean", action="store_true", help="Να μη διαγραφούν build/dist πριν το build.")
    parser.add_argument("--zip", action="store_true", help="Δημιουργία zip του τελικού build.")
    parser.add_argument("--skip-auto-install", action="store_true", help="Μην εγκαταστήσεις αυτόματα όσα Python packages λείπουν.")
    parser.add_argument("--with-plot-deps", action="store_true", help="Εγκατάσταση και bundling matplotlib/mpl_toolkits/numpy/pandas όπου εντοπιστούν.")
    parser.add_argument("--dry-run", action="store_true", help="Εμφάνιση του build plan χωρίς εκτέλεση του PyInstaller.")
    return parser.parse_args()


def _site_package_dirs() -> List[Path]:
    paths: List[Path] = []
    for raw in list(site.getsitepackages()) + [site.getusersitepackages()]:
        if not raw:
            continue
        try:
            path = Path(raw).resolve()
        except Exception:
            continue
        if path not in paths:
            paths.append(path)
    return paths


def _extract_version_score(filename: str) -> Tuple[int, int]:
    lowered = filename.lower()
    updated_match = re.search(r"updated(?:_v(\d+))?", lowered)
    if updated_match:
        return (1, int(updated_match.group(1) or "1"))
    plain_match = re.search(r"_v(\d+)(?:\.py)?$", lowered)
    if plain_match:
        return (0, int(plain_match.group(1) or "0"))
    return (0, 0)


# Ο auto-detector προτιμά το πιο πρόσφατο και πιο "κύριο" app αρχείο.
def autodetect_source(project_root: Path) -> Optional[Path]:
    candidates: List[Path] = []
    for pattern in SOURCE_GLOB_PATTERNS:
        for path in project_root.glob(pattern):
            if not path.is_file():
                continue
            if path.name in SOURCE_EXCLUDE_NAMES:
                continue
            candidates.append(path.resolve())

    if not candidates:
        return None

    ranked = sorted(
        set(candidates),
        key=lambda p: (
            0 if p.name.lower().startswith("ollama_cloud_chat_studio") else 1,
            0 if "updated" in p.stem.lower() else 1,
            -_extract_version_score(p.name)[0],
            -_extract_version_score(p.name)[1],
            -p.stat().st_mtime,
            p.name.lower(),
        ),
    )
    return ranked[0]


def resolve_source_path(source_arg: str) -> Path:
    if source_arg:
        return Path(source_arg).resolve()

    search_roots = [Path.cwd()]
    script_dir = Path(__file__).resolve().parent
    if script_dir not in search_roots:
        search_roots.append(script_dir)

    for root in search_roots:
        detected = autodetect_source(root)
        if detected is not None:
            return detected

    raise FileNotFoundError("Δεν βρέθηκε αυτόματα source αρχείο. Δώσε ρητά --source <αρχείο.py>.")


def validate_input_paths(source: Path, icon: Optional[Path]) -> None:
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"Δεν βρέθηκε το source αρχείο: {source}")
    if source.suffix.lower() != ".py":
        raise ValueError("Το source πρέπει να είναι αρχείο .py")
    if icon is not None and (not icon.exists() or not icon.is_file()):
        raise FileNotFoundError(f"Δεν βρέθηκε το icon αρχείο: {icon}")


def clean_build_artifacts(project_root: Path, app_name: str) -> None:
    for target in (project_root / "build", project_root / "dist", project_root / f"{app_name}.spec"):
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
        elif target.exists():
            try:
                target.unlink()
            except OSError:
                pass


def read_source_text(source: Path) -> str:
    return source.read_text(encoding="utf-8")


# Τα AST imports πιάνουν τα πραγματικά imports του app.
def extract_import_roots(source_text: str) -> Set[str]:
    tree = ast.parse(source_text)
    roots: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                roots.add(node.module.split(".", 1)[0])
    return roots


# Τα runtime hints πιάνουν imports που κρύβονται σε generated scripts/string templates.
def extract_runtime_hint_roots(source_text: str) -> Set[str]:
    hinted: Set[str] = set()
    for root, patterns in RUNTIME_IMPORT_HINTS.items():
        if any(re.search(pattern, source_text) for pattern in patterns):
            hinted.add(root)
    return hinted


def is_stdlib_module(module_name: str) -> bool:
    if module_name in STD_LIB_FALLBACK:
        return True

    try:
        spec = importlib.util.find_spec(module_name)
    except Exception:
        return False

    if spec is None:
        return False

    origin = spec.origin
    if origin in (None, "built-in", "frozen"):
        return True

    try:
        origin_path = Path(origin).resolve()
    except Exception:
        return False

    site_dirs = _site_package_dirs()
    if any(origin_path == site_dir or site_dir in origin_path.parents for site_dir in site_dirs):
        return False

    try:
        stdlib_dir = Path(os.__file__).resolve().parent
        if origin_path == stdlib_dir or stdlib_dir in origin_path.parents:
            return True
    except Exception:
        pass

    return False


def detect_third_party_roots(import_roots: Iterable[str]) -> List[str]:
    return sorted({name for name in import_roots if not is_stdlib_module(name)})


def uninstall_obsolete_pathlib_backport_if_present() -> None:
    found_backport = False
    for base in _site_package_dirs():
        if not base.exists():
            continue
        if (base / "pathlib.py").exists() or any(base.glob("pathlib-*.dist-info")) or any(base.glob("pathlib-*.egg-info")):
            found_backport = True
            break

    if not found_backport:
        return

    print("Βρέθηκε obsolete package 'pathlib' στο site-packages. Γίνεται αφαίρεση...")
    result = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pathlib"], text=True)
    if result.returncode != 0:
        raise RuntimeError("Απέτυχε η αφαίρεση του obsolete package 'pathlib'.")


def ensure_package_installed(import_name: str, pip_name: Optional[str] = None) -> None:
    try:
        if importlib.util.find_spec(import_name) is not None:
            return
    except Exception:
        pass

    package_to_install = pip_name or import_name
    print(f"Λείπει το πακέτο '{package_to_install}'. Γίνεται εγκατάσταση...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", package_to_install], text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Απέτυχε η εγκατάσταση του '{package_to_install}'.")


def ensure_pyinstaller_ready() -> None:
    ensure_package_installed("PyInstaller", "pyinstaller")


def is_module_importable(module_name: str) -> bool:
    try:
        __import__(module_name)
        return True
    except Exception:
        return False


def should_include_rule(root: str, with_plot_deps: bool) -> bool:
    rule = PACKAGE_RULES.get(root)
    if not rule:
        return False
    if root in {"matplotlib", "mpl_toolkits", "numpy", "pandas"} and not with_plot_deps:
        return False
    if not bool(rule.get("optional", False)):
        return True
    return is_module_importable(root)


def ensure_detected_dependencies_installed(import_roots: Iterable[str], *, with_plot_deps: bool) -> None:
    roots = set(import_roots)
    for root in sorted(roots):
        rule = PACKAGE_RULES.get(root)
        if not rule:
            continue
        pip_name = rule.get("pip")
        if not pip_name:
            continue
        if root in {"matplotlib", "mpl_toolkits", "numpy", "pandas"} and not with_plot_deps:
            continue
        if bool(rule.get("optional", False)):
            print(f"Παραλείπεται το optional/native package '{pip_name}' για να αποφευχθούν build προβλήματα από system DLLs.")
            continue
        ensure_package_installed(root, str(pip_name))

    if "docx" in roots or "lxml" in roots:
        ensure_package_installed("lxml", "lxml")


def gather_pyinstaller_options(import_roots: Sequence[str], *, with_plot_deps: bool) -> Tuple[List[str], List[str]]:
    hiddenimports: List[str] = []
    collect_args: List[str] = []
    metadata_targets: Set[str] = set()

    for root in sorted(set(import_roots)):
        rule = PACKAGE_RULES.get(root)
        if not rule:
            continue
        if not bool(rule.get("bundle", False)) and not should_include_rule(root, with_plot_deps):
            continue
        if bool(rule.get("optional", False)) and not is_module_importable(root):
            print(f"Παραλείπεται το optional/native import '{root}' από το bundling γιατί δεν είναι importable στο τρέχον σύστημα.")
            continue

        for name in rule.get("hidden", []):
            hiddenimports.append(str(name))
        for name in rule.get("collect_submodules", []):
            collect_args.extend(["--collect-submodules", str(name)])
        for name in rule.get("copy_metadata", []):
            try:
                importlib.metadata.distribution(str(name))
                metadata_targets.add(str(name))
            except importlib.metadata.PackageNotFoundError:
                pass

    hiddenimports.extend(
        [
            "concurrent.futures",
            "concurrent.futures._base",
            "concurrent.futures.thread",
            "concurrent.futures.process",
        ]
    )
    for name in sorted(metadata_targets):
        collect_args.extend(["--copy-metadata", name])
    return sorted(set(hiddenimports)), collect_args


def build_exclude_args(import_roots: Sequence[str], *, with_plot_deps: bool) -> List[str]:
    imported = set(import_roots)
    if with_plot_deps:
        imported.update({"matplotlib", "mpl_toolkits", "numpy", "pandas"})
    excludes: List[str] = []
    for name in sorted(FORCED_EXCLUDES):
        if name not in imported:
            excludes.extend(["--exclude-module", name])
    return excludes


def build_pyinstaller_command(
    source: Path,
    app_name: str,
    icon: Optional[Path],
    onefile: bool,
    hiddenimports: Sequence[str],
    collect_args: Sequence[str],
    exclude_args: Sequence[str],
) -> List[str]:
    cmd: List[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--noupx",
        "--name",
        app_name,
    ]
    cmd.append("--onefile" if onefile else "--onedir")
    if icon is not None:
        cmd.extend(["--icon", str(icon)])
    for mod in hiddenimports:
        cmd.extend(["--hidden-import", mod])
    cmd.extend(collect_args)
    cmd.extend(exclude_args)
    cmd.append(str(source))
    return cmd


def remove_spec_if_needed(project_root: Path, app_name: str, keep_spec: bool) -> None:
    if keep_spec:
        return
    spec_path = project_root / f"{app_name}.spec"
    if spec_path.exists():
        try:
            spec_path.unlink()
        except OSError:
            pass


def zip_output(project_root: Path, app_name: str, onefile: bool) -> Path:
    dist_dir = project_root / "dist"
    target = dist_dir / (f"{app_name}.exe" if onefile else app_name)
    archive_base = dist_dir / f"{app_name}_portable"
    return Path(shutil.make_archive(str(archive_base), "zip", root_dir=str(target.parent), base_dir=target.name))


# Οι σημειώσεις αυτές λένε καθαρά τι λύνει ο builder και τι εξαρτάται ακόμα από runtime Python.
def detect_capabilities(source_text: str) -> List[str]:
    notes: List[str] = []
    if "resolve_python_for_generated_scripts" in source_text:
        notes.append(
            "Το app εκτελεί generated Python scripts μέσω εξωτερικού interpreter όταν είναι packaged. "
            "Το .exe δουλεύει κανονικά, αλλά τα >Run / plot features χρειάζονται διαθέσιμο Python στο target μηχάνημα."
        )
    if "OLLAMA_PLOT_OUTPUT" in source_text or "matplotlib" in source_text:
        notes.append(
            "Εντοπίστηκε plotting/runtime λογική. Με --with-plot-deps εγκαθίστανται και δένονται τα plot dependencies στο build περιβάλλον, "
            "όμως αυτό δεν υποκαθιστά τον εξωτερικό Python interpreter που ψάχνει το app στο packaged mode."
        )
    if "fitz" in source_text or "from docx" in source_text or "pypdf" in source_text:
        notes.append("Εντοπίστηκε stack export PDF/DOCX και ο builder το υποστηρίζει ρητά με hidden imports και metadata rules.")
    return notes


def print_summary(
    source: Path,
    app_name: str,
    direct_roots: Sequence[str],
    hinted_roots: Sequence[str],
    third_party: Sequence[str],
    hiddenimports: Sequence[str],
    onefile: bool,
    exclude_args: Sequence[str],
    capability_notes: Sequence[str],
) -> None:
    excluded_modules = [exclude_args[i + 1] for i, item in enumerate(exclude_args[:-1]) if item == "--exclude-module"]
    print("=" * 86)
    print("Builder για Ollama Cloud Chat Studio")
    print("=" * 86)
    print(f"Source              : {source.name}")
    print(f"App name            : {app_name}")
    print(f"Build mode          : {'onefile' if onefile else 'onedir'}")
    print("Console             : disabled (GUI / χωρίς terminal)")
    print("UPX                 : disabled")
    print(f"Direct imports      : {', '.join(direct_roots) if direct_roots else 'κανένα'}")
    print(f"Runtime hints       : {', '.join(hinted_roots) if hinted_roots else 'κανένα'}")
    print(f"Third-party         : {', '.join(third_party) if third_party else 'κανένα'}")
    print(f"Hidden imports      : {', '.join(hiddenimports) if hiddenimports else 'κανένα'}")
    print(f"Excludes            : {', '.join(excluded_modules) if excluded_modules else 'κανένα'}")
    if capability_notes:
        print("Notes               :")
        for note in capability_notes:
            print(f"  - {note}")
    print("=" * 86)


def main() -> int:
    args = parse_args()

    source = resolve_source_path(args.source)
    icon = Path(args.icon).resolve() if args.icon else None
    validate_input_paths(source, icon)

    project_root = source.parent
    os.chdir(project_root)
    app_name = args.name.strip() or source.stem

    if not args.no_clean:
        clean_build_artifacts(project_root, app_name)

    uninstall_obsolete_pathlib_backport_if_present()
    ensure_pyinstaller_ready()

    source_text = read_source_text(source)
    direct_roots = sorted(extract_import_roots(source_text))
    hinted_roots = sorted(extract_runtime_hint_roots(source_text))
    all_roots = sorted(set(direct_roots) | set(hinted_roots))
    third_party = detect_third_party_roots(all_roots)
    capability_notes = detect_capabilities(source_text)

    if not args.skip_auto_install:
        ensure_detected_dependencies_installed(third_party, with_plot_deps=args.with_plot_deps)

    hiddenimports, collect_args = gather_pyinstaller_options(all_roots, with_plot_deps=args.with_plot_deps)
    exclude_args = build_exclude_args(all_roots, with_plot_deps=args.with_plot_deps)

    print_summary(
        source=source,
        app_name=app_name,
        direct_roots=direct_roots,
        hinted_roots=hinted_roots,
        third_party=third_party,
        hiddenimports=hiddenimports,
        onefile=args.onefile,
        exclude_args=exclude_args,
        capability_notes=capability_notes,
    )

    cmd = build_pyinstaller_command(
        source=source,
        app_name=app_name,
        icon=icon,
        onefile=args.onefile,
        hiddenimports=hiddenimports,
        collect_args=collect_args,
        exclude_args=exclude_args,
    )

    print("Εκτέλεση:")
    print(" ".join(f'"{part}"' if " " in part else part for part in cmd))

    if args.dry_run:
        print("\nDRY RUN: Δεν εκτελέστηκε το PyInstaller.")
        return 0

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise RuntimeError(f"Το PyInstaller απέτυχε με exit code {result.returncode}.")

    remove_spec_if_needed(project_root, app_name, args.keep_spec)

    dist_path = project_root / "dist" / (f"{app_name}.exe" if args.onefile else app_name)
    print(f"\nOK: Το build ολοκληρώθηκε στο: {dist_path}")

    if args.zip:
        archive_path = zip_output(project_root, app_name, args.onefile)
        print(f"ZIP: {archive_path}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        eprint(f"\nΣφάλμα: {exc}")
        raise SystemExit(1)
