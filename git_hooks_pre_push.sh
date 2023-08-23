#!/bin/sh
#
while read oldrev newrev refname
do
    branch=$(git rev-parse --symbolic --abbrev-ref $refname)
    if [ "main" = "$branch" ]; then
        # Run pylint
        exec pylint pymarble
        exec pylint tests
        # Run mypy
        exec mypy pymarble
        # Test document creation
        exec make -C docs html
        # Run pytest
        exec pytest -s tests
        #
        echo "Pre-commit-tests are finished"
    fi
done

