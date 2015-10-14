import os

auto_install_message = """
Can not find cpptraj header and libcpptraj files.
We're trying to dowload and build libcpptraj for you, would take about 5-10 minutes.
You can check ./cpptraj/ folder after installation.

To avoid auto-installation
--------------------------
You should set CPPTRAJHOME or installing ./cpptraj/ in this current folder.

If you want to manually install `libcpptraj`, you can download cpptraj
development version from here: https://github.com/Amber-MD/cpptraj

$ git clone https://github.com/Amber-MD/cpptraj/
$ cd cpptraj
$ export CPPTRAJHOME=`pwd`
$ ./configure -shared gnu
$ make libcpptraj

and then go back to pytraj folder:
python setup.py install
"""

def remind_export_LD_LIBRARY_PATH(build_tag, libdir, pytraj_inside_amber):
    if build_tag:
        if not pytraj_inside_amber:
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
            # pytraj is a part of Amber
            print('make sure to `source $AMBERHOME/amber.sh` (if using bash) '
                  'or `source $AMBERHOME/amber.csh` if using csh')
    else:
        print("not able to install pytraj")
