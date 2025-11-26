# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Cloud Storage Client
Creates a single executable with GUI
"""

block_cipher = None

a = Analysis(
    ['../client/gui/main_window.py'],
    pathex=['..'],
    binaries=[],
    datas=[
        ('../config.yaml', '.'),
        ('../shared', 'shared'),
    ],
    hiddenimports=[
        'client',
        'client.api_client',
        'client.auth_manager', 
        'client.crypto_handler',
        'client.gui',
        'client.gui.login_dialog',
        'client.gui.file_manager',
        'client.gui.main_window',
        'shared.constants',
        'tkinter',
        'yaml',
        'requests',
        'Crypto',
        'Crypto.Cipher',
        'Crypto.PublicKey',
        'Crypto.Random',
        'cryptography',
        'PIL',
        '_tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'pytest'],
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
    name='CloudStorageClient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon=../assets/icon.ico if you have one
)
