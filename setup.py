import subprocess as sh
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

def inject_fig_script():
    with open('./.figure_control.m', 'r') as infile:
        with open('./figure_control.m', 'w') as outfile:
            contents = infile.read()
            contents = contents.replace('{pypath}', '"{}"'.format(sh.check_output('which figure-control', shell=True).decode('utf-8').strip()))
            outfile.write(contents)

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        inject_fig_script()

class DevelopInstallCommand(develop):
    def run(self):
        develop.run(self)
        inject_fig_script()

setup(
    cmdclass={'install': PostInstallCommand,
              'develop': DevelopInstallCommand},
    name="figure_control",
    version="0.1",
    packages=find_packages(),

    # metadata for upload to PyPI
    author="Winthrop Gillis",
    author_email="win.gillis@gmail.com",
    description="A tool to keep track of which code commit generated which figures",
    keywords="version-control figure git",
    url="https://github.com/wingillis/figure-control",   # project home page, if any
    install_requires=['click', 'ruamel.yaml', 'GitPython'],
    entry_points={
        'console_scripts': ['figure-control = figure_control.main:main']
    }

    # could also include long_description, download_url, classifiers, etc.
)
