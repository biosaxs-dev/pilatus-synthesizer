import sys
import os
import shutil
# from nose.tools import eq_

this_dir = os.path.dirname( os.path.abspath( __file__ ) )
sys.path.append( this_dir + '/../lib' )
import KekLib, Synthesizer
from BasicUtils import clear_dirs_with_retry
from AutoRunTestTools import RscSimulator

sys.path.append( this_dir + '/../..' )
from SynthesizerTestEnv import get_data_folder 

temp_dir = os.path.join(this_dir, 'temp')

def test_setup():
    clear_dirs_with_retry( [temp_dir] )

def test_RscSimulator():
    # in_folder = os.path.join(get_data_folder('20201020'), 'test101')
    in_folder = r"D:\Synthesizer\Data\20240927\1.測定中のAlert\testfilename\casec292saxs_tiffiles_copyed"
    out_folder = temp_dir

    rs = RscSimulator(in_folder, temp_dir)
    rs.run()

if __name__ == '__main__':
    test_setup()
    test_RscSimulator()
