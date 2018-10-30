#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import sys

from .case import TestState
from .suite import TestSuite
from .runner import TestRunner
from .utils import TermColor


"""
Provides the entry point for the software.

Attempts to parse arguments provided at the command line.
If not arguments are given, will launch a GUI.
Imports for the GUI (namely wxPython) will only be made if the GUI is
actually used. This allows the program to run, even if no wxPython is
present on the system.
"""


def main():
    # Check whether wxpython is installed or not
    try:
        import wx

        # Has the exe been double clicked? -> Try GUI
        # Allow at max 1 parameter if a testbench has been dropped onto the
        # the exe.
        if sys.argv[0].endswith(".exe") and len(sys.argv) < 2:
            sys.argv.append("--gui")
    except ImportError:
        if "--no-gui" not in sys.argv:
            sys.argv.append("--no-gui")

    if "--no-color" in sys.argv:
        TermColor.active = False
    if "--version" in sys.argv:
        runner = TestRunner(flush=True)
    elif "--gui" in sys.argv:
        # Capt. Obvious: We're running the GUI
        from gui import TestRunnerGui

        if len(sys.argv) > 1 and not sys.argv[1].startswith("-") and os.path.exists(sys.argv[1]):
            sys.argv[1] = "--bench=" + sys.argv[1]
        gui = TestRunnerGui()
        gui.buildWindow()
        gui.show()
    else:
        # Capt. Obvious: We're running in console mode
        runner = TestRunner()
        runner.parseArgv()
        suite = runner.loadSuite()
        if suite is not None:
            for testcase in runner.run():
                pass
            if not runner.options["info"] and not runner.options["length"] and not runner.options["quiet"]:
                print(f"{suite.getRate():2.2f}%")
            sys.exit(int(suite.lastResult) if suite.lastResult not in [TestState.Waiting, TestState.InfoOnly] else 0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
