# coding: utf-8
"""

    TimeUtils.py

    Copyright (c) 2019, Masatsuyo Takahashi, KEK-PF

"""
from datetime import datetime

"""
    from https://stackoverflow.com/questions/538666/format-timedelta-to-string
"""
def format_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%d:%0d:%02d' % (hours, minutes, seconds)

def seconds_to_datetime(seconds):
    return datetime.strptime(format_seconds(seconds), "%H:%M:%S")
