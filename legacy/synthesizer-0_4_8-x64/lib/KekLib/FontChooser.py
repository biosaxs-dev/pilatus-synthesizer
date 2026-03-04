from __future__ import division, print_function, unicode_literals

from OurTkinter     import Dialog, Font
from OurTix         import tix

class FontChooser( Dialog ):
    BASIC = 1
    ALL   = 2

    def __init__( self, parent, defaultfont=None, showstyles=None ):
        self._family       = tix.StringVar(  value='Ariel'       )
        self._sizeString   = tix.StringVar(  value='12'          )
        self._weight       = tix.StringVar(  value=Font.NORMAL )
        self._slant        = tix.StringVar(  value=Font.ROMAN  )
        self._isUnderline  = tix.BooleanVar( value=False         )
        self._isOverstrike = tix.BooleanVar( value=False         )

        if defaultfont:
            self._initialize( defaultfont )

        self._currentFont  = Font.Font( font=self.getFontTuple() )

        self._showStyles   = showstyles

        self.sampleText      = None

        Dialog.__init__( self, parent, 'Font Chooser' )

    def _initialize( self, aFont ):
        if not isinstance( aFont, Font.Font ):
            aFont = Font.Font( font=aFont )

        fontOpts = aFont.actual( )

        self._family.set(       fontOpts[ 'family'     ] )
        self._sizeString.set(   fontOpts[ 'size'       ] )
        self._weight.set(       fontOpts[ 'weight'     ] )
        self._slant.set(        fontOpts[ 'slant'      ] )
        self._isUnderline.set(  fontOpts[ 'underline'  ] )
        self._isOverstrike.set( fontOpts[ 'overstrike' ] )

    def body( self, master ):
        theRow = 0

        tix.Label( master, text="Font Family" ).grid( row=theRow, column=0 )
        tix.Label( master, text="Font Size" ).grid( row=theRow, column=2 )

        theRow += 1

        # Font Families
        fontList = tix.ComboBox( master, command=self.selectionChanged, dropdown=False, editable=False, selectmode=tix.IMMEDIATE, variable=self._family )
        fontList.grid( row=theRow, column=0, columnspan=2, sticky=tix.N+tix.S+tix.E+tix.W, padx=10 )
        first = None
        familyList = list(Font.families( ))
        familyList.sort()
        for family in familyList:
            if family[0] == '@':
                continue
            if first is None:
                first = family
            fontList.insert( tix.END, family )
        fontList.configure( value=first )

        # Font Sizes
        sizeList = tix.ComboBox( master, command=self.selectionChanged, dropdown=False, editable=False, selectmode=tix.IMMEDIATE, variable=self._sizeString )
        sizeList.grid( row=theRow, column=2, columnspan=2, sticky=tix.N+tix.S+tix.E+tix.W, padx=10 )
        for size in range( 6,31 ):
            sizeList.insert( tix.END, '%d' % size )
        sizeList.configure( value='9' )

        # Styles
        if self._showStyles is not None:
            theRow += 1

            if self._showStyles in ( FontChooser.ALL, FontChooser.BASIC ):
                tix.Label( master, text='Styles', anchor=tix.W ).grid( row=theRow, column=0, pady=10, sticky=tix.W )
                
                theRow += 1
                
                tix.Checkbutton( master, text="bold", command=self.selectionChanged, offvalue='normal', onvalue='bold', variable=self._weight ).grid(row=theRow, column=0)
                tix.Checkbutton( master, text="italic", command=self.selectionChanged, offvalue='roman', onvalue='italic', variable=self._slant ).grid(row=theRow, column=1)

                if self._showStyles == FontChooser.ALL:
                     tix.Checkbutton( master, text="underline", command=self.selectionChanged, offvalue=False, onvalue=True, variable=self._isUnderline ).grid(row=theRow, column=2)
                     tix.Checkbutton( master, text="overstrike", command=self.selectionChanged, offvalue=False, onvalue=True, variable=self._isOverstrike ).grid(row=theRow, column=3)

        # Sample Text
        theRow += 1

        tix.Label( master, text='Sample Text', anchor=tix.W ).grid( row=theRow, column=0, pady=10, sticky=tix.W )

        theRow += 1

        self.sampleText = tix.Text( master, height=11, width=70 )
        self.sampleText.insert( tix.INSERT,
                               'ABCDEFGHIJKLMNOPQRSTUVWXYZ\nabcdefghijklmnopqrstuvwxyz', 'fontStyle' )
        self.sampleText.config( state=tix.DISABLED )
        self.sampleText.tag_config( 'fontStyle', font=self._currentFont )
        self.sampleText.grid( row=theRow, column=0, columnspan=4, padx=10 )

    def apply( self ):
        self.result = self.getFontTuple( )

    def selectionChanged( self, something=None ):
        self._currentFont.configure( family=self._family.get(), size=self._sizeString.get(),
                                     weight=self._weight.get(), slant=self._slant.get(),
                                     underline=self._isUnderline.get(),
                                     overstrike=self._isOverstrike.get() )

        if self.sampleText:
            self.sampleText.tag_config( 'fontStyle', font=self._currentFont )

    def getFontTuple( self ):
        family = self._family.get()
        size   = int(self._sizeString.get())

        styleList = [ ]
        if self._weight.get() == Font.BOLD:
            styleList.append( 'bold' )
        if self._slant.get() == Font.ITALIC:
            styleList.append( 'italic' )
        if self._isUnderline.get():
            styleList.append( 'underline' )
        if self._isOverstrike.get():
            styleList.append( 'overstrike' )
          
        if len(styleList) == 0:
            return family, size
        else:
            return family, size, ' '.join( styleList )

def askChooseFont( parent, defaultfont=None, showstyles=FontChooser.ALL ):
    return FontChooser( parent, defaultfont=defaultfont, showstyles=showstyles ).result

if __name__ == '__main__':
    root = tix.Tk( )
    font = askChooseFont( root )
    if font:
        print( font )
