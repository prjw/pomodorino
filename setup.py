import os
import shutil

from setuptools import setup, find_packages

setup(name='pomodorino',
      version='0.3',
      description='A simple pomodoro application for time-tracking purposes.',
      author='prjw',
      author_email='prjw@posteo.de',
      url='http://www.github.com/prjw/pomodorino',
      license='GPL',
      packages=['pomodorino'],
      scripts=["pomo"]
     )

print("\ncreating: /usr/share/pomodorino")
os.makedirs("/usr/share/pomodorino", exist_ok=True)

data = {"data/pomodorino.desktop": "/usr/share/applications/pomodorino.desktop",
        "data/pomodorino.png": "/usr/share/icons/pomodorino.png",
        "data/ring.wav": "/usr/share/pomodorino/ring.wav",
        "data/strings.xml": "/usr/share/pomodorino/strings.xml"}

for res in data:
    print("copying " + data[res])
    shutil.copyfile(res, data[res])
