from .map import map
from pytraj.tools import concat_dict
from .pjob import PJob


def get_comm_size_rank():
    try:
        from mpi4py import MPI
        comm = MPI.COMM_WORLD
        rank = comm.rank
        size = comm.size
        return comm, size, rank
    except ImportError:
        comm = rank = size = None


def gather(name='data', clients=None, restype='ndarray'):
    '''gather data from different clients

    Parameters
    ----------
    name : name of the output holder
        for example: data = pytraj.calc_radgyr(traj) --> name = 'data'
    clients : IPython.parallel.Client objects
        number of clients == n_cores you use
    restype : str, {'ndarray', 'dataset'}, default 'ndarray' 
        if 'ndarray': hstack data by numpy.vstack
        if 'dataset': 'data' should be a list of dict, then will be converted
        to `pytraj.datasetlist.DatasetList` object

    Examples
    --------
    (fill me)
    '''
    if restype == 'ndarray':
        import numpy as np
        return np.hstack((x[name] for x in clients))
    elif restype == 'dataset':
        # it's user's responsibility to return a list of dicts
        from pytraj import datasetlist
        iter_of_dslist = (
            datasetlist._from_full_dict(x[name]) for x in clients)
        return datasetlist.vstack(iter_of_dslist)
    elif restype == 'dict':
        return concat_dict((x[name] for x in clients))
    else:
        raise ValueError("must be ndarray | dataset | dict")


def _worker_state(rank, n_cores=1, traj=None, lines=[], dtype='dict'):
    # need to make a copy if lines since python's list is dangerous
    # it's easy to mess up with mutable list
    # do not use lines.copy() since this is not available in py2.7
    my_lines = [line for line in lines]
    from pytraj.utils import split_range
    from pytraj.core.cpptraj_core import _load_batch

    mylist = split_range(n_cores, 0, traj.n_frames)[rank]
    start, stop = mylist
    crdframes_string = 'crdframes ' + ','.join((str(start+1), str(stop)))

    for idx, line in enumerate(my_lines):
        if not line.lstrip().startswith('reference'):
            my_lines[idx] = ' '.join(('crdaction traj', line, crdframes_string))

    my_lines = ['loadtraj name traj',] + my_lines

    state = _load_batch(my_lines, traj)
    state.run()
    if dtype == 'dict':
        return (rank, state.data[1:].to_dict())
    elif dtype == 'state':
        return state