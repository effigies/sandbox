# Set up a common environment for use from Python scripts
#
# 2012-2016 Chris Markiewicz <effigies@bu.edu>

import os
from subprocess import check_output

# Check for FreeSurfer
env = os.environ
if 'FREESURFER_HOME' not in env:
    raise RuntimeError('FreeSurfer environment not defined. Define the '
                       'FREESURFER_HOME environment variable.')
# Run FreeSurferEnv.sh if not most recent script to set PATH
if not env['PATH'].startswith(os.path.join(env['FREESURFER_HOME'], 'bin')):
    envout = check_output(['bash', '-c', 'source /etc/freesurfer.sh && env'],
                          env={})
    os.environ.update(dict(line.split('=', 1)
                           for line in envout.split('\n')
                           if line and not line.startswith('_=')))

# Session metadata and results directories
metadata_dir = '/data/fs_sess_metadata'
results_dir = '/data/fs_sess_results'

spm_path = '/data/software/spm8'
