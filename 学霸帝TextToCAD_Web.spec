# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 路径设置
WORKDIR = os.path.abspath(os.getcwd())
# python-embed 在上级目录
PARENT_DIR = os.path.dirname(WORKDIR)
EMBED_DIR = os.path.join(PARENT_DIR, "python-embed")
SITE_PACKAGES = os.path.join(EMBED_DIR, "Lib", "site-packages")

# 查找 lib3mf.dll
lib3mf_dll = os.path.join(SITE_PACKAGES, "lib3mf", "lib3mf.dll")
if not os.path.exists(lib3mf_dll):
    lib3mf_dll = os.path.join(SITE_PACKAGES, "lib3mf-", "lib3mf", "lib3mf.dll")

print(f"Workdir: {WORKDIR}")
print(f"Embed dir: {EMBED_DIR}")
print(f"Site-packages: {SITE_PACKAGES}")
print(f"lib3mf.dll: {lib3mf_dll} exists={os.path.exists(lib3mf_dll)}")

a = Analysis(
    ["web_gui_v3.py"],
    pathex=[WORKDIR],
    binaries=[
        (lib3mf_dll, "lib3mf"),
    ],
    datas=[],
    hiddenimports=[
        "build123d",
        "build123d.buildpart",
        "build123d.buildline",
        "build123d.exporters",
        "build123d.topology",
        "build123d.algebre",
        "build123d.geometry",
        "cadquery_ocp",
        "vtk",
        "numpy",
        "scipy",
        "matplotlib",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="学霸帝TextToCAD_Web",
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
)
