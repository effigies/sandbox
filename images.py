# Common functions on datasets
# Builds on nibabel
#
# 2013-2016 Chris Markiewicz <effigies@bu.edu>

import numpy as np
import scipy as sp
import scipy.stats
import nibabel as nib
try:
    import mne
except ImportError:
    pass


def mean_images(overlays):
    """Read set of spatial files, write average (ignoring zeros) to new file"""

    stack = nib.concat_images(overlays, check_affines=False)

    sums = np.sum(stack.get_data(), axis=3)
    counts = np.sum(stack.get_data() != 0, axis=3)
    counts[counts == 0] = 1

    return image_like(stack, sums / counts)


def t_test_normalized_images(overlays):
    """Perform group-level t-tests with each image's spatial mean removed."""
    demean = lambda x: map_image(lambda y: y - np.mean(y), x)
    return t_test_images(map(demean, map(nib.load, overlays)), 0.0)


def t_test_images(images, popmean=0.0):
    """Perform per-entry t-test on nibabel spatial images"""
    stack = nib.concat_images(images, check_affines=False)

    tstats, pvalues = sp.stats.ttest_1samp(stack.get_data(), popmean, axis=3)
    reject, corrected = mne.stats.fdr_correction(pvalues)

    return (image_like(stack, tstats), image_like(stack, pvalues),
            image_like(stack, corrected))


def t_test_2sample(sample_a, sample_b, equal_var=True):
    """t-statistics are positive if a > b"""
    a_stack = nib.concat_images(sample_a, check_affines=False)
    b_stack = nib.concat_images(sample_b, check_affines=False)

    tstats, pvalues = sp.stats.ttest_ind(a_stack.get_data(),
                                         b_stack.get_data(), axis=3,
                                         equal_var=equal_var)
    reject, corrected = mne.stats.fdr_correction(pvalues)

    return (image_like(a_stack, tstats), image_like(a_stack, pvalues),
            image_like(a_stack, corrected))


def image_like(img, data):
    return img.__class__(data, img.affine, img.header.copy(),
                         extra=img.extra.copy())


def map_image(func, mgh):
    return image_like(mgh, func(mgh.get_data()))


def sum_images(inputs):
    return map_image(lambda x: np.sum(x, axis=3), nib.concat_images(inputs))


def diff_images(path1, *paths):
    """Test whether image data arrays have the same shape and contents

    Returns False only if all volumes differ.

    Does not check affines or headers"""
    ref = nib.load(path1)
    return any(np.any(ref.get_data() != nib.load(path).get_data())
               for path in paths)
