from figure_control.main import (clean_path, generate_commit_hash, repo_is_dirty,
    assemble_save_path, load_config, is_git_repo, auto_commit, generate_show_script,
    get_commit_count)
import os
import stat
from os.path import join

class FigureControl(object):

    def __init__(self, repo, config_name='', final=False):
        '''config_name is just the name of the file (no path)'''
        self.is_final = final
        self.repo = clean_path(repo)
        assert os.path.exists(self.repo), 'Specified repo does not exist'
        assert is_git_repo(self.repo), 'Not a git repo'

        self.options = load_config(self.repo, config_name)
        assert 'path' in self.options, 'No save path specified'
        self.options['path'] = clean_path(self.options['path'])

        self.hash = generate_commit_hash(self.repo)
        self.commit_count = get_commit_count(self.repo, self.hash)

        self.fn = None

    def getSavePath(self):
        if repo_is_dirty(self.repo):
            if self.options.get('auto-commit', False):
                print('Auto-commit is on, committing repo changes...')
                self.autoCommit()
            else:
                print('Warning: repo has changes, it is recommended you commit them')
        return assemble_save_path(self.options['path'], self.hash,  self.commit_count, self.is_final)

    def autoCommit(self):
        '''Returns the commit message'''
        diff = auto_commit(self.repo)
        self.hash = generate_commit_hash(self.repo)
        self.commit_count = get_commit_count(self.repo, self.hash)
        return diff

    def createSavePath(self):
        '''If save path doesn't exist, create it'''
        sp = self.getSavePath()
        if not os.path.exists(sp):
            os.makedirs(sp)
            if self.options.get('executable', False):
                self.writeExecScript()
        return sp

    def writeExecScript(self):
        exec_contents = generate_show_script(self.repo, self.hash)
        exec_file_path = join(self.getSavePath(), 'goto-commit-{}'.format(self.hash))
        with open(exec_file_path, 'w') as exec_file:
            exec_file.write(exec_contents)
        st = os.stat(exec_file_path)
        os.chmod(exec_file_path, st.st_mode | stat.S_IEXEC)

    def registerSaver(self, function):
        # let the user define their own save function that accepts a path str
        self.fn = function

    def save(self, *args, **kwargs):
        # make sure that the path already exists
        sp = self.createSavePath()
        self.fn(sp, *args, **kwargs)

    def registerMatplotlibSaver(self):
        # option for the save dirs to have sub dirs?
        def saver(path, figs, **kwargs):
            if isinstance(figs, (list, tuple)):
                for i, fig in enumerate(figs):
                    fig.savefig(join(path, str(i) + '.png'), **kwargs)
                    fig.savefig(join(path, str(i) + '.pdf'), **kwargs)
            elif isinstance(figs, dict):
                for fname, fig in figs.items():
                    fig.savefig(join(path, fname + '.png'), **kwargs)
                    fig.savefig(join(path, fname + '.pdf'), **kwargs)
            else:
                figs.savefig(join(path, 'fig1.png'), **kwargs)
                figs.savefig(join(path, 'fig1.pdf'), **kwargs)

        self.fn = saver
