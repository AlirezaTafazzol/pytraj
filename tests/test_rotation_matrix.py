#!/usr/bin/env python
from __future__ import print_function
import unittest
import pytraj as pt
from pytraj.utils import eq, aa_eq


class TestRotationMatrix(unittest.TestCase):
    def setUp(self):
        self.traj = pt.iterload("./data/tz2.nc", "./data/tz2.parm7")
        cm_avg= '''
        average avg.pdb
        run
        '''
        pt.load_batch(self.traj, cm_avg).run()

    def test_nomass(self):
        traj = self.traj
        # cpptraj output
        cm = '''
        reference avg.pdb
        rms R0 reference @CA,C,N,O savematrices
        '''

        state = pt.load_batch(traj, cm)
        state.run()
        saved_mat = state.data[-1].values

        # pytraj output
        avg = pt.mean_structure(traj)
        mat = pt.calc_rotation_matrix(traj, ref=avg, mask='@CA,C,N,O')
        assert mat.shape == (traj.n_frames, 3, 3), 'mat shape'
        aa_eq(mat.flatten(), saved_mat.flatten())

    def test_mass(self):
        traj = self.traj
        # cpptraj output
        cm = '''
        reference avg.pdb
        rms R0 reference @CA,C,N,O savematrices mass
        '''

        state = pt.load_batch(traj, cm)
        state.run()
        saved_mat = state.data[-1].values

        # pytraj output
        avg = pt.mean_structure(traj)
        mat = pt.calc_rotation_matrix(traj, ref=avg, mask='@CA,C,N,O', mass=True)
        assert mat.shape == (traj.n_frames, 3, 3), 'mat shape'
        aa_eq(mat.flatten(), saved_mat.flatten())


if __name__ == "__main__":
    unittest.main()
