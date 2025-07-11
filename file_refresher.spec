# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['file_refresher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        'rich',
        'yaml',
        'csv',
        'logging',
        'datetime',
        'pathlib',
        'collections',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'PIL.ImageTk',
        'PIL.ImageWin',
    ],
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
    name='file_refresher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)