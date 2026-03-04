# coding: utf-8
"""

    ファイル名：    LogDiff.py

    処理内容：      ログファイルの diff

    Copyright (c) 2017, Masatsuyo Takahashi, KEK-PF

"""
import re
from difflib    import unified_diff
from io         import StringIO

log_diff_re = re.compile( r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' )
time_re     = re.compile( r'was \d\.\d+ seconds' )

def time_re_sub( line ):
    return re.sub( time_re, 'was S.SSS seconds', line )

def make_log_diff( from_file, to_file, re_sub=None ):

    def substitute( line ):
        line = re.sub( log_diff_re, 'YYYY-mm-dd HH:MM:SS', line )
        if re_sub is not None:
            line = re_sub( line )
        return line

    log_text_list = []
    for file in [from_file, to_file]:
        fh = open( file )
        text = [ substitute(line) for line in fh ]
        log_text_list.append( text )

    buff = StringIO()
    buff.writelines( unified_diff( log_text_list[0], log_text_list[1], fromfile=from_file, tofile=to_file ) )

    return buff.getvalue()
