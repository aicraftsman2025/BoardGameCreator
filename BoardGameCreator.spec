# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import os
import sqlite3

block_cipher = None

# Determine the platform
is_windows = sys.platform.startswith('win')
is_mac = sys.platform.startswith('darwin')
is_linux = sys.platform.startswith('linux')

console=True

# Create initial database if it doesn't exist
db_path = 'boardgame.db'
if not os.path.exists(db_path):
    print("Creating initial database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Add your initial tables here
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Collect all files from assets_static recursively
assets_static_files = []
for root, dirs, files in os.walk('assets_static'):
    for file in files:
        source_path = os.path.join(root, file)
        target_path = os.path.join(os.path.relpath(root), file)
        assets_static_files.append((source_path, os.path.dirname(target_path)))

# Combine with other data files
datas = assets_static_files + [
    ('views', 'views'),
    ('controllers', 'controllers'),
    ('models', 'models'),
    ('utils', 'utils'),
    (db_path, '.'),  # Include the database file in the root of the bundle
]

# Debug print to verify assets are being collected
print("Assets being bundled:")
for source, target in assets_static_files:
    print(f"Source: {source} -> Target: {target}")
print(f"Database being bundled: {db_path}")

# Collect all required modules
hiddenimports = [
    'PIL._tkinter_finder',
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
    'pkg_resources.py2_warn',
    'packaging.version',
    'packaging.specifiers',
    'packaging.requirements'
] + collect_submodules('customtkinter')

# Platform specific configurations
if is_windows:
    icon_file = 'assets_static/icons/app_icon.ico'
elif is_mac:
    icon_file = 'assets_static/icons/app_icon.icns'
else:  # Linux
    icon_file = 'assets_static/icons/app_icon.png'

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

if is_mac:
    # Remove system Tcl/Tk to use bundled ones
    a.binaries = [b for b in a.binaries if not b[0].startswith('tcl')]
    a.binaries = [b for b in a.binaries if not b[0].startswith('tk')]
    a.binaries = [b for b in a.binaries if not b[0].startswith('_tkinter')]

    # Debug version (console enabled)
    exe_debug = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='BoardGameCreator_debug',
        debug=True,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=True,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )

    # Release version (no console)
    exe_release = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='BoardGameCreator',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )

    coll = COLLECT(
        exe_release,  # Use release version for the app
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='BoardGameCreator'
    )

    app = BUNDLE(
        coll,
        name='BoardGameCreator.app',
        icon=icon_file,
        bundle_identifier='com.boardgamecreator',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'CFBundleName': 'BoardGameCreator',
            'CFBundleDisplayName': 'Board Game Creator',
            'CFBundleIdentifier': 'com.boardgamecreator',
            'CFBundlePackageType': 'APPL',
            'LSMinimumSystemVersion': '10.13.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSApplicationCategoryType': 'public.app-category.graphics-design',
            'LSEnvironment': {
                'PATH': '/usr/bin:/bin:/usr/sbin:/sbin',
                'PYTHONPATH': '@executable_path/../Resources',
                'DYLD_LIBRARY_PATH': '@executable_path/../Frameworks',
                'DYLD_FRAMEWORK_PATH': '@executable_path/../Frameworks'
            }
        }
    )
else:
    # Windows/Linux configurations remain the same
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='BoardGameCreator',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,  # GUI version for normal use
        disable_windowed_traceback=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=icon_file
    )

    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='BoardGameCreator'
    ) 