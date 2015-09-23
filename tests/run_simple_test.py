#!/usr/bin/env python
'''Aim: just make sure pytraj runnable.
'''

import unittest
from pytraj import *
import pytraj as pt
from pytraj.trajs import *
from pytraj.datasets import *
from pytraj.common_actions import *


class TestRunnable(unittest.TestCase):
    def test_loading(self):
        traj = pt.load_sample_data('tz2')
        traj[:]
        traj[:3]

        # load from a list of files
        fname = traj.filename
        t0 = pt.iterload([fname, fname], traj.top,
                         frame_slice=[(0, 8, 2), ] * 2)

    def test_import(self):
        from pytraj import run_tests
        run_tests()

    def test_create_actions(self):
        print("try to make all action objects")
        from pytraj import adict
        failed_list = []

        for key in adict.keys():
            if key not in failed_list:
                adict[key]

    def test_create_analysis(self):
        DatasetList()
        print("try to make all analysis objects")
        from pytraj import analdict
        failed_list = []

        for key in analdict.keys():
            if key not in failed_list:
                analdict[key]

    def test_Dataset(self):
        print("try to make all dataset stuff")
        DatasetDouble()
        DatasetFloat()
        DatasetInteger()
        DatasetString()
        DatasetMatrixDouble()
        DatasetMatrixFloat()
        DatasetVector()
        DatasetCoords()
        DatasetCoordsRef()
        DatasetCoordsCRD()

    def test_geometry(self):
        print("try to make structure-related objects")
        Topology()
        Molecule()
        Residue()
        Atom()
        Frame()
        TrajectoryIterator()

    def test_other(self):
        print("other stuff. throw all tests don't belong anywhere else here")
        from pytraj import cpptraj_dict
        from pytraj.misc import get_atts
        keys = get_atts(cpptraj_dict)
        cdict = cpptraj_dict.__dict__

        for key in keys:
            if isinstance(cdict[key], dict):
                assert cdict[key].keys() is not None


if __name__ == "__main__":
    from pytraj import show_versions
    show_versions()
    print('')
    unittest.main()
