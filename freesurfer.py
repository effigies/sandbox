# Utility functions for working with datasets in FreeSurfer directory
# structures
#
# 2013-2016 Chris Markiewicz <effigies@bu.edu>

import os
import numpy as np
import nibabel as nib
import networkx as nx
import subprocess
from util import check_deps


def subj_from_sess(sess, sessions_dir=os.environ['FUNCTIONALS_DIR']):
    with open(os.path.join(sessions_dir, sess, 'subjectname'), 'r') as f:
        return f.readline().rstrip('\n')


def surface(subject, hemi, surface='white',
            subject_dir=os.environ['SUBJECTS_DIR']):
    surf_path = os.path.join(subject_dir, subject, 'surf',
                             hemi + '.' + surface)
    return nib.freesurfer.read_geometry(surf_path)


def surface_graph(subject, hemi, surface='white',
                  subject_dir=os.environ['SUBJECTS_DIR']):
    coords, faces = surface(subject, hemi, surface, subject_dir)
    graph = nx.Graph()

    for i, j, k in faces:
        graph.add_edge(i, j)
        graph.add_edge(i, k)
        graph.add_edge(j, k)

    return graph


def weighted_surface_graph(subject, hemi, surface,
                           subject_dir=os.environ['SUBJECTS_DIR']):
    """Build a bidirectional graph with Euclidean distances as edges"""
    graph = nx.Graph()

    coords, faces = surface(subject, hemi, surface, subject_dir)

    def norm(x, y):
        diff = x - y
        return np.sqrt(diff.dot(diff))

    for i, j, k in faces:
        graph.add_edge(i, j, weight=norm(coords[i, :], coords[j, :]))
        graph.add_edge(i, k, weight=norm(coords[i, :], coords[k, :]))
        graph.add_edge(j, k, weight=norm(coords[j, :], coords[k, :]))

    return graph


def mri_vol2surf(sess, hemi, src, out=None, projfrac=0.5,
                 sessions_dir=os.environ['FUNCTIONALS_DIR']):
    srcreg = os.path.join(sessions_dir, sess, 'bold', 'register.dof6.dat')

    if out is None:
        assert src[-4:] == '.nii'
        directory, filename = os.path.split(src)
        out = os.path.join(directory, '{}.{}.mgh'.format(hemi, filename[:-4]))

    cmd = 'mri_vol2surf'
    options = ["--src", src,
               "--srcreg", srcreg,
               "--hemi", hemi,
               "--projfrac", "{:g}".format(projfrac),
               "--out", out]

    subprocess.check_call([cmd] + options)

    return True


def mri_surf2surf(src, tgtsess, tgt, srcsess,
                  sessions_dir=os.environ['FUNCTIONALS_DIR']):

    paths = src.split(os.path.sep)

    srcsubject = subj_from_sess(srcsess, sessions_dir=sessions_dir)
    tgtsubject = subj_from_sess(tgtsess, sessions_dir=sessions_dir)

    hemi = paths[-1][:2]

    cmd = 'mri_surf2surf'
    options = ["--srcsubject", srcsubject,
               "--trgsubject", tgtsubject,
               "--hemi", hemi,
               "--sval", src,
               "--tval", tgt]

    if check_deps(tgt, src):
        return True

    subprocess.check_call([cmd] + options)

    return True


def mri_surf2vol(sess, src, tgt=None, projfrac=0.5,
                 sessions_dir=os.environ['FUNCTIONALS_DIR']):
    bolddir = os.path.join(sessions_dir, sess, 'bold')
    srcreg = os.path.join(bolddir, 'register.dof6.dat')

    runs = sorted(d for d in os.listdir(bolddir)
                  if len(d) == 3 and d.isdigit())
    template = os.path.join(bolddir, runs[0], 'fmc.nii.gz')

    directory, filename = os.path.split(src)
    hemi = filename[:2]
    assert hemi in ('lh', 'rh')

    if tgt is None:
        assert src[-4:] == '.mgh'
        tgt = os.path.join(directory, '{}.nii'.format(filename[:-4]))

    cmd = 'mri_surf2vol'
    options = ["--surfval", src,
               "--hemi", hemi,
               "--volreg", srcreg,
               "--template", template,
               "--projfrac", "{:g}".format(projfrac),
               "--outvol", tgt]

    subprocess.check_call([cmd] + options)

    return True
