import sys
import glob
import subprocess

packages = [
        'AutoRunController',
        'BasicUtils',
        'CommandController',
        'ChangeableLogger',
        'Development',
        'GuiSettingInfo',
        'GuiPreferences',
        'GuiController',
        'ImageSynthesizer',
        'MinimalTiff',
        'PersistentInfo',
        'PilatusCounter',
        'PilatusImageInfoTable',
        'PilatusImageViewer',
        'PilatusUtils',
        'Preferences',
        'SAnglerMask',
        'Settings',
        'OurColorMaps',
        'OurImageIO',
        'ZoomPan',
    ]

# subprocess.call( 'nosetests --verbose --with-coverage --cover-erase --cover-package=' + ','.join( packages ), shell=True )

def get_test_script( name ):
    files = glob.glob( 'test*' + name + '*.py' )
    print( files )
    assert( len( files ) == 1 )
    return files[0]

def get_cover_package( name ):
    for p in packages:
        if p.find( name ) >= 0:
            return p
    assert( False )

num_args = len( sys.argv ) - 1
assert( num_args >= 0 )

if num_args == 0:
    subprocess.Popen( [
        'nosetests',
        '--verbose',
        '--with-coverage',
        '--cover-erase',
        '--cover-package',
        ','.join( packages ),
        ], stdout=sys.stdout )
else:
    name = sys.argv[1]
    script  = get_test_script( name )
    cover   = get_cover_package( name )
    subprocess.Popen( [
        'nosetests',
        script,
        '--verbose',
        '--with-coverage',
        '--cover-erase',
        '--cover-package',
        cover,
        ], stdout=sys.stdout )
