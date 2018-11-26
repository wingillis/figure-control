'''
The base class for figure_control. This class can be imported in a python script
and interfaced with directly. This class will handle commits, diffs, etc.

Usage: ## TODO
>>> from figure_control import FigureControl

OR

>>> from figure_control.base import FigureControl
'''
import os
import stat
import warnings
from git import Repo
from figure_control.util import (load_config, clean_path, create_save_path,
                                 generate_show_script)
from typing import Callable


class FigureControl():

  def __init__(self, repo_path: str, config_path: str =None, final: bool =False):
    '''
    Args:
      repo_path: path to the figure-generating codebase
      config_path: path to the config file describing how to treat
                   saving the figures and commit-related information
    '''
    self.repo = Repo(repo_path, search_parent_directories=True)
    self.base = self.repo.working_dir
    # if config_path is not supplied, default to the codebase's working dir
    if config_path is None:
      config_path = self.base
    self.options = load_config(config_path)
    self.options['path'] = clean_path(self.options['path'])

    self.final = final

    # list to store all the saving functions
    self.fns = []

  # git-related functions
  def commit(self, message=None, max_commit_len=500):
    self.repo.git.add('--all')
    if message is None:
      diff = self.repo.git.diff('HEAD')
      self.repo.index.commit(diff[:max_commit_len])
    else:
      self.repo.index.commit(message)

  @property
  def commit_count(self):
    return self.repo.active_branch.commit.count()

  @property
  def hash(self):
    return self.repo.active_branch.commit.hexsha

  # save directory related functions
  @property
  def save_path(self):
    return create_save_path(self.options['path'], self.hash, self.commit_count, self.final)

  def setSavePath(self, p):
    self.options['old-path'] = self.options['path']
    self.options['path'] = clean_path(p)

  def resetSavePath(self):
    self.options['path'] = self.options['old-path']

  def createSavePath(self):
    if self.repo.is_dirty() and self.options.get('auto-commit', False):
      self.commit()
    elif not self.options.get('auto-commit', False):
      warnings.warn('Repo has changes and auto-commit is off!!! Your figures' +
                    ' might not match the code that generated them!!!')

    sp = self.save_path
    if not os.path.exists(sp):
      os.makedirs(sp)
      if self.options.get('executable', False):
        self.createExecutable()
    return sp

  def createExecutable(self):
    script = generate_show_script(self.base, self.hash)
    file_path = os.path.join(self.save_path, 'go-to-{}'.format(self.hash[:7]))
    with open(file_path, 'w') as f:
      f.write(script)
    st = os.stat(file_path).st_mode
    os.chmod(file_path, st | stat.S_IEXEC)

  ## figure saving functions
  def addSavingFun(self, fun: Callable):
    '''Add a user-defined function for saving figures, with the following
    signature: def saver(path, figs, **kwargs). `path` is used by this class
    to supply the generated path based on the current commit.

    Args:
      fun: a function used to save figures (or honestly anything you want)
    Example:
    >>> def saver(path, figs, **kwargs):
          if isinstance(figs, (list, tuple)):
            for i, fig in enumerate(figs):
              fig.savefig(join(path, 'fig_{:04d}.png'.format(i), **kwargs)
    '''
    
    assert callable(fun), 'Please supply a function to this method'
    self.fns += [fun]

  def clearSavers(self):
    self.fns = []

  def regiserMPLSaver(self):

    def saver(path, figs, **kwargs):
      if isinstance(figs, (list, tuple)):
        for i, fig in enumerate(figs):
          fig.savefig(join(path, 'fig_{:04d}.png'.format(i)), **kwargs)
          fig.savefig(join(path, 'fig_{:04d}.pdf'.format(i)), **kwargs)
      elif isinstance(figs, dict):
        for fname, fig in figs.items():
          fig.savefig(join(path, fname + '.png'), **kwargs)
          fig.savefig(join(path, fname + '.pdf'), **kwargs)
      else:
        figs.savefig(join(path, 'fig_0000.png'), **kwargs)
        figs.savefig(join(path, 'fig_0000.pdf'), **kwargs)
    
    self.addSavingFun(saver)

  def save(self, *args, **kwargs):
    sp = self.createSavePath()
    for fun in self.fns:
      fun(sp, *args, **kwargs)
