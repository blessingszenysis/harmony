# Integration Guide

The manual for writing integrations:
 - [English](https://docs.google.com/document/d/1Hqj70NSy2GPP45bW5ea8mSBS-VbL2y2Qk8GMsiZYRn8/edit?usp=sharing)
 - [Português](https://docs.google.com/document/d/1cNhmiym6TN_u7-L2Ezf2CCGdsjLMaFUYdmqwKXse9f4/edit?usp=sharing)

# Local development setup for pipeline only

In order to run data pipeline steps on the command line, you'll need to set up a local development environment.

Operating systems supported by this documentation:

- Linux (Ubuntu)
- macOS

## System requirements

1. Install python (any version 3.8 - 3.10).
2. Update package managers.
   1. macOS: install [homebrew](https://brew.sh/)
   2. Ubuntu:
      ```
      sudo apt-get update # updates available package version list
      sudo apt-get upgrade # update packages
      sudo apt-get autoremove # remove old packages
      sudo do-release-upgrade # update os version
      ```

## Source code

As this is a private repository, you will need SSH authentication set up. Follow these [instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh). You can run `ssh -T git@github.com` to check it was done correctly.

Clone repo: `git clone git@github.com:Zenysis/Harmony-Brazil.git`.
​

## Dev dependencies

1. On macOS:
   ```
   brew install wget curl cmake geos jq pigz lz4 openconnect watchman proj lefthook coreutils grep pypy3
   echo 'export PATH="/usr/local/opt/coreutils/libexec/gnubin:/usr/local/opt/grep/libexec/gnubin:${PATH}"' >> ~/.zshrc
   ```
2. Ubuntu:
   ```
   sudo apt-get update
   sudp apt-get install --no-install-recommends -y \
      wget \
      curl \
      cmake \
      geos \
      yarn \
      jq \
      pigz \
      lz4 \
      openconnect \
      watchman \
      proj \
      lefthook \
      coreutils \
      grep \
      pypy3
   ```

## Python dependencies

1. Update `PYTHONPATH`. In your bash profile (or z profile, etc.), set the `PYTHONPATH` environment variable to include the path to your clone of Harmony-Brazil. Run `echo 'export PYTHONPATH="${PYTHONPATH}:<path to repo>"' >> ~/.bash_profile` (or `.bashrc`, `.zshrc`, etc.). Note that anytime you update your bash profile, you either have to restart your terminal or run `source ~/.bash_profile`.

2. Create a python3 virtual environment and a pypy environment. Change into the source directory (ie `~/Harmony-Brazil`). Run the following:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip setuptools
   pip install -r requirements.txt
   pip install -r requirements-pipeline.txt
   deactivate
   
   pypy3 -m venv venv_pypy3
   source venv_pypy3/bin/activate
   pip install --upgrade pip setuptools
   pip install -r requirements.txt
   pip install -r requirements-pipeline.txt
   deactivate
   ```
   ​
   If you see wheel-related errors here, run `pip install wheel` before iterating over the requirements files.
   ​
3. To enter the virtual environment, run `source venv/bin/activate`.

## Environment variables

Ensure that environment variables are set correctly:

```text
ZEN_ENV=<project code>
ZEN_HOME=<path to git source code>
```

## Validate everything worked
Run `./pipeline/br/process/zeus_process run ./pipeline/br/process/run/00_yellow_fever`

There should be no red errors and should say "SUCCESS" in green.

## Javascript dependencies

These are necessary for adding translations for new dimensions. We use yarn as a node.js package manager. ​

1. Install yarn.
   1. macOS: `brew install yarn`
   2. Ubuntu: `curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add - echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list sudo apt update && sudo apt install yarn`
2. Install node.
   1. macOS: `brew install node@14`
   2. Ubuntu: `sudo apt install nodejs`
3. Download all dependencies: `yarn install`
4. Verify this worked with `yarn translations`
