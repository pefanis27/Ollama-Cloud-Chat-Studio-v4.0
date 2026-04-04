#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Διαδραστικός οδηγός δημιουργίας εκτελέσιμου με PyInstaller.

Η έκδοση αυτή βελτιώνει το build wizard ώστε να αναγνωρίζει καλύτερα τα
third-party packages που χρησιμοποιεί η εφαρμογή, να τα περνά αυτόματα στο
PyInstaller και να γράφει προαιρετικά manifest με τα πακέτα που χρειάζονται.

Ειδικά για το τρέχον Ollama Cloud Chat Studio, η εφαρμογή χρησιμοποιεί πλέον
τα optional packages:
- pypdf      : για ανάγνωση uploaded PDF αρχείων
- PyMuPDF    : για post-processing / polish του exported PDF (import names: fitz, pymupdf)

Το script:
1. Σκανάρει το source file με AST.
2. Ανιχνεύει imports και τρίτα packages.
3. Προσθέτει hidden-import / collect-all για packages που το χρειάζονται.
4. Γράφει requirements manifest με τα packages που χρησιμοποιεί πλέον η εφαρμογή.
"""
from __future__ import annotations

import ast
import importlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set

APP_VERSION = '3.2'
SEP = '=' * 72
SEP2 = '─' * 72
DEFAULT_APP_NAME = 'OllamaCloudChatStudio'
DEFAULT_UPX_EXCLUDES = ['_uuid.pyd', 'python3.dll']
DEFAULT_STDLIB_HIDDEN_IMPORTS = [
    'concurrent.futures',
    'concurrent.futures._base',
    'concurrent.futures.thread',
    'concurrent.futures.process',
    'http.server',
    'urllib.request',
    'urllib.error',
    'urllib.parse',
    'xml.etree.ElementTree',
    'email.mime.text',
]

# Packages που θέλουν ειδικό χειρισμό στο PyInstaller.
# Το collect-all είναι ιδιαίτερα χρήσιμο για packages με data/binaries.
PACKAGE_RULES: Dict[str, Dict[str, object]] = {
    'pypdf': {
        'display_name': 'pypdf',
        'import_names': ['pypdf'],
        'pip_name': 'pypdf',
        'hidden_imports': ['pypdf'],
        'collect_all': ['pypdf'],
    },
    'pymupdf': {
        'display_name': 'PyMuPDF',
        'import_names': ['fitz', 'pymupdf'],
        'pip_name': 'PyMuPDF',
        'hidden_imports': ['fitz', 'pymupdf'],
        'collect_all': ['fitz', 'pymupdf'],
    },
}


@dataclass
class BuildConfig:
    """Συγκεντρώνει όλες τις ρυθμίσεις του build σε ένα ενιαίο αντικείμενο."""

    source: Path
    app_name: str
    one_file: bool
    console: bool
    icon_path: str = ''
    use_upx: bool = False
    upx_excludes: list[str] = field(default_factory=list)
    clean_before_build: bool = True
    open_dist_after_build: bool = False
    run_after_build: bool = False
    extra_hidden_imports: list[str] = field(default_factory=list)
    write_requirements_manifest: bool = True


@dataclass
class ResolvedBuildAssets:
    """Τα τελικά assets/flags που θα περάσουν στο PyInstaller."""

    hidden_imports: list[str] = field(default_factory=list)
    collect_all_packages: list[str] = field(default_factory=list)
    detected_packages: list[str] = field(default_factory=list)
    detected_import_roots: list[str] = field(default_factory=list)
    requirements_lines: list[str] = field(default_factory=list)


def step(msg: str) -> None:
    print(f'\n  ▶  {msg}')


def ok(msg: str) -> None:
    print(f'  ✅  {msg}')


def warn(msg: str) -> None:
    print(f'  ⚠   {msg}')


def fail(msg: str, code: int = 1) -> None:
    print(f'\n  ❌  {msg}\n')
    raise SystemExit(code)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"\n  $ {' '.join((str(c) for c in cmd))}\n")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        fail(f'Η εντολή απέτυχε με κωδικό {result.returncode}.')
    return result


def ask_text(prompt: str, default: str = '') -> str:
    suffix = f' [{default}]' if default else ''
    value = input(f'{prompt}{suffix}: ').strip()
    return value if value else default


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    default_text = 'Y/n' if default else 'y/N'
    while True:
        value = input(f'{prompt} [{default_text}]: ').strip().lower()
        if not value:
            return default
        if value in {'y', 'yes', 'ν', 'ναι', 'nai'}:
            return True
        if value in {'n', 'no', 'ο', 'oxi', 'όχι'}:
            return False
        print('  Δώσε y ή n.')


def ask_choice(prompt: str, options: list[tuple[str, str]], default_index: int = 0) -> str:
    print(f'\n{prompt}')
    for idx, (_, label) in enumerate(options, 1):
        marker = ' (default)' if idx - 1 == default_index else ''
        print(f'  [{idx}] {label}{marker}')
    while True:
        raw = input('Επιλογή: ').strip()
        if not raw:
            return options[default_index][0]
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1][0]
        print('  Μη έγκυρη επιλογή.')


def parse_csv(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(',') if x.strip()]


def unique_keep_order(items: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = str(item or '').strip()
        if not clean or clean in seen:
            continue
        result.append(clean)
        seen.add(clean)
    return result


def check_python() -> None:
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 9):
        fail(f'Απαιτείται Python 3.9+. Τρέχουσα έκδοση: {major}.{minor}')
    ok(f'Python {major}.{minor}.{sys.version_info.micro}')


def ensure_pyinstaller() -> str:
    try:
        import PyInstaller
        version = PyInstaller.__version__
        ok(f'PyInstaller {version}')
        return version
    except ImportError:
        pass

    step('Εγκατάσταση/αναβάθμιση PyInstaller…')
    run([sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--upgrade'])
    import PyInstaller
    importlib.reload(PyInstaller)
    version = PyInstaller.__version__
    ok(f'PyInstaller {version} εγκαταστάθηκε')
    return version


def has_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except Exception:
        return False


def find_upx() -> str | None:
    return shutil.which('upx')


def find_sources(script_dir: Path) -> list[Path]:
    this_file = Path(__file__).resolve()
    candidates = [
        f for f in sorted(script_dir.glob('*.py'), key=lambda p: p.name.lower())
        if f.resolve() != this_file and not f.name.lower().startswith('build_exe')
    ]
    preferred = [f for f in candidates if re.search('ollama', f.name, re.IGNORECASE)]
    return preferred or candidates


def choose_source(script_dir: Path) -> Path:
    candidates = find_sources(script_dir)
    if not candidates:
        fail('Δεν βρέθηκαν .py αρχεία για build στον ίδιο φάκελο.')
    print('\nΔιαθέσιμα αρχεία πηγής:\n')
    for i, c in enumerate(candidates, 1):
        size_kb = c.stat().st_size / 1024
        print(f'  [{i}] {c.name}  ({size_kb:.1f} KB)')
    while True:
        raw = input(f'\nΕπίλεξε source file [1-{len(candidates)}] (default 1): ').strip()
        if not raw:
            return candidates[0].resolve()
        if raw.isdigit() and 1 <= int(raw) <= len(candidates):
            return candidates[int(raw) - 1].resolve()
        print('  Μη έγκυρη επιλογή.')


def _handle_remove_error(func, path, excinfo) -> None:
    err = excinfo if isinstance(excinfo, BaseException) else excinfo[1]
    path_obj = Path(path)
    if isinstance(err, PermissionError):
        print()
        warn(f'Το αρχείο ή ο φάκελος είναι κλειδωμένος και δεν μπορεί να διαγραφεί: {path_obj}')
        print('     Συνήθως αυτό σημαίνει ότι το παλιό .exe είναι ακόμη ανοιχτό.')
        while True:
            action = input("     Κλείσ' το και πάτησε [R]etry, ή [A]bort για ακύρωση build: ").strip().lower()
            if action in {'', 'r', 'retry'}:
                try:
                    func(path)
                    return
                except PermissionError:
                    warn('     Παραμένει κλειδωμένο.')
                    continue
                except Exception as retry_exc:
                    fail(f'Αποτυχία διαγραφής του {path_obj}: {retry_exc}')
            if action in {'a', 'abort'}:
                fail('Το build ακυρώθηκε επειδή το παλιό εκτελέσιμο είναι ακόμη ανοιχτό.', 2)
            print('     Δώσε R ή A.')
    raise err


def _remove_target(path: Path) -> bool:
    if not path.exists():
        return False
    if path.is_dir():
        shutil.rmtree(path, onexc=_handle_remove_error)
    else:
        path.unlink()
    return True


def clean_previous(script_dir: Path, app_name: str) -> None:
    targets = [script_dir / 'build', script_dir / 'dist', script_dir / f'{app_name}.spec']
    cleaned = False
    for target in targets:
        try:
            cleaned = _remove_target(target) or cleaned
        except FileNotFoundError:
            continue
    if cleaned:
        ok('Καθαρίστηκαν προηγούμενα builds')
    else:
        ok('Δεν υπήρχαν προηγούμενα build artifacts')


def scan_source_import_roots(source: Path) -> list[str]:
    """Σκανάρει το source file και επιστρέφει τα top-level import roots."""
    try:
        tree = ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
    except Exception as exc:
        warn(f'Αποτυχία AST scan στο {source.name}: {exc}')
        return []

    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.append(alias.name.split('.', 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.append(node.module.split('.', 1)[0])
    return unique_keep_order(roots)


def distribution_name_for_import(import_name: str) -> str | None:
    """Προσπαθεί να βρει το pip/distribution name για ένα import root."""
    try:
        from importlib import metadata as importlib_metadata
    except Exception:
        return None

    lowered = str(import_name or '').strip().lower()
    if not lowered:
        return None

    explicit = {
        'fitz': 'PyMuPDF',
        'pymupdf': 'PyMuPDF',
        'pypdf': 'pypdf',
        'pyinstaller': 'pyinstaller',
    }
    if lowered in explicit:
        return explicit[lowered]

    try:
        packages_map = importlib_metadata.packages_distributions()
    except Exception:
        packages_map = {}

    candidates = packages_map.get(import_name) or packages_map.get(lowered) or []
    if candidates:
        return str(candidates[0])
    return None


def installed_distribution_with_version(distribution_name: str) -> str:
    """Επιστρέφει distribution pin μορφής name==version όταν υπάρχει."""
    try:
        from importlib import metadata as importlib_metadata
        version = importlib_metadata.version(distribution_name)
        return f'{distribution_name}=={version}'
    except Exception:
        return distribution_name


def resolve_build_assets(config: BuildConfig) -> ResolvedBuildAssets:
    """Υπολογίζει hidden imports, collect-all packages και requirements manifest."""
    detected_import_roots = scan_source_import_roots(config.source)

    hidden: list[str] = list(DEFAULT_STDLIB_HIDDEN_IMPORTS)
    hidden.extend(config.extra_hidden_imports)
    collect_all: list[str] = []
    detected_packages: list[str] = []

    detected_import_set = set(detected_import_roots)

    for rule in PACKAGE_RULES.values():
        import_names = [str(x) for x in rule.get('import_names', [])]
        if not any(name in detected_import_set for name in import_names):
            continue
        if not any(has_module(name) for name in import_names):
            warn(f"Το package {rule.get('display_name', import_names[0])} ανιχνεύθηκε στο source αλλά δεν είναι εγκατεστημένο στο τρέχον Python env.")
            continue
        hidden.extend([str(x) for x in rule.get('hidden_imports', [])])
        collect_all.extend([str(x) for x in rule.get('collect_all', [])])
        detected_packages.append(str(rule.get('display_name', import_names[0])))

    # Requirements manifest: μόνο τρίτα packages + PyInstaller.
    req_lines: list[str] = []
    runtime_distributions: list[str] = []

    # Πάντα include το pyinstaller επειδή είναι build dependency.
    runtime_distributions.append('pyinstaller')

    for import_root in detected_import_roots:
        dist_name = distribution_name_for_import(import_root)
        if not dist_name:
            continue
        normalized = dist_name.lower()
        if normalized in {'python', 'setuptools', 'pip'}:
            continue
        runtime_distributions.append(dist_name)

    for line in unique_keep_order(installed_distribution_with_version(name) for name in runtime_distributions):
        req_lines.append(line)

    return ResolvedBuildAssets(
        hidden_imports=unique_keep_order(hidden),
        collect_all_packages=unique_keep_order(collect_all),
        detected_packages=unique_keep_order(detected_packages),
        detected_import_roots=detected_import_roots,
        requirements_lines=req_lines,
    )


def write_requirements_manifest(script_dir: Path, config: BuildConfig, assets: ResolvedBuildAssets) -> Path:
    """Γράφει manifest με τα packages που χρειάζεται πλέον η εφαρμογή."""
    out_path = script_dir / f'{config.app_name}_requirements.txt'
    lines: list[str] = [
        '# Requirements manifest generated by build_exe_interactive_v2.py',
        f'# Source: {config.source.name}',
        '#',
        '# Σημείωση: για το server-side PDF export χρειάζεται επίσης εγκατεστημένος',
        '# Microsoft Edge, Google Chrome ή Chromium στο λειτουργικό σύστημα.',
        '',
    ]
    lines.extend(assets.requirements_lines or ['pyinstaller'])
    out_path.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    return out_path


def build(config: BuildConfig, script_dir: Path, assets: ResolvedBuildAssets) -> Path:
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        f'--name={config.app_name}',
        '--clean',
        '--noconfirm',
    ]
    cmd.append('--onefile' if config.one_file else '--onedir')
    cmd.append('--console' if config.console else '--windowed')
    if config.icon_path:
        cmd += ['--icon', config.icon_path]
    if config.use_upx:
        for item in config.upx_excludes:
            cmd.append(f'--upx-exclude={item}')
    else:
        cmd.append('--noupx')
    for hidden_import in assets.hidden_imports:
        cmd.append(f'--hidden-import={hidden_import}')
    for package_name in assets.collect_all_packages:
        cmd.append(f'--collect-all={package_name}')
    cmd.append(str(config.source))

    print(f'\n{SEP2}')
    step('Έναρξη build…')
    print(SEP2)
    run(cmd, cwd=str(script_dir))

    if config.one_file:
        exe = script_dir / 'dist' / f'{config.app_name}.exe'
    else:
        exe = script_dir / 'dist' / config.app_name / f'{config.app_name}.exe'
    return exe


def print_summary(config: BuildConfig, assets: ResolvedBuildAssets, upx_found: str | None) -> None:
    print(f'\n{SEP}')
    print('  Σύνοψη build')
    print(SEP2)
    print(f'  Πηγή                 : {config.source.name}')
    print(f'  Όνομα εφαρμογής      : {config.app_name}')
    print(f"  Build mode           : {('onefile' if config.one_file else 'onedir')}")
    print(f"  Terminal window      : {('Ναι' if config.console else 'Όχι')}")
    print(f"  Εικονίδιο            : {config.icon_path or 'Κανένα'}")
    print(f"  UPX                  : {('Ναι' if config.use_upx else 'Όχι')}")
    if upx_found:
        print(f'  UPX path             : {upx_found}')
    if config.use_upx:
        print(f"  UPX excludes         : {(', '.join(config.upx_excludes) if config.upx_excludes else 'Κανένα')}")
    print(f"  Καθαρισμός build     : {('Ναι' if config.clean_before_build else 'Όχι')}")
    print(f"  Ανιχνευμένα imports  : {(', '.join(assets.detected_import_roots) if assets.detected_import_roots else 'Κανένα')}")
    print(f"  Runtime packages     : {(', '.join(assets.detected_packages) if assets.detected_packages else 'Κανένα third-party package')}")
    print(f"  Hidden imports       : {(', '.join(assets.hidden_imports) if assets.hidden_imports else 'Κανένα')}")
    print(f"  Collect-all packages : {(', '.join(assets.collect_all_packages) if assets.collect_all_packages else 'Κανένα')}")
    print(f"  Requirements manifest: {('Ναι' if config.write_requirements_manifest else 'Όχι')}")
    print(f"  Run μετά το build    : {('Ναι' if config.run_after_build else 'Όχι')}")
    print(f"  Άνοιγμα dist folder  : {('Ναι' if config.open_dist_after_build else 'Όχι')}")
    print(SEP)


def configure(script_dir: Path) -> tuple[BuildConfig, ResolvedBuildAssets]:
    step('Εύρεση αρχείου πηγής…')
    source = choose_source(script_dir)
    ok(f'Πηγή: {source.name}')

    default_app_name = Path(source).stem
    app_name = ask_text('Όνομα εφαρμογής / exe', default_app_name or DEFAULT_APP_NAME)
    mode = ask_choice(
        'Επίλεξε τύπο build:',
        [
            ('onefile', 'Ένα μόνο .exe (ευκολότερη διανομή, πιο βαρύ startup)'),
            ('onedir', 'Φάκελος dist με exe + αρχεία (πιο σταθερό για apps με αρχεία)'),
        ],
        default_index=1,
    )
    console_mode = ask_choice(
        'Θες terminal window;',
        [('console', 'Ναι, να φαίνεται terminal/logs'), ('windowed', 'Όχι, καθαρό GUI χωρίς terminal')],
        default_index=0,
    )

    icon_path = ask_text('Διαδρομή εικονιδίου .ico (άφησέ το κενό αν δεν θες)', '')
    if icon_path:
        icon_candidate = Path(icon_path)
        if not icon_candidate.is_absolute():
            icon_candidate = (script_dir / icon_candidate).resolve()
        if not icon_candidate.exists():
            warn(f'Το icon δεν βρέθηκε: {icon_candidate}. Θα αγνοηθεί.')
            icon_path = ''
        else:
            icon_path = str(icon_candidate)

    upx_path = find_upx()
    use_upx = False
    upx_excludes: list[str] = []
    if upx_path:
        use_upx = ask_yes_no('Βρέθηκε UPX. Να χρησιμοποιηθεί συμπίεση UPX;', False)
        if use_upx:
            raw_excludes = ask_text('UPX excludes (comma separated)', ', '.join(DEFAULT_UPX_EXCLUDES))
            upx_excludes = parse_csv(raw_excludes)
    else:
        ok('UPX δεν βρέθηκε — θα χρησιμοποιηθεί --noupx')

    clean_before = ask_yes_no('Να καθαριστούν προηγούμενα build/dist/spec;', True)
    extra_hidden_imports = parse_csv(ask_text('Extra hidden imports (comma separated, προαιρετικό)', ''))
    write_requirements = ask_yes_no('Να γραφτεί και requirements manifest με τα πακέτα της εφαρμογής;', True)
    run_after = ask_yes_no('Να τρέξει το exe μόλις ολοκληρωθεί το build;', False)
    open_dist = ask_yes_no('Να ανοίξει ο φάκελος dist μετά το build;', False)

    config = BuildConfig(
        source=source,
        app_name=app_name,
        one_file=mode == 'onefile',
        console=console_mode == 'console',
        icon_path=icon_path,
        use_upx=use_upx,
        upx_excludes=upx_excludes,
        clean_before_build=clean_before,
        open_dist_after_build=open_dist,
        run_after_build=run_after,
        extra_hidden_imports=extra_hidden_imports,
        write_requirements_manifest=write_requirements,
    )

    assets = resolve_build_assets(config)
    print_summary(config, assets, upx_path)
    if not ask_yes_no('Να ξεκινήσει το build με αυτές τις ρυθμίσεις;', True):
        fail('Το build ακυρώθηκε από τον χρήστη.', 0)
    return config, assets


def open_in_explorer(path: Path) -> None:
    if sys.platform.startswith('win'):
        os.startfile(str(path))
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', str(path)])
    else:
        subprocess.Popen(['xdg-open', str(path)])


def print_result(exe: Path, source: Path, manifest_path: Path | None) -> None:
    if not exe.exists():
        fail('Το εκτελέσιμο δεν δημιουργήθηκε.\nΈλεγξε τα μηνύματα του PyInstaller παραπάνω.')
    size_mb = exe.stat().st_size / (1024 * 1024)
    print(f'\n{SEP}')
    print('  ✅  Build επιτυχές!')
    print(SEP2)
    print(f'  📁  Αρχείο  : {exe}')
    print(f'  📦  Μέγεθος : {size_mb:.1f} MB')
    print(f'  🐍  Πηγή    : {source.name}')
    if manifest_path is not None:
        print(f'  🧾  Requirements : {manifest_path}')
    print(SEP2)
    print('  🚀  Εκτέλεση:')
    print(f'        {exe.name}')
    print(SEP)


def main() -> None:
    print(f'\n{SEP}')
    print(f'  Ollama Cloud Chat Studio v{APP_VERSION} — Interactive Build Wizard')
    print(f'  Python: {sys.executable}')
    print(SEP)

    script_dir = Path(__file__).resolve().parent
    check_python()

    step('Έλεγχος PyInstaller…')
    ensure_pyinstaller()

    config, assets = configure(script_dir)

    if config.clean_before_build:
        step('Καθαρισμός προηγούμενων builds…')
        clean_previous(script_dir, config.app_name)

    manifest_path: Path | None = None
    if config.write_requirements_manifest:
        step('Γραφή requirements manifest…')
        manifest_path = write_requirements_manifest(script_dir, config, assets)
        ok(f'Γράφτηκε: {manifest_path.name}')

    exe = build(config, script_dir, assets)
    print_result(exe, config.source, manifest_path)

    if config.open_dist_after_build:
        dist_dir = exe.parent if exe.parent.exists() else script_dir / 'dist'
        open_in_explorer(dist_dir)
    if config.run_after_build:
        step('Εκτέλεση του exe…')
        subprocess.Popen([str(exe)], cwd=str(exe.parent))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n  ⛔  Διακόπηκε από τον χρήστη.\n')
        raise SystemExit(130)
