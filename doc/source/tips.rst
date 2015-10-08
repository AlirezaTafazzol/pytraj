.. _tips:

Tips
====

.. contents::

.. _process_many_files:

process many files
------------------

Normally, user needs to follow below code to process many files

.. ipython:: python

    import pytraj as pt
    import numpy as np
    template = 'tz2.%s.nc'
    flist = [template % str(i) for i in range(4)]
    print(flist)
    trajlist = [pt.iterload(fname, 'tz2.parm7') for fname in flist]

    # calculate radgyr
    data = []
    for traj in trajlist:
        data.append(pt.radgyr(traj))
    data = np.array(data).flatten()
    print(data)

However, ``pytraj`` offer shorter (and easy?) way to do

.. ipython:: python
    
    # load all files into a single TrajectoryIterator
    filelist = ['tz2.0.nc', 'tz2.1.nc', 'tz2.2.nc']
    traj = pt.iterload(filelist, 'tz2.parm7')
    # perform calculation
    data = pt.radgyr(traj)
    # that's it
    print(data)

``pytraj`` will auto-allocate ``data`` too

.. ipython:: python
    
    print([t.filename.split('/')[-1] for t in trajlist])
    data = pt.radgyr(trajlist, top=trajlist[0].top)
    print(data)

load from a list of files with frame stride
-------------------------------------------

Supposed you have a list of 5 (or whatever) trajectories, you only want to load those files 1st to 100-th frames
and skip every 10 frames. Below is a convention ``cpptraj`` input.

.. code-block:: bash

    parm 2koc.parm7
    trajin traj0.nc 1 100 10
    trajin traj1.nc 1 100 10
    trajin traj2.nc 1 100 10
    trajin traj3.nc 1 100 10
    trajin traj4.nc 1 100 10

In ``pytraj``, you can specify ``frame_slice``

.. code-block:: python

    import pytraj as pt
    pt.iterload('traj*.nc', top='2koc.parm7', frame_slice=[(0, 100, 10),]*5)

    # [(0, 100, 10),]*5 is equal to [(0, 100, 10), (0, 100, 10),(0, 100, 10),(0, 100, 10),(0, 100, 10),]

load specific frame numbers to memory
-------------------------------------

.. ipython:: python

    import pytraj as pt
    frame_indices = [2, 4, 7, 51, 53]
    # use ``load`` to load those frames to memory
    traj0 = pt.load('tz2.nc', 'tz2.parm7', frame_indices=frame_indices)
    traj0

    # only loadd coordinates for specific atoms
    traj1 = pt.load('tz2.nc', 'tz2.parm7', frame_indices=frame_indices, mask='@CA')
    traj1

    # or use ``iterload``
    frame_indices = [2, 4, 7, 51, 53]
    traj2 = pt.iterload('tz2.nc', 'tz2.parm7')
    traj2
    traj2[frame_indices, '@CA']

merge multiple trajectories to a single file
--------------------------------------------

.. ipython:: python

    import pytraj as pt
    # load multiple files
    traj = pt.iterload(['tz2.0.nc', 'tz2.1.nc', 'tz2.2.nc'], top='tz2.parm7')
    traj.save('tz2_combined.nc', overwrite=True)

memory saving
-------------

If memory is critical, do not load all frames into memory.

.. ipython:: python

    # DO this (only a single frame will be loaded to memory)
    pt.radgyr(traj, frame_indices=[0, 200, 300, 301])

    # DON'T do this if you want to save memory (all 4 frames will be loaded to memory)
    pt.radgyr(traj[[0, 200, 300, 301]])

    pt.iterframe(traj, frame_indices=[0, 200, 300, 301])
    traj[[0, 200, 300, 301]]

See also: :ref:`trajectory_slice`

convert trajectory
------------------

.. code-block:: python
    
    # convert Amber netcdf to Charmm dcd file.
    pt.iterload('traj.nc', 'prmtop').save('traj.dcd', overwrite=True)

pickle data
-----------

Sometimes you need to perform very long analysis (hours), you need to save the output to
disk to do further analysis. You have options to save data to different files and write
code to load the data back. However, you can use ``pytraj.to_pickle`` nad
``pytraj.read_pickle`` to save the state of data. Check the example:

.. ipython:: python

    traj3 = pt.load_pdb_rcsb('1l2y')
    data = pt.dssp(traj, ':3-7')
    data
    pt.to_pickle(data, 'my_data.pk')
    # load the data's state back for further analysis
    pt.read_pickle('my_data.pk')
    # note: do not read_pickle from files that don't belong to you. It's not secure.

speed up calculation with paralle (mpi4py)
------------------------------------------

Just experimental code, try it with your own risk

.. code-block:: bash

    $ cat radgyr_mpi.sh
    import pytraj as pt
    
    # add extra lines
    from pytraj.parallel import map_mpi
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    
    traj = pt.iterload('md.nc', 'tc5bwat.top')
    data = map_mpi(pt.radgyr, traj, '@CA')
    
    if comm.rank == 0:
        pt.to_pickle(data, 'data.pk')

    $ # run
    $ mpirun -n 4 python radgyr_mpi.sh

 
read cpptraj manual
-------------------

This does not work with ipython-notebook but it's still good for interactive ipython

.. code-block:: python

    In [106]: import pytraj as pt
    In [107]: pt.info('radgyr')
            [<name>] [<mask1>] [out <filename>] [mass] [nomax] [tensor]
              Calculate radius of gyration of atoms in <mask>
