from __future__ import print_function
import pytraj as pt
import numpy as np
import unittest
from pytraj.hbonds import search_hbonds
from pytraj.testing import aa_eq
from pytraj.compat import izip as zip


class TestSearchHbonds(unittest.TestCase):
    def test_hbonds(self):
        traj = pt.iterload("./data/DPDP.nc", "./data/DPDP.parm7")
        dslist = search_hbonds(traj, dtype='dataset')
        for key in dslist.keys():
            if 'UU' not in key:
                assert len(dslist[key].values) == traj.n_frames
        mydict = dslist.to_dict()
        mydict_np = dslist.to_dict()
        assert len(mydict.keys()) == dslist.size
        assert len(mydict_np.keys()) == dslist.size

        for key in mydict.keys():
            mydict[key] = np.asarray(mydict[key])
            aa_eq(mydict[key], mydict_np[key])

        # FIXME: "Warning: Mask has no atoms"
        #dslist_b = search_hbonds_nointramol(traj)

    def test_hbonds_with_image(self):
        traj = pt.iterload("data/tz2.ortho.nc", "data/tz2.ortho.parm7")

        hbonds_0 = pt.search_hbonds(traj(autoimage=True))
        hbonds_1 = pt.search_hbonds(traj, image=True)
        aa_eq(hbonds_0.values, hbonds_1.values)

    def test_hbonds_from_pdb(self):
        traj = pt.load('data/1L2Y.pdb')
        hb = pt.search_hbonds(traj)

        state = pt.load_cpptraj_state('''
        parm data/1L2Y.pdb
        trajin data/1L2Y.pdb
        hbond series
        ''')
        state.run()

        for data_p, data_cpp in zip(hb.data, state.data[1:]):
            assert len(data_p) == traj.n_frames == 38, 'size of dataset must be 38'
            aa_eq(data_p, data_cpp)

        # make sure distances are smaller than cutoff
        distance_cutoff = 2.5
        hb = pt.search_hbonds(traj)
        distances = pt.distance(traj, hb._amber_mask())
        assert np.all(distances< distance_cutoff), 'must smaller than 2.5 angstrom'

        saved_donor_aceptors = ['ASP9_OD2-ARG16_NH1-HH12',
                                'ASP9_OD2-ARG16_NH2-HH22',
                                'ASP9_OD2-ARG16_NE-HE',
                                'ASP9_OD2-ARG16_NH2-HH21',
                                'ASP9_OD2-ARG16_NH1-HH11'] 

        donor_aceptors = pt.search_hbonds(traj, ':9,16').donor_aceptor
        assert saved_donor_aceptors == donor_aceptors, 'saved_donor_aceptors'

if __name__ == "__main__":
    unittest.main()
