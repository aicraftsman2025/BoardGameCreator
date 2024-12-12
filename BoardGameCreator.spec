# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import os

block_cipher = None

# Determine the platform
is_windows = sys.platform.startswith('win')
is_mac = sys.platform.startswith('darwin')
is_linux = sys.platform.startswith('linux')

# Collect all necessary data files
datas = [
    ('assets_static', 'assets_static'),
    ('views', 'views'),
    ('controllers', 'controllers'),
    ('models', 'models'),
    ('utils', 'utils'),
]

# Collect all required modules
hiddenimports = [
    'PIL._tkinter_finder',
    'customtkinter',
    'tkinter',
    'tkinter.ttk',
] + collect_submodules('customtkinter')

# Platform specific configurations
if is_windows:
    icon_file = 'assets_static/icons/app_icon.ico'
elif is_mac:
    icon_file = 'assets_static/icons/app_icon.icns'
else:  # Linux
    icon_file = 'assets_static/icons/app_icon.png'

a = Analysis(
    ['app.py'],  # Main script
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

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

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
    console=False,  # Set to True if you want to see console output
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

# macOS specific bundle configuration
if is_mac:
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
            'CFBundleSignature': '????',
            'LSMinimumSystemVersion': '10.13.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSApplicationCategoryType': 'public.app-category.graphics-design',
        },
    ) 