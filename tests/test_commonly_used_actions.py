import unittest
import pytraj as pt
from pytraj.testing import aa_eq
from pytraj.compat import zip
from pytraj import adict


class TestAutoImage(unittest.TestCase):
    def test_0(self):
        traj = pt.iterload(
            "./data/tz2.truncoct.nc", "./data/tz2.truncoct.parm7")
        f0 = traj[0]
        act = adict['autoimage']
        f0cp = f0.copy()
        assert f0.same_coords_as(f0cp) == True
        act("", f0, traj.top)
        assert f0.same_coords_as(f0cp) == False

    def test_1(self):
        traj = pt.iterload(
            "./data/tz2.truncoct.nc", "./data/tz2.truncoct.parm7")
        f0 = traj[0]
        f0cp = f0.copy()
        #print(f0.same_coords_as(f0cp))
        assert f0.same_coords_as(f0cp) == True
        adict['autoimage']("", f0, traj.top)
        #print(f0.same_coords_as(f0cp))
        assert f0.same_coords_as(f0cp) == False

        fsaved = pt.iterload("./data/tz2.truncoct.autoiamge.save.r",
                               "./data/tz2.truncoct.parm7")[0]
        aa_eq(fsaved.coords, f0.coords)

    def test_2(self):
        from pytraj.common_actions import do_autoimage
        # test do_autoimage
        traj = pt.iterload(
            "./data/tz2.truncoct.nc", "./data/tz2.truncoct.parm7")
        f0 = traj[0]
        f0cp = f0.copy()
        #print(f0.same_coords_as(f0cp))
        assert f0.same_coords_as(f0cp) == True
        do_autoimage(traj=f0, top=traj.top)
        #print(f0.same_coords_as(f0cp))
        assert f0.same_coords_as(f0cp) == False

        fsaved = pt.iterload("./data/tz2.truncoct.autoiamge.save.r",
                               "./data/tz2.truncoct.parm7")[0]
        aa_eq(fsaved.coords, f0.coords)


class TestGeometry(unittest.TestCase):
    def testRadgyr(self):
        traj = pt.iterload(top="./data/Tc5b.top",
                           filename='data/md1_prod.Tc5b.x', )
        txt = '''
        parm ./data/Tc5b.top
        trajin ./data/md1_prod.Tc5b.x
        radgyr @CA nomax
        radgyr nomax
        radgyr !@H= nomax
        '''

        data = pt.datafiles.load_cpptraj_output(txt)
        for mask, out  in zip(['@CA', '', '!@H='], data):
            aa_eq(pt.radgyr(traj, mask), out)


if __name__ == "__main__":
    unittest.main()
