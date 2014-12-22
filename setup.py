import os
import shutil

from setuptools import setup, find_packages

setup(name='pomodorino',
      version='0.2',
      description='A simple pomodoro application written in Python',
      author='prjw',
      author_email='prjw@posteo.de',
      url='http://www.github.com/prjw/pomodorino',
      license='GPL',
      packages=['pomodorino'],
      scripts=["pomo"]
     )
     
     
shutil.copyfile("data/pomodorino.desktop", "/usr/share/applications/pomodorino.desktop")     
shutil.copyfile("data/pomodorino.png", "/usr/share/icons/pomodorino.png")
os.makedirs("/usr/share/pomodorino", exist_ok=True)
shutil.copyfile("data/ring.wav", "/usr/share/pomodorino/ring.wav")
shutil.copyfile("data/strings.xml", "/usr/share/pomodorino/strings.xml") 
     
shutil.rmtree('dist/', True)
shutil.rmtree('pomodorino.egg-info/', True)
shutil.rmtree('build/', True)
shutil.rmtree('pomodorino/__pycache__/', True)
