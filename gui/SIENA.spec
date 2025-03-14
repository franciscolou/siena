# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['auth.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('gui_widgets.py', 'gui_widgets.py'), ('gui_tools.py', 'gui_tools.py'), ('gui.py', 'gui.py')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SIENA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\images\\SIENA.ico'],
)
