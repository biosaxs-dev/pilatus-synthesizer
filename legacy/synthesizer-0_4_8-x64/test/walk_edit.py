#   walk_edit.py
import os
import re

folder = '.'
for root, dirs, files in os.walk( folder ):
    for file in files:
        if not re.search( r'\.py$', file ): continue
        path = os.path.join( root, file )
        # print( path )
        try:
            fh = open( path, encoding='utf-8' )
            src = ''.join( [ line for line in fh ] )
            fh.close()
            ( mdy, n ) = re.subn( r"\nsys\.path\.append\(.+'/../lib'\s*\)\s*\n", r"\g<0>import KekLib, Synthesizer\n", src, count=1 )
            if n == 0:
                print( path + ' ... skipped' )
                continue

            bak = path.replace( '.py', '.bak' )
            if os.path.exists( bak ):
                print( path + ' ... bak exists' )
                continue

            mdy = mdy.replace( '\r', '' )
            tmp = path.replace( '.py', '.tmp' )
            fh = open( tmp, 'wb' )
            fh.write( mdy.encode() )
            fh.close()
            os.rename( path, bak )
            os.rename( tmp, path )
            print( path + ' ... edited' )
        except Exception as exc:
            print( path + ' ... error' + str(exc) )
