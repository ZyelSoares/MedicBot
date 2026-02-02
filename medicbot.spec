# PyInstaller spec - gera o .exe do MedicBot (npm run ship)
# Inclui MedicBot.ps1 na pasta do executável para a manutenção funcionar.

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['medicbot.py'],
    pathex=[],
    binaries=[],
    datas=[('MedicBot.ps1', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MedicBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # sem janela do terminal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
