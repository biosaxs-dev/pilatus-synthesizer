import re

src = "aaaa\nsys.path.append( os.path.dirname( os.path.abspath( __file__ ) ) + '/../lib' )\nbbb"
mdy = re.sub( r"\nsys\.path\.append\(.+'/../lib'\s*\)\s*$", r'\g<0>XXXXX', src )

print( mdy )
