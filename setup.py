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
from time import sleep
import subprocess
from subprocess import CalledProcessError
from random import shuffle
from distutils.core import setup, Command
from distutils.extension import Extension
import distutils.ccompiler
from functools import partial
from glob import glob
from itertools import chain

if sys.version_info < (2, 6):
    sys.stderr.write('You must have at least Python 2.6 for pytraj\n')
    sys.exit(0)


PYTRAJ_DIR = os.path.abspath(os.path.dirname(__file__))

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if sys.platform == 'darwin':
    # copied from ParmEd
    # You *need* to use clang and clang++ for extensions on a Mac;
    # Anaconda does annoying stuff that breaks this, since their distutils
    # automatically tries to use "gcc", which would conflict with the MacPorts
    # gcc... sigh.
    os.environ['CXX'] = 'clang++'
    os.environ['CC'] = 'clang'

pytraj_version = read("pytraj/__version__.py").split("=")[-1]
pytraj_version = pytraj_version.replace('"', '', 10)
rootname = os.getcwd()
pytraj_home = rootname + "/pytraj/"

openmp_str = "openmp"
if openmp_str in sys.argv:
    # python ./setup.py build openmp
    # make sure to update Makefile in $AMBERHOME/AmberTools/src
    # if changing '-openmp' to something else
    with_openmp = True
    sys.argv.remove(openmp_str)
else:
    with_openmp = False

faster_build_str = "faster"

KeyErrorTXT = """
Can not use -faster_build with `install`,
try  "python ./setup.py build faster_build
then "python ./setup.py install" 
"""

if faster_build_str in sys.argv:
    # try using multiple cores
    faster_build = True
    sys.argv.remove(faster_build_str)
    if "install" in sys.argv:
        sys.stderr.write(KeyErrorTXT)
        sys.exit(0)
    if 'build' not in sys.argv:
        sys.stderr.write('faster must come with build')
        sys.exit(0)
else:
    faster_build = False

if len(sys.argv) == 2 and sys.argv[1] == 'install':
    do_install = True
else:
    do_install = False

if len(sys.argv) == 2 and sys.argv[1] == 'build':
    do_build = True
else:
    do_build = False

# require cython version >= 0.23 for now.
cmdclass = {}
try:
    import Cython
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
    has_cython = True
    cmdclass['build_ext'] = build_ext
    if Cython.__version__ < '0.23':
        raise ImportError
except ImportError:
    #has_cython = False
    #from distutils.command.build_ext import build_ext 
    #cmdclass['build_ext'] = build_ext
    sys.stderr.write('Building from source requires cython >= 0.23 \n')
    sys.exit(0)

# check AMBERHOME
try:
    amberhome = os.environ['AMBERHOME']
    has_amberhome = True
except KeyError:
    has_amberhome = False

# check CPPTRAJHOME or "./cpptraj" folder
try:
    cpptrajhome = os.environ['CPPTRAJHOME']
    has_cpptrajhome = True
except KeyError:
    has_cpptrajhome = False

has_cpptraj_in_current_folder = os.path.exists("./cpptraj/")

# check if has environment variables
CPPTRAJ_LIBDIR = os.environ.get('CPPTRAJ_LIBDIR', '')
CPPTRAJ_HEADERDIR = os.environ.get('CPPTRAJ_HEADERDIR', '')

AMBERHOME = os.environ.get('AMBERHOME', '')
PYTRAJ_AMBER_DIR = os.path.join(AMBERHOME, 'AmberTools', 'src', 'pytraj')


if PYTRAJ_AMBER_DIR == PYTRAJ_DIR:
    # install pytraj inside AMBER
    CPPTRAJ_LIBDIR = os.path.join(AMBERHOME, 'lib')
    CPPTRAJ_HEADERDIR = os.path.join(AMBERHOME, 'AmberTools', 'src', 'cpptraj', 'src')

if CPPTRAJ_LIBDIR and CPPTRAJ_HEADERDIR:
    cpptraj_include = CPPTRAJ_HEADERDIR
    libdir = CPPTRAJ_LIBDIR
else:
    if has_cpptrajhome:
        # use libcpptraj and header files in CPPTRAJHOME (/lib, /src)
        cpptraj_dir = cpptrajhome
        cpptraj_include = cpptraj_dir + "/src/"
        libdir = cpptrajhome + "/lib/"
    elif has_cpptraj_in_current_folder:
        cpptraj_dir = os.path.abspath("./cpptraj/")
        cpptraj_include = cpptraj_dir + "/src/"
        libdir = cpptraj_dir + "/lib/"
    else:
        nice_message = """
        We're trying to dowload and build libcpptraj for you. (5-10 minutes)
        (check ./cpptraj/ folder after installation)
    
        To avoid auto-installation
        --------------------------
        Must set CPPTRAJHOME or installing ./cpptraj/ in current folder.
    
        If you want to manually install `libcpptraj`, you can download cpptraj
        development version from here: https://github.com/Amber-MD/cpptraj
    
        $ git clone https://github.com/Amber-MD/cpptraj/
        $ cd cpptraj
        $ export CPPTRAJHOME=`pwd`
        $ ./configure -shared gnu
        $ make libcpptraj
    
        and then go back to pytraj folder:
        python setup.py install
        ...
        """

        if do_install or do_build:
            print(nice_message)
            sleep(3)
            try:
                subprocess.check_call(['sh',
                                       './installs/install_cpptraj_git.sh'])
            except CalledProcessError:
                sys.stderr.write(
                    'can not install libcpptraj, you need to install it manually \n')
                sys.exit(0)
        cpptraj_dir = os.path.join(rootname, "cpptraj")
        cpptraj_include = os.path.join(cpptraj_dir, 'src')
        libdir = os.path.join(cpptraj_dir, 'lib')

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
extra_compile_args = ['-O0', ]
extra_link_args = ['-O0', ]

list_of_libcpptraj = glob(os.path.join(libdir, 'libcpptraj') + '*')
if not list_of_libcpptraj:
    if has_cpptrajhome:
        sys.stderr.write(
            '$CPPTRAJHOME exists but there is no libcpptraj in $CPPTRAJHOME/lib \n'
            'There are two solutions: \n'
            '1. unset CPPTRAJHOME and `python setup.py install` again. We will install libcpptraj for you. \n'
            '2. Or you need to install libcpptraj in $CPPTRAJHOME/lib \n')
        sys.exit(0)
    if do_install or do_build:
        if has_cpptraj_in_current_folder:
            print(
                'can not find libcpptraj but found ./cpptraj folder, trying to reinstall it to ./cpptraj/lib/ \n')
            sleep(3)
            try:
                subprocess.check_call(
                    ['sh', './installs/install_cpptraj_current_folder.sh'])
                cpptraj_include = os.path.join(cpptraj_dir, 'src')
            except CalledProcessError:
                sys.stderr.write(
                    'can not install libcpptraj, you need to install it manually \n')
                sys.exit(0)
        else:
            sys.stderr.write('can not find libcpptraj in $CPPTRAJHOME/lib. '
                             'You need to install ``libcpptraj`` manually. ')
            sys.exit(0)

if with_openmp:
    extra_compile_args.append("-fopenmp")
    extra_link_args.append("-fopenmp")

# since we added "INSTALLTYPE" after setup.py file, we need
# to remove it if having one
installtype = os.environ.get("INSTALLTYPE", "")
try:
    sys.argv.remove(installtype)
except ValueError:
    pass

# pre-cythonize files in parallel
cython_directives = {
        'embedsignature': True,
        'boundscheck': False,
        'wraparound': False,
    }

cythonize(
    [pfile + '.pyx' for pfile in pyxfiles],
    nthreads=int(os.environ.get('NUM_THREADS', 6)),
    compiler_directives=cython_directives,
    )

ext_modules = []
for ext_name in pyxfiles:
    if has_cython:
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
                       library_dirs=[libdir, ],
                       include_dirs=[cpptraj_include, pytraj_home],
                       extra_compile_args=extra_compile_args,
                       extra_link_args=extra_link_args)
    ext_modules.append(extmod)

#shuffle(ext_modules)
setup_args = {}
packages = [
    'pytraj',
    'pytraj.utils',
    'pytraj.actions',
    'pytraj.analyses',
    'pytraj.datasets',
    'pytraj.externals',
    'pytraj.trajs',
    'pytraj.datafiles',
    'pytraj.datafiles.Ala3',
    'pytraj.datafiles.tz2',
    'pytraj.plot',
    'pytraj.math',
    'pytraj.core',
    'pytraj.parallel',
    'pytraj.cluster',
    'pytraj.sandbox',
]

pylen = len('pytraj') + 1
pxdlist = [p.replace("pytraj/", "") for p in pxd_include_patterns]
sample_data = ["datafiles/Ala3/Ala3.*", "datafiles/tz2/tz2.*"]
datalist = pxdlist + sample_data


def build_func(my_ext):
    return setup(
        name="pytraj",
        version=pytraj_version,
        author="Hai Nguyen",
        author_email="hainm.comp@gmail.com",
        url="https://github.com/Amber-MD/pytraj",
        packages=packages,
        description=
        """Python API for cpptraj: a data analysis package for biomolecular simulation""",
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
        ext_modules=my_ext,
        package_data={'pytraj': datalist},
        cmdclass=cmdclass, )


def remind_ld_lib_path(build_tag, libdir):
    if build_tag:
        from scripts.acsii_art import batman
        print("")
        print("")
        print(batman)
        libdir = os.path.abspath(libdir)
        print('make sure to add %s to your LD_LIBRARY_PATH \n\n'
              'example: export LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH\n\n'
              'try simple test: python ./runtests.py simple\n\n' %
              (libdir, libdir))
        print("")
    else:
        print("not able to install pytraj")


if __name__ == "__main__":
    if not faster_build:
        build_tag = build_func(ext_modules)
        if do_install:
            remind_ld_lib_path(build_tag, libdir)
    else:
        from multiprocessing import cpu_count
        n_cpus = cpu_count()
        num_each = int(len(ext_modules) / n_cpus)

        sub_ext_modules_list = []
        # there is idiom to do this but I am too lazy to think
        for i in range(n_cpus):
            if i != n_cpus - 1:
                sub_ext_modules_list.append(
                    ext_modules[i * num_each:num_each * (i + 1)])
            else:
                sub_ext_modules_list.append(ext_modules[num_each * i:])

        #from multiprocessing import Pool
        from  multiprocessing.pool import ThreadPool as Pool
        pool = Pool(n_cpus)
        pool.map(build_func, sub_ext_modules_list)
        try:
            p.close()
            p.join()
        except AttributeError:
            pass
