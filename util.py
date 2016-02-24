# Generic utility functions
#
# 2014-2016 Chris Markiewicz <effigies@bu.edu>

import time
import os
from six import string_types


def timestamp(message):
    print('{} {}'.format(time.strftime('%Y.%m.%d %H:%M:%S'),
                         message))


def check_deps(targets, dependencies):
    """Return true if all targets exist and are newer than all dependencies.

    An OSError will be raised if there are missing dependencies."""

    # Allow single target/dependency
    if isinstance(targets, string_types):
        targets = [targets]
    if isinstance(dependencies, string_types):
        dependencies = [dependencies]

    return all(map(os.path.exists, targets)) and \
        min(map(os.path.getmtime, targets)) > \
        max(map(os.path.getmtime, dependencies))


def prep_dirs(targets):
    """Create all necessary directories in a path"""
    if isinstance(targets, string_types):
        targets = [targets]

    for dirname in map(os.path.dirname, targets):
        if not os.path.isdir(dirname):
            try:
                os.makedirs(dirname)
            except OSError as e:
                # Already exists errors are common when running parallel
                # jobs
                if e[0] != 17:
                    raise e
