# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Main.py'],
             pathex=['Z:\\GitHub\\Python\\PDF_Manager'],
             binaries=[],
             datas=[('Z:\\GitHub\\Python\\PDF_Manager\\pdf.ico', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ASSA PDF Merger',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, icon='Z:\\GitHub\\Python\\PDF_Manager\\pdf.ico' )
