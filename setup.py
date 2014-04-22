from setuptools import setup, find_packages
import shutil


setup(name='pomodorian',
      version='0.0',
      description='A simple pomodoro application written in Python',
      author='prjw',
      author_email='prjw@posteo.de',
      url='http://www.github.com/prjw/pomodorian',
      license='GPL',
      packages=['pomodorian'],
      scripts=["pomo"]
     )
     
shutil.copyfile("data/pomodorian.desktop", "/usr/share/applications/pomodorian.desktop")     
shutil.copyfile("data/pomodorian.png", "/usr/share/icons/pomodorian.png")     
     
print("Cleanup? [y/n]: ")
clean = input();
while clean != 'y' and clean != 'n':
    print("Cleanup? [y/n]: ")
    clean = input();
    
if clean == 'y':
    shutil.rmtree('dist/')
    shutil.rmtree('pomodorian.egg-info/')
    shutil.rmtree('build/')
    shutil.rmtree('pomodorian/__pycache__/')
