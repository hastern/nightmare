#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
This file contains an assorted collection of utilities:
    - Terminal coloring
    - A custom logger
"""

from typing import List

import sys
import os
import time


class TermColor:
    """ Print colored text """

    Black = 0
    """Black color code"""
    Red = 1
    """Red color code"""
    Green = 2
    """Green color code"""
    Yellow = 3
    """Yellow color code"""
    Blue = 4
    """Blue color code"""
    Purple = 5
    """Purple color code"""
    Cyan = 6
    """Cyan color code"""
    White = 7
    """White color code"""
    Normal = 0
    """Normal text style"""
    Bold = 1
    """Bold text style"""
    Dim = 2
    """Dim text style"""
    Background = 40
    """Change background color"""
    Text = 30
    """Change text color"""

    active = True
    """activate colorful output"""

    @staticmethod
    def colorText(text, fg=7, bg=0, style=0):
        if TermColor.active and (os.getenv("ANSI_COLORS_DISABLED") is None):
            return f"\033[{style:02};{fg + TermColor.Text:2};{bg + TermColor.Background:2}m{text:s}\033[0m"
        else:
            return text


@staticmethod
def logPrinter(msg):
    print(msg)


class logger:
    """Logger class"""

    _buffer: List[str] = []
    """Message buffer"""
    autoflush = False
    """Auto flush logged messages"""
    logListener = logPrinter
    """Listener to redirect output"""

    @staticmethod
    def log(str, showTime=True):
        """
        Writes a log message to the buffer

        @type    str: String
        @param    str: Log message
        """
        if showTime:
            msg = (
                TermColor.colorText(f"[{time.strftime('%H:%M:%S')}]", TermColor.Blue, style=TermColor.Dim)
                + " "
                + str.strip("\r\n")
            )
        else:
            msg = "           " + str.strip("\r\n")
        if logger.autoflush:
            logger.logListener(msg)
        else:
            logger._buffer.append(msg)

    @staticmethod
    def flush(quiet=False):
        """
        flushes the message buffer

        @type    quiet: Boolean
        @param    quiet: Flag if the buffer should be printed or not
        """
        if not quiet:
            for b in logger._buffer:
                logger.logListener(b)
            sys.stdout.flush()
        logger.clear()

    @staticmethod
    def clear():
        """
        Clears the buffer
        """
        logger._buffer = []
