# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Cloud Storage Server
Creates a single executable for the Flask server
"""

block_cipher = None

a = Analysis(
    ['../server/app.py'],
    pathex=['..'],
    binaries=[],
    datas=[
        ('../config.yaml', '.'),
        ('../shared', 'shared'),
    ],
    hiddenimports=[
        'server',
        'server.app',
        'server.auth',
        'server.config',
        'server.models',
        'server.storage',
        'shared.constants',
        'flask',
        'flask_cors',
        'flask_sqlalchemy',
        'sqlalchemy',
        'jwt',
        'bcrypt',
        'yaml',
        'werkzeug',
        'click',
        'itsdangerous',
        'jinja2',
        'markupsafe',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'pytest', 'tkinter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CloudStorageServer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep console for server logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon=../assets/server_icon.ico if you have one
)
