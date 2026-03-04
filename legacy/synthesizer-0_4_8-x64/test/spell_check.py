import os
import codecs
import re
from enchant.checker    import SpellChecker

ext_re = re.compile( '.+\.(py|txt)$' )
checker = SpellChecker("en_US")

os.chdir( '../' )
root_dir = os.getcwd()

for root, dirs, files in os.walk( root_dir ):
    if root.find( '__pycache__' ) >= 0:
        continue
    if root.find( 'synthesizer' ) >= 0:
        continue

    print( 'Checking %s' % root )
    # print( root, dirs )
    for file in files:
        if not ext_re.match( file ):
            continue

        print( "\tChecking %s" % ( file ) )
        path = os.path.join( root, file )
        fh = codecs.open( path, "r", "utf-8" )
        text = fh.read()
        fh.close()
        checker.set_text( text )
        for err in checker:
            print( err )
