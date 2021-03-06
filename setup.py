import os
import sys
from setuptools import setup, find_packages

os.chdir(os.path.dirname(os.path.realpath(__file__)))

VERSION_PATH = os.path.join('athanor', 'VERSION.txt')
OS_WINDOWS = os.name == "nt"

ALL_MODULES = ('athanor', 'athanor_ainfo', 'athanor_mail', 'athanor_awho', 'athanor_bbs', 'athanor_channels',
               'athanor_cmail', 'athanor_cwho', 'athanor_district', 'athanor_fclist', 'athanor_watch', 'athanor_groups',
               'athanor_guest', 'athanor_jobs', 'athanor_logintrack', 'athanor_meetme', 'athanor_navigation',
               'athanor_page', 'athanor_pennmush', 'athanor_radio', 'athanor_scene', 'athanor_staff')

def get_requirements():
    """
    To update the requirements for Evennia, edit the requirements.txt
    file, or win_requirements.txt for Windows platforms.
    """
    filename = 'requirements.txt'
    with open(filename, 'r') as f:
        req_lines = f.readlines()
    reqs = []
    for line in req_lines:
        # Avoid adding comments.
        line = line.split('#')[0].strip()
        if line:
            reqs.append(line)
    return reqs


def get_scripts():
    """
    Determine which executable scripts should be added. For Windows,
    this means creating a .bat file.
    """
    pass
    """
    if OS_WINDOWS:
        batpath = os.path.join("bin", "windows", "evennia.bat")
        scriptpath = os.path.join(sys.prefix, "Scripts", "evennia_launcher.py")
        with open(batpath, "w") as batfile:
            batfile.write("@\"%s\" \"%s\" %%*" % (sys.executable, scriptpath))
        return [batpath, os.path.join("bin", "windows", "evennia_launcher.py")]
    else:
        return [os.path.join("bin", "unix", "evennia")]
    """


def get_version():
    """
    When updating the Evennia package for release, remember to increment the
    version number in evennia/VERSION.txt
    """
    return open(VERSION_PATH).read().strip()


def package_data():
    """
    By default, the distribution tools ignore all non-python files.

    Make sure we get everything.
    """
    file_set = []
    for modpath in ALL_MODULES:
        for root, dirs, files in os.walk(modpath):
            for f in files:
                if '.git' in f.split(os.path.normpath(os.path.join(root, f))):
                    # Prevent the repo from being added.
                    continue
                file_name = os.path.relpath(os.path.join(root, f), modpath)
                file_set.append(file_name)
    return file_set


# setup the package
setup(
    name='athanor',
    version=get_version(),
    author="Volund",
    maintainer="Volund",
    maintainer_email="volundmush@gmail.com",
    url="https://github.com/volundmush/athanor",
    description='Code for running an Evennia-based Themed Freeform Roleplay game.',
    packages=find_packages(),
    scripts=get_scripts(),
    install_requires=get_requirements(),
    package_data={'': package_data()},
    zip_safe=False
)
