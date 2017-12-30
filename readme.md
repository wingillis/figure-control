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
  executable: true
```
