'''install rule
- if pytraj is inside $AMBERHOME, use libcpptraj.so in $AMBERHOME/lib and header file in cpptraj/src folder
- if pytraj is outside $AMBERHOME
    - check CPPTRAJ_LIBDIR and CPPTRAJ_HEADERDIR: if found, use those to install
    - if not CPPTRAJ_LIBDIR, CPPTRAJ_HEADERDIR: check CPPTRAJHOME and found libcpptraj.so and header files in
    CPPTRAJHOME/{lib, src}
    - if not CPPTRAJHOME, find cpptraj folder in current folder
    - if can not find cpptraj folder, do git clone from github
'''

import os
import sys
import time
import subprocess
from subprocess import CalledProcessError
from distutils.core import setup
from distutils.extension import Extension
from glob import glob

# local import
from scripts.base_setup import (check_flag, check_cpptraj_version, write_version_py, get_version_info,
                                get_include_and_lib_dir, do_what)
from scripts.base_setup import (try_updating_libcpptraj, remind_export_LD_LIBRARY_PATH)
from scripts.base_setup import (message_openmp_cpptraj, message_serial_cpptraj, message_auto_install,
                                message_cython)
from scripts.base_setup import CleanCommand, ISRELEASED

# python version >= 2.6
if sys.version_info < (2, 6):
    print('You must have at least Python 2.6 for pytraj\n')
    sys.exit(0)

amber_release = check_flag('--amber_release')
disable_openmp = check_flag('--disable-openmp')
debug = check_flag('--debug')
use_phenix_python = check_flag('--phenix')
create_tar_file_for_release = True if 'sdist' in sys.argv else False
amber_home = os.environ.get('AMBERHOME')
has_amber_home = True if amber_home is not None else False
rootname = os.getcwd()
pytraj_home = rootname + "/pytraj/"
cpptraj_home = os.environ.get('CPPTRAJHOME', '')
has_cpptraj_in_current_folder = os.path.exists("./cpptraj/")
phenix_python_lib = os.path.join(os.environ.get('PHENIX'),
                                 'base/lib/') if use_phenix_python else ''
pytraj_dir = os.path.abspath(os.path.dirname(__file__))
do_install, do_build = do_what(pytraj_dir)
cpptraj_dir, cpptraj_include, cpptraj_libdir, pytraj_inside_amber = get_include_and_lib_dir(rootname, cpptraj_home,
        has_cpptraj_in_current_folder, do_install, do_build, pytraj_dir)
libcpptraj_files = glob(os.path.join(cpptraj_libdir, 'libcpptraj') + '*')
do_clean = (len(sys.argv) == 2 and 'clean' in sys.argv)
write_version_py()
FULLVERSION, GIT_REVISION = get_version_info()


cython_directives = {
    'embedsignature': True,
    'boundscheck': False,
    'wraparound': False,
}

if debug:
    cython_directives.update({
        'profile': True,
        'linetrace': True,
        'binding': True})
    define_macros = [('CYTHON_TRACE', 1), ]
else:
    define_macros = []

# get INSTALLTYPE type from amber
installtype = os.environ.get("INSTALLTYPE", "")

if installtype:
    sys.argv.remove(installtype)


# python setup.py clean
cmdclass = {'clean': CleanCommand}

if ISRELEASED:
    # ./devtools/mkrelease
    need_cython = False
else:
    try:
        import Cython
        from Cython.Distutils import build_ext
        from Cython.Build import cythonize
        need_cython = True
        cmdclass['build_ext'] = build_ext
        if Cython.__version__ < '0.21':
            print(message_cython)
            sys.exit(0)
    except ImportError:
        print(message_cython)
        sys.exit(0)


def read(fname):
    # must be in this setup file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if sys.platform == 'darwin':
    # copied from ParmEd
    # You *need* to use clang and clang++ for extensions on a Mac;
    # Anaconda does annoying stuff that breaks this, since their distutils
    # automatically tries to use "gcc", which would conflict with the MacPorts
    # gcc... sigh.
    os.environ['CXX'] = 'clang++'
    os.environ['CC'] = 'clang'

# get *.pyx files
pxd_include_dirs = [
    directory for directory, dirs, files in os.walk('pytraj') if '__init__.pyx'
    in files or '__init__.pxd' in files or '__init__.py' in files
]

pxd_include_patterns = [p + '/*.pxd' for p in pxd_include_dirs]

pyxfiles = []
for p in pxd_include_dirs:
    pyxfiles.extend([ext.split(".")[0] for ext in glob(p + '/*.pyx')
                     if '.pyx' in ext])

# check command line
extra_compile_args = ['-O0', '-ggdb', ]
extra_link_args = ['-O0', '-ggdb', ]

if not libcpptraj_files:
    libcpptraj_files = try_updating_libcpptraj(cpptraj_home,
            do_install, do_build, has_cpptraj_in_current_folder)

if not create_tar_file_for_release:
    add_flag_if_openmp(extra_compile_args, extra_link_args, libcpptraj_files)

check_cpptraj_version(cpptraj_include, (4, 2, 8))

if not do_clean and not ISRELEASED:
    cythonize(
        [pfile + '.pyx' for pfile in pyxfiles],
        nthreads=int(os.environ.get('NUM_THREADS', 4)),
        compiler_directives=cython_directives,
    )

library_dirs = [cpptraj_libdir, ] if not use_phenix_python else [cpptraj_libdir, phenix_python_lib]

ext_modules = []
for ext_name in pyxfiles:
    if need_cython:
        ext = ".pyx"
    else:
        ext = ".cpp"
    pyxfile = ext_name + ext

    # replace "/" by "." get module
    if "/" in ext_name:
        ext_name = ext_name.replace("/", ".")

    sources = [pyxfile]
    extmod = Extension(ext_name,
                       sources=sources,
                       libraries=['cpptraj'],
                       language='c++',
                       library_dirs=library_dirs,
                       define_macros=define_macros,
                       include_dirs=[cpptraj_include, pytraj_home],
                       extra_compile_args=extra_compile_args,
                       extra_link_args=extra_link_args)
    ext_modules.append(extmod)

setup_args = {}
packages = [
    'pytraj',
    'pytraj.utils',
    'pytraj.c_action',
    'pytraj.c_analysis',
    'pytraj.datasets',
    'pytraj.externals',
    'pytraj.c_traj',
    'pytraj.datafiles',
    'pytraj.datafiles.ala3',
    'pytraj.datafiles.tz2',
    'pytraj.datafiles.dpdp',
    'pytraj.datafiles.trpcage',
    'pytraj.datafiles.remd_ala2',
    'pytraj.plot',
    'pytraj.math',
    'pytraj.core',
    'pytraj.parallel',
    'pytraj.cluster',
    'pytraj.sandbox',
]

pylen = len('pytraj') + 1
pxdlist = [p.replace("pytraj/", "") for p in pxd_include_patterns]
sample_data = ["datafiles/ala3/Ala3.*",
               "datafiles/tz2/tz2.*",
               "datafiles/rna.pdb",
               "datafiles/trpcage/trpcage*",
               "datafiles/remd_ala2/*",
               "datafiles/dpdp/DPDP*"]
datalist = pxdlist + sample_data


def build_func(ext_modules):
    return setup(
        name="pytraj",
        version=FULLVERSION,
        author="Hai Nguyen",
        author_email="hainm.comp@gmail.com",
        url="https://github.com/Amber-MD/pytraj",
        packages=packages,
        description="""Python API for cpptraj: a data analysis package for biomolecular simulation""",
        license="BSD License",
        classifiers=[
            'Development Status :: 4 - Beta', 'Operating System :: Unix',
            'Operating System :: MacOS',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Cython', 'Programming Language :: C',
            'Programming Language :: C++', 'Topic :: Scientific/Engineering'
        ],
        ext_modules=ext_modules,
        package_data={'pytraj': datalist},
        cmdclass=cmdclass, )


if __name__ == "__main__":
    build_tag = build_func(ext_modules)
    if do_install:
        remind_export_LD_LIBRARY_PATH(build_tag, cpptraj_libdir, pytraj_inside_amber)
