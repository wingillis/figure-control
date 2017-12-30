#!/usr/bin/env python
'''This is a python package and cli script to manage figure production based
on the commit hash for the repository that is generating the figures.

Author: wingillis (https://github.com/wingillis) - Winthrop Gillis
'''
import os
import sys
import stat
from os.path import join
from glob import glob
import subprocess as sh
import shutil
import click
import yaml

def excepthook(t, value, traceback):
    print(value)

def clean_path(repo):
    repo = os.path.expanduser(repo)
    repo = os.path.abspath(repo)
    return repo

@click.command()
@click.option('--repo', '-p', default='.', type=click.Path(), help='Path to the repo to reference')
@click.option('--final', '-f', is_flag=True)
def main(repo, final):
    sys.excepthook = excepthook

    repo = clean_path(repo)
    assert os.path.exists(repo), 'Sorry repo does not exist, ' + repo
    assert is_git_repo(repo), 'Specified path is not a git repository: ' + repo
    # the config file should be in the code directory
    options = load_config(repo)

    assert 'path' in options, 'No destination directory specified under `path` keyword'
    base_path = clean_path(options['path'])

    if repo_is_dirty(repo):
        click.echo('Your repo: {}\n\thas some unstaged changes, it is recommended that you commit them'.format(repo))

    commit_hash = generate_commit_hash(repo)
    save_path = assemble_save_path(repo, base_path, commit_hash, final)
    # check if save_path exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        click.echo('Created directory for saving')

    if options.get('executable', False):
        # make an executable that goes to the code folder and specific commit
        exec_contents = generate_show_script(repo, commit_hash)
        exec_file_path = join(save_path, 'goto-commit-{}'.format(commit_hash))
        with open(exec_file_path, 'w') as exec_file:
            exec_file.write(exec_contents)
        st = os.stat(exec_file_path)
        os.chmod(exec_file_path, st.st_mode | stat.S_IEXEC)

    click.echo(save_path)

def is_git_repo(path):
    return os.path.exists(join(path, '.git'))

def load_config(repo):
    conf_glob = '*.yaml'
    # the config file should be in the code directory
    conf = glob(join(repo, conf_glob))
    assert len(conf) > 0, 'No config file found'
    conf = conf[0]
    with open(conf, 'r') as f:
        options = yaml.load(f)
    assert options is not None, 'Nothing seems to be in the config file ' + conf
    assert 'figure-control' in options, 'Required key figure-control not in config file: ' + conf
    return options['figure-control']

def assemble_save_path(repo_path, base_path, commit_hash, is_final_fig):
    # subdir is based on type of analysis happening
    dirtype = 'final' if is_final_fig else 'exploratory'
    return join(base_path, commit_hash, dirtype)

def repo_is_dirty(repo_path):
    output = sh.check_output('git -C "{}" status --porcelain'.format(repo_path), shell=True)
    return output != b''

def generate_commit_hash(repo):
    return sh.check_output('git -C "{}" rev-parse HEAD | cut -c1-7'.format(repo),
                           shell=True).decode('utf-8').strip()

# return a pickled save function, so that any language can pass the pickled
# save function as a parameter, here we can unpickle it, and use it to save
# the figures - this won't work, but the idea could be interesting

# maybe add a function to create a config file for a repo

# if there is a change in the code that hasn't been committed warn the user
# and auto-commit code
# save files generated with unstaged code into a directory that contains the
# most recently committed code hash + '-unstaged'
# then you can commit your code, and rename the folder with the current commit hash

# do I add the date of the commit to the save path???

# add an option in the config to show the commit that created the figures

# TODO: multiple path options just in case one doesn't exist already

def generate_show_script(repo, commit_hash):
    bash = '#!/bin/bash\n'
    bash += 'git -C "{}" checkout {}\n'.format(repo, commit_hash)
    bash += 'cd "{}"'.format(repo)
    bash += 'echo "Modified files:"\n'
    bash += 'git --no-pager diff --stat {}^1 {}\n'.format(commit_hash, commit_hash)
    bash += 'exec $SHELL\n'
    return bash

def auto_commit(repo_path, max_commit_len=500):
    # get what changed in the code
    diff_to_commit = sh.check_output('git -C "{}" diff HEAD | egrep \'^\\+|^-{{1}}[^-]\''.format(repo_path), shell=True)
    # now commit with the diff as the message
    sh.check_call('git -C "{}" add --all'.format(repo_path), shell=True)
    # only keep max_commit_len characters tho
    sh.check_call('git -C "{}" commit -m "{}"'.format(repo_path, diff_to_commit.decode('utf-8')[:max_commit_len]), shell=True)
    return diff_to_commit[:max_commit_len]

if __name__ == '__main__':
    main()
