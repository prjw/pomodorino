from setuptools import setup, find_packages
import shutil

DEV = True

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
     
     
print("Install icon and desktop entries? [y/n]: ")
choice = input();
while choice != 'y' and choice != 'n':
    print("Install icon and desktop entries? [y/n]: ")
    choice = input();
    
if choice == 'y':
    shutil.copyfile("data/pomodorian.desktop", "/usr/share/applications/pomodorian.desktop")     
    shutil.copyfile("data/pomodorian.png", "/usr/share/icons/pomodorian.png")     
     
if DEV == True:
    print("Cleanup this directory? [y/n]: ")
    choice = input();
    while choice != 'y' and choice != 'n':
        print("Cleanup this directory? [y/n]: ")
        choice = input();
        
    if choice == 'y':
        shutil.rmtree('dist/', True)
        shutil.rmtree('pomodorian.egg-info/', True)
        shutil.rmtree('build/', True)
        shutil.rmtree('pomodorian/__pycache__/', True)
