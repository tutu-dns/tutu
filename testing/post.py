import shutil
import os.path

if os.path.isfile('tutu.cfg.orig'):
  shutil.move('tutu.cfg.orig', 'tutu.cfg');
