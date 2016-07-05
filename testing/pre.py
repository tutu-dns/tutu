import shutil
import os.path

if os.path.isfile('tutu.cfg'):
  shutil.move('tutu.cfg', 'tutu.cfg.orig');
shutil.copy('testing/tutu.cfg', 'tutu.cfg');
