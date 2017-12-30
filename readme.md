# Figure Control

This is an attempted solution to problems many researchers have for
managing the reproducibility of figures they create.

This is an attempt to ease the pain of managing which figures are associated
with which commit.

This is two things:
1. a command-line-interface built with python to interface with multiple programming languages
2. a python package to use directly in python

Basically, this package associates one git repository with an output figure
path, subdivided into either `final` figures or `exploratory` figures. This
division is mainly added to allow the user to easily distinguish the output of
their work. Folders are created that are named by the current date and the
most current commit logged in the associated git repository. Check out below
to see how to use the CLI interface.

Proper use of this repository will make it very easy to track your progress
through figure generation, so you don't have to overwrite figures any more.

## Installation

Clone this repository to your local computer. Navigate to `figure-control`'s
directory. Run:

```
  pip install -e .
```

to install the cli and python package.

Type: `which figure-control` to verify it installed correctly. When the cli is
installed, a convenience matlab script is also produced, for people who prefer
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

And a new directory will be created with the commit number, today's date, and the latest commit
for this repo.

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

# get the save path
save_path = fig_ctrl.createSavePath()

# register a save function
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
```

Every time `getSavePath` or `createSavePath` is run, it will check if any
code has changed in the repository. You can then `autoCommit` and it will
update all necessary settings in the class.
