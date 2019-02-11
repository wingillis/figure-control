import os
import ruamel.yaml as yaml
from glob import glob
from os.path import join
from datetime import date

def clean_path(repo):
  repo = os.path.expanduser(repo)
  repo = os.path.abspath(repo)
  return repo


def load_config(config_path: str) -> dict:
  '''Load a figure control config file. Ideally, this file is located
  in the git repository of your exploratory codebase.

  Args:
    config_path: A path to a config file. Can either be a glob, directory,
                 or yaml file path
  '''
  if os.path.isdir(config_path):
    file = glob(join(config_path, '*figure*.yaml'))[0]
  elif config_path.find('*') != -1:
    file = glob(config_path)[0]
  else:
    file = config_path

  with open(file, 'r') as f:
    options = yaml.load(f, Loader=yaml.SafeLoader)
  
  # some assertions to make sure that we are reading in the proper config file
  assert options is not None, 'Nothing seems to be in the config file ' + file
  assert 'figure-control' in options, 'Required key figure-control not in config file: ' + file
  assert 'path' in options['figure-control'], 'No save path specified'

  return options['figure-control']


def create_save_path(base, hash, commit_count, final_fig):
    '''Creates a subdir path based on the commit hash and commit count'''
    dirtype = 'final' if final_fig else 'exploratory'
    today = date.today().strftime('%Y-%m-%d')
    dirname = '{}-{}-{}'.format(commit_count, today, hash)
    return join(base, dirtype, dirname)


def generate_show_script(repo, hash):
  bash = '#!/bin/bash\n'
  bash += 'git -C "{}" checkout {}\n'.format(repo, hash)
  bash += 'cd "{}"\n'.format(repo)
  bash += 'echo "Modified files:"\n'
  bash += 'git --no-pager diff --stat {hash}^1 {hash}\n'.format(hash=hash)
  bash += '''if [[ "$0" != "$BASH_SOURCE" ]]; then
  echo "Sourced"
else
  exec $SHELL
fi
'''
  return bash