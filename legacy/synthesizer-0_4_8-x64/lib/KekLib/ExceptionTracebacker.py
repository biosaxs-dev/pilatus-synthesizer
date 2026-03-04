# coding: utf-8
"""
    ExceptionTracebacker.py

    Copyright (c) 2016-2020, Masatsuyo Takahashi, KEK-PF
"""
import sys
import numpy                as np
import traceback
import logging

class ExceptionTracebacker:
    def __init__( self, call_stack=False ):
        ( exc_type_type_, exc_value, exc_traceback ) = sys.exc_info()
        self.c_seq = traceback.format_stack()[:-2] if call_stack else []
        self.e_seq = traceback.format_exception( exc_type_type_, exc_value, exc_traceback)[1:]

    def __str__( self ):
        return ''.join( self.c_seq + self.e_seq )

    def __repr__( self ):
        return self.__str__()

    def log( self ):
        logger  = logging.getLogger( __name__ )
        logger.error( str(self) )

    def last_line( self ):
        return self.e_seq[-1][:-1]      # remove trailing '\n'

    def last_lines( self, n=2 ):
        return ''.join(self.e_seq[-n:])

def log_exception(logger, message):
    etb = ExceptionTracebacker()
    logger.warning(message + etb.last_lines())
