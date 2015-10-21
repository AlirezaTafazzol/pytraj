from __future__ import print_function
import unittest
from glob import glob
import pytraj as pt
from pytraj.testing import eq, aa_eq
from pytraj.testing import cpptraj_test_dir
from pytraj.utils import goto_temp_folder


class TestWriteTraj(unittest.TestCase):
    def setUp(self):
        self.traj = pt.load_sample_data('tz2')

    def test_regular(self):
        traj = self.traj.copy()
        assert traj[0].has_box() == True

        with goto_temp_folder():
            # write traj with nobox info
            fname = "traj_nobox.nc"
            pt.write_traj(fname, traj, mode='nobox')
            t = pt.load(fname, traj.top)

            assert t[0].has_box() == False
            aa_eq(t.xyz, traj.xyz)

            # write from frame_iter, need to provide top
            fname = "traj_frame_iter.nc"
            # raise ValueError if there is no Topology
            pt.write_traj(fname, traj(), top=traj.top, overwrite=True)
            t = pt.iterload(fname, traj.top)
            aa_eq(t.xyz, traj.xyz)

    def test_write_xyz(self):
        xyz = self.traj.xyz
        fname = './output/test_xyz.nc'
        pt.write_traj(fname, xyz, top=self.traj.top, overwrite=True)
        t0 = pt.iterload(fname, top=self.traj.top)
        aa_eq(self.traj.xyz, t0.xyz)


    def test_split_and_write_traj(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        # duplcate
        traj.load(traj.filename)
        assert traj.n_frames == 20
        top = traj.top

        # test TrajectoryIterator object
        pt.tools.split_and_write_traj(traj,
                                      n_chunks=4,
                                      root_name='./output/trajiterx')
        flist = sorted(glob("./output/trajiterx*"))
        traj4 = pt.iterload(flist, top)
        aa_eq(traj4.xyz, traj.xyz)

        # dcd ext
        pt.tools.split_and_write_traj(traj, 4,
                                      root_name='./output/ts',
                                      ext='dcd')
        flist = sorted(glob("./output/ts.*.dcd"))
        traj4 = pt.iterload(flist, top)
        aa_eq(traj4.xyz, traj.xyz)

    def test_raise_NotimplementedError(self):
        traj = pt.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")

        self.assertRaises(NotimplementedError, lambda: pt.write_traj([traj[0], traj[1]],
            top=traj.top, frame_indices=range(3)))


if __name__ == "__main__":
    unittest.main()
