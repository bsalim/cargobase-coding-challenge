#!/bin/bash -ex

# Fetch master branch from Github
git fetch origin master
git reset --hard origin/master

# Rewrite ownership after pull from git
chown www-data:www-data . -R
supervisorctl restart cargoscrapper
