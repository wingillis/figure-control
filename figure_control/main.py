#!/usr/bin/env python
'''This is a python package and cli script to manage figure production based
on the commit hash for the repository that is generating the figures.

Author: wingillis (https://github.com/wingillis) - Winthrop Gillis
'''
import sys
import click
from figure_control.base import FigureControl

def excepthook(t, value, traceback):
    print(value)


@click.command()
@click.option('--repo', '-p', default='.', type=click.Path(), help='Path to the repo to reference')
@click.option('--final', '-f', is_flag=True, help='Is this a final figure? (Defaults to exploratory figure generation)')
@click.option('--config', '-c', default=None type=str)
def main(repo, final, config):
    sys.excepthook = excepthook

    fc = FigureControl(repo, config, final)
    save_path = fc.createSavePath()

    click.echo(save_path)


if __name__ == '__main__':
    main()
