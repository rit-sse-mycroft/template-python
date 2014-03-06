"""
main.py
Main module for Mycroft
Handles running scripts for things like app initialization
"""

import sys
import os
import re


def main():
    if 'init' in sys.argv:
        print("Initializing application.")

        name = input("App name: ")
        displayname = input("Display name: ")
        instanceid = input("Instance ID: ")
        description = input("Description: ")

        dir_ = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(dir_, 'templates')
        template = os.path.join(template_dir, 'manifest.json.template')
        manifest = ''
        with open(template) as f:
            manifest = f.read()

        manifest = manifest.replace("$NAME", name)
        manifest = manifest.replace("$DISPLAYNAME", displayname)
        manifest = manifest.replace("$INSTANCEID", instanceid)
        manifest = manifest.replace("$DESCRIPTION", description)
        with open('manifest.json', mode='w') as f:
            f.write(manifest)

        app_template = os.path.join(template_dir, 'app.py.template')
        app = ''
        with open(app_template) as f:
            app = f.read()

        classname = re.sub(r'[\W\d]', '', name)
        classname = classname[0].title() + classname[1:]
        app = app.replace("$CLASSNAME", classname)
        app = app.replace("$NAME", name)

        with open(classname+'.py', mode='w') as f:
            f.write(app)

    else:
        print("USAGE: python -m mycroft init")

if __name__ == '__main__':
    main()
