#!/usr/bin/env python

from __future__ import print_function
import unittest
import pytraj as pt
import pytraj as pt
from pytraj.testing import run_docstring
import pytraj.common_actions as pyca
from pytraj.base import *
import pytraj as pt


def silly_doc_func():
    """
    """
    pass


class Test(unittest.TestCase):
    def test_0(self):
        from pytraj._shared_methods import iterframe_master as fi
        from pytraj import matrix_analysis as ma
        from pytraj import dihedral_analysis as da
        from pytraj import Trajectory
        from pytraj import Frame
        from pytraj.misc import split_range
        from pytraj.tools import grep
        from pytraj import clustering_dataset
        from pytraj.cluster import kmeans
        from pytraj.array import DataArray
        from pytraj import vector_analysis as va

        try:
            import parmed
            has_parmed = True
        except ImportError:
            has_parmed = False

        funclist =  [DataArray,
                    pt.iterframe,
                    pt.iterchunk,
                    pt.calc_vector,
                    pt.rdf,
                    va.vector_mask,
                    pt.select_atoms,
                    pt.multidihedral,
                    pt.rmsd,
                    pt.watershell,
                    pt.distance,
                    pt.angle,
                    pt.dihedral,
                    pt.dssp,
                    pt.radgyr,
                    pt.molsurf,
                    pt.search_hbonds,
                    pt.closest,
                    pt.search_neighbors,
                    pt.pairwise_rmsd,
                    pt.center,
                    silly_doc_func,
                    fi,
                    split_range,
                    Frame.__getitem__,
                    Topology.select,
                    grep,
                    clustering_dataset,
                    pt.mindist,
                    kmeans, ]

        if has_parmed:
            funclist.append(pt.load_parmed)

        for func in funclist:
            run_docstring(func)

        func_names = ma.default_key_dict.keys()
        for key in func_names:
            run_docstring(ma.__dict__[key])

        func_names = da.supported_dihedral_types
        for key in func_names:
            run_docstring(da.__dict__['calc_' + key])


if __name__ == "__main__":
    unittest.main()
