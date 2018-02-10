# Figure Control

Figure Control aims to solve problems many researchers have for
managing the reproducibility of figures they create.

To ease the pain of linking different figure versions with the code that
generated them, Figure Control automatically handles much of the heavy lifting
for committing your code, generating a consistent save path, linking the
commit that generated your figures to the save path, and separating exploratory
vs final figures.

Figure Control is a mixture of two things:
1. a command-line-interface (CLI) built with python to allow you to generate figures in essentially any language
2. a python package/class to use directly within python by importing FigureControl as a module

Figure Control associates one git repository with an output figure
path and subdivides it into either `final` figures or `exploratory` figures. This
division is added to allow the user to easily distinguish the output of
their work. Folders are created and named with the date you generated the figures and the
most current commit associated with your code repository. Check out below
to see how to use the CLI interface.

Proper use of this repository makes it very easy to track your progress
through figure generation, so you don't have to overwrite figures or have
trouble re-finding parameters you used to make 'that one good figure from 3
months ago'.

## Installation

Clone this repository to your local computer.

```
git clone https://github.com/wingillis/figure-control.git
```

Navigate to `figure-control`'s directory. Run:

```
  pip install -e .
```

to install the cli and python package.

Type: `which figure-control` to verify it installed correctly. When the cli is
installed, a matlab script is also produced for people who prefer
to make their figures in matlab.

## Usage

### CLI

First, you need to add a `.yaml` file into the git repo you want to track.
The contents should look something like this (call it whatever you want, or
`config.yaml`):

```yaml
figure-control:
  path: /path/to/figure/output/
  # this option allows you to create script to automatically take you to the
  # commit that created the figures in a specific folder
  # you can either double-click on the script, or source it from the terminal
  # i.e: `. ./goto-commit-42fbc33` or `source ./goto-commit-42fbc33`
  executable: true
  # this option will allow the code to automatically commit any unstaged changes
  # that you have made
  auto-commit: true
```

To get a save directory, run:

`figure-control --repo="/path/to/your/repo"`

And a result like this should follow:

`/path/to/figure/output/exploratory/223-12-30-2017-f8f5853`

And a new directory will be created with the commit number (`223`), today's date
(`12-30-2017`), and the latest commit (`f8f5853`) for this repo.

### Matlab

A helper function in `matlab` is installed as well. To use it in matlab,
add the `figure-control` directory to your matlab path, and type:

```octave
save_path = figure_control('/path/to/repo')
% you can also make it a lambda function, for more convenient usage
getProjSave = @() figure_control('/path/to/repo');
```

and it will execute and parse the CLI to give you the path to save your figures.


### Python

The module is slightly more feature-rich than the CLI. For instance, you can
run auto-commits. To use the `FigureControl` class:

```python
from figure_control import FigureControl as FC

fig_ctrl = FC('/path/to/repo')
# change some code in the repository, next time you get a save path, you will
# get a warning that code has changed in the repository
# commit the changes, with the changes as the commit message like so:
fig_ctrl.autoCommit()

# - create a save path
# - this is only needed if you want to manually save your figures
# - it is recommended that you call this every time you generate a new figure
# just in case you changed your code between saving figures
# - if you register your own saver function, you never have to get the actual
# save path
save_path = fig_ctrl.createSavePath()

# if you just want to know what the current folder save path is, grab it by
# typing:
save_path = fig_ctrl.savePath

# register a save function
# the class automatically will fill in the save path so you don't have to worry
# about always supplying it
def save(path, name, fig, **kwargs):
  # make sure it accepts a path parameter
  fig.savefig(os.path.join(path, name + '.png'), **kwargs)
  fig.savefig(os.path.join(path, name + '.pdf'))

# this registers a function so that you can call it with `fig_ctrl.save()`
fig_ctrl.registerSaver(save)


# plot some data with matplotlib
import matplotlib.pyplot as plt
fig1 = plt.figure()
plt.plot(range(10))

# this will save it in the dir associated with the repo's current commit hash
fig_ctrl.save('line', fig1, dpi=300)

# because matplotlib is one of the most popular ways to generate figures in
# python, a special function is included to easily save matplotlib figures:
fig_ctrl.registerMatplotlibSaver()

# to save your figures with it, either store your figures in a `list`,
# and files will be saved with a numerical file name, i.e. fig_0001, fig_0002, fig_0003, or
# a `dict` where the keys are your file name
# also, add any normal `savefig` parameters to the save function, and they will
# be properly transferred
fig_ctrl.save({
  'figure-cool-line': fig1
}, dpi=300, transparent=True)

fig_ctrl.save([fig1, fig1])
```

Every time `createSavePath` is run, it will check if any
code has changed in the repository. It will `autoCommit` you repository if
that option is true in your `yaml` config file.

## Developing an interface for another language

It is very easy to extend this framework to other languages that people use to
generate figures. If you'd like to extend this to work with any other languages,
please look at the `.figure_control.m` file included in this repo for an
example of how it was done for matlab.
