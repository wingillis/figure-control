from figure_control.main import (clean_path, generate_commit_hash, repo_is_dirty,
    assemble_save_path, load_config, is_git_repo, auto_commit, generate_show_script)
import os
import stat

class FigureControl(object):

    def __init__(self, repo, final=False):
        self.repo = clean_path(repo)
        assert os.path.exists(self.repo), 'Specified repo does not exist'
        assert is_git_repo(self.repo), 'Not a git repo'

        self.is_final = final
        self.hash = generate_commit_hash(self.repo)
        self.options = load_config(self.repo)

    def getSavePath(self):
        if repo_is_dirty(self.repo):
            print('Warning: repo has changes, it is recommended you commit them')
        return assemble_save_path(self.repo, self.options['path'], self.hash, self.is_final)

    def autoCommit(self):
        '''Returns the commit message'''
        diff = auto_commit(self.repo)
        self.hash = generate_commit_hash(self.repo)
        return diff

    def createSavePath(self):
        sp = self.getSavePath()
        if not os.path.exists(sp):
            os.makedirs(sp)
            if self.options.get('executable', False):
                self.writeExecScript()

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

    def save(self):
        # make sure that the path already exists
        self.createSavePath()
        self.fn(self.getSavePath())
