#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List

import os
import re
import sys
import time
import math
import argparse
import itertools
import struct
import subprocess
import collections
import fractions

try:
    import pyparsing
except:
    pyparsing = None

# from threading import Thread

from .utils import TermColor, logger
from .case import Test, TestState, TestGroup, TestAny, TestAll
from .case import Expectation, ExpectFile, Stringifier, StringifiedFile, CompareFiles
from .suite import TestSuite, TestSuiteMode
from .arnold_converter import syntax, buildTestList

import nightmare


class TestRunner(object):
    """Testrunner. Reads a testbench file and executes the testrun"""

    def __init__(self, flush=False):
        """Initialises the test runner"""
        # Thread.__init__(self)
        logger.log(
            TermColor.colorText("NIGHTMARE I", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("s of ", TermColor.White)
            + TermColor.colorText("G", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("enerous ", TermColor.White)
            + TermColor.colorText("H", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("elp when ", TermColor.White)
            + TermColor.colorText("T", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("esting; ", TermColor.White)
            + TermColor.colorText("M", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("ay ", TermColor.White)
            + TermColor.colorText("A", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("rnold be ", TermColor.White)
            + TermColor.colorText("R", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("emembered ", TermColor.White)
            + TermColor.colorText("E", TermColor.Red, style=TermColor.Bold)
            + TermColor.colorText("ternally", TermColor.White)
        )
        logger.log(f"Welcome to nightmare Version {nightmare.__version__}")
        if flush:
            logger.flush(quiet=False)
        self.options = dict()
        self.testCount = 0
        self.runsuite = None
        self.finished = None

    def setDUT(self, DUT: str):
        """
        set the Device under Test
        """
        self.options["dut"] = DUT
        if self.runsuite is not None:
            self.runsuite.setDUT(DUT)

    def getSuite(self) -> TestSuite:
        """Returns the suite. If none is loaded a new one will be created"""
        if self.runsuite is None:
            self.runsuite = TestSuite(DUT=self.options["dut"], mode=self.options["mode"])
        return self.runsuite

    def parseArgv(self):
        """Parses the argument vector"""
        args = argparse.ArgumentParser(description="A test tool for non-interactive commandline programms")
        group = args.add_argument_group("Test selection")
        group.add_argument("--bench", action="store", nargs=1, help="File which contains the testbench.")
        group.add_argument("--suite", action="store", nargs=1, help="Use testsuite SUITE from the testbench.", metavar="SUITE")
        group.add_argument("--dut", "--DUT", action="store", nargs=1, help="Set the device under test.")
        group.add_argument("--test", action="store", nargs="+", type=int, help="Run only the specified tests")
        group.add_argument("--timeout", action="store", nargs=1, type=float, help="Set a global timeout for all tests.")
        group.add_argument(
            "--arnold",
            "-a",
            action="store_true",
            default=False,
            dest="arnold",
            help="Use the arnold mode (requires pyparsing module)",
        )
        group.add_argument("--save", action="store", nargs=1, help="Save the testsuite as FILE", metavar="FILE")
        group = args.add_argument_group("Output Control")
        group.add_argument(
            "--limit",
            action="store",
            type=int,
            default=2000,
            help="Set a (soft) limit for a number of Bytes, after which output piping will we stopped. Checks are made after each line.",
        )
        group.add_argument(
            "--quiet",
            "-q",
            action="store_const",
            const=True,
            default=False,
            dest="quiet",
            help="Quiet mode. There will be no output except results.",
        )
        group.add_argument(
            "--verbose",
            "-v",
            action="store_const",
            const=False,
            dest="quiet",
            help="Verbose mode. The program gets chatty (default).",
        )
        group.add_argument(
            "--commands",
            "-C",
            action="store_true",
            default=False,
            dest="commands",
            help="Show the command executed for each test.",
        )
        group.add_argument(
            "--length",
            "-l",
            action="store_true",
            default=False,
            dest="length",
            help="Print only the number of tests in the suite.",
        )
        group.add_argument(
            "--info-only",
            "-i",
            action="store_true",
            default=False,
            dest="info",
            help="Display only test information, but don't run them.",
        )
        group.add_argument(
            "--pipe-streams",
            "-p",
            action="store_true",
            default=None,
            dest="pipe",
            help="Redirect DUT output to their respective streams.",
        )
        group.add_argument(
            "--output-fails",
            "-o",
            action="store_true",
            default=None,
            dest="output",
            help="Redirect DUT output from failed tests to their respective streams.",
        )
        group.add_argument(
            "--unify-fails",
            "-u",
            action="store_true",
            default=None,
            dest="diff",
            help="Display the unified diff of output and expectation.",
        )
        group.add_argument("--no-color", action="store_false", default=True, dest="color", help="Don't use any colored output.")
        group = args.add_argument_group("Test Flow")
        group.add_argument(
            "--continue",
            "-c",
            action="store_const",
            const=TestSuiteMode.Continuous,
            dest="mode",
            help="Continuous mode (Don't halt on failed tests).",
        )
        group.add_argument(
            "--error",
            "-e",
            action="store_const",
            const=TestSuiteMode.BreakOnError,
            dest="mode",
            help="Same as '-c', but will halt if an error occurs.",
        )
        group.add_argument(
            "--ignoreEmptyLines", "-L", action="store_true", default=None, dest="ignoreEmptyLines", help="Ignore empty lines"
        )
        group.add_argument(
            "--relative",
            "-r",
            action="store_true",
            default=False,
            dest="relative",
            help="Use a path relative to the testbench path.",
        )
        group.add_argument(
            "--cr", action="store_const", const="\r", dest="linesep", help="Force the line separation character (Mac OS)."
        )
        group.add_argument(
            "--ln",
            action="store_const",
            const="\n",
            dest="linesep",
            help="Force the line separation character (Unix / Mac OS-X).",
        )
        group.add_argument(
            "--crln", action="store_const", const="\r\n", dest="linesep", help="Force the line separation character (Windows)."
        )
        args.add_argument(
            "--gui", action="store_true", default=False, dest="gui", help="Use the GUI (experimental and unstable)."
        )
        args.add_argument("--no-gui", action="store_true", default=False, dest="gui", help="Don't use the GUI.")
        args.add_argument("--version", action="store_const", const=True, default=False, help="Display version information")
        args.set_defaults(linesep=os.linesep, bench=[""], save=[], suite=["suite"], dut=[None], timeout=[None], test=[])

        self.options.update(vars(args.parse_args()))
        self.options["bench"] = self.options["bench"][0]
        self.options["suite"] = self.options["suite"][0]
        self.options["dut"] = self.options["dut"][0]
        self.options["timeout"] = self.options["timeout"][0]

        logMessages = [
            (
                "mode",
                lambda v: "I'm running in continuous mode now"
                if v == TestSuiteMode.Continuous
                else "I'm running in continuous mode now, but will halt if an error occurs"
                if v == TestSuiteMode.BreakOnError
                else "I will halt on first fail.",
            ),
            ("suite", lambda v: f"I'm using the testsuite '{v}'"),
            ("test", lambda v: f"I'm only running test {v}" if len(v) > 0 else ""),
            ("bench", lambda v: f"I'm using testbench '{v}'"),
            ("timeout", lambda v: f"Setting global timeout to {v}"),
            ("dut", lambda v: f"Device under Test is: {v}"),
            ("commands", lambda v: "I will print every command I'll exceute." if v else ""),
            ("length", lambda v: "I will only print the number of tests" if v else ""),
            ("info", lambda v: "I will only print the test information." if v else ""),
            ("pipe", lambda v: "I will pipe all tests outputs to their respective streams" if v else ""),
            ("output", lambda v: "I will pipe failed tests outputs to their respective streams" if v else ""),
            ("diff", lambda v: "I will show the differences in output and expectations" if v else ""),
        ]
        for option, msgFunc in logMessages:
            if self.options[option] is not None:
                msg = msgFunc(self.options[option])
                if len(msg) > 0:
                    logger.log(f"\t{msg}")
        logger.flush(self.options["quiet"])

    def addTest(self) -> Test:
        test = Test(name="New Test", description="Add a description", DUT=self.options["dut"])
        test.pipe = self.options["pipe"]
        test.outputOnFail = self.options["output"]
        test.linesep = self.options["linesep"]
        self.getSuite().addTest(test)
        return test

    def loadArnold(self) -> TestSuite:
        """
        Loads a test suite in the Arnold file format.
        """
        if syntax is not None:
            logger.log("\t...using Arnold-Mode")
            syn = syntax()
            fileHnd = open(self.options["bench"])
            content = []
            for line in fileHnd:
                if not line.startswith("#") and not line.strip() == "":
                    content.append(
                        line.replace("ä", "ae")
                        .replace("Ä", "Ae")
                        .replace("ö", "oe")
                        .replace("Ö", "Oe")
                        .replace("ü", "ue")
                        .replace("Ü", "Ue")
                        .replace("ß", "ss")
                    )
            s = "".join(content)
            ast = syn.parseString(s)
            testList = buildTestList(ast)
            suite = TestSuite(*testList)
            suite.setDUT(self.options["dut"])
        else:
            logger.log("\t ... could not init arnold mode due to missing pyparsing package")
            suite = None
        return suite

    def loadPython(self) -> TestSuite:
        """
        Executes a python script and reads the suite from the resulting
        namespace.

        THIS WILL EXECUTE FOREIGN CODE BY USING EVAL.

        You have been warned!
        """
        glb = {
            "__builtins__": __builtins__,
            # External / Standard libraries
            "parser": pyparsing,
            "os": os,
            "regex": re,
            "math": math,
            "itertools": itertools,
            "struct": struct,
            "collections": collections,
            "fractions": fractions,
            # nightmare specific things
            "Test": Test,
            "Group": TestGroup,
            "Any": TestAny,
            "All": TestAll,
            "Suite": TestSuite,
            "Mode": TestSuiteMode,
            "State": TestState,
            "Expectation": Expectation,
            "ExpectFile": ExpectFile,
            "Stringifier": Stringifier,
            "StringifiedFile": StringifiedFile,
            "CompareFiles": CompareFiles,
            # Helping functions
            "readFile": lambda fname: open(fname).read().rstrip() if os.path.exists(fname) else "File not found",
        }
        ctx = {self.options["suite"]: None, "DUT": None}
        exec(open(self.options["bench"]).read(), glb, ctx)
        if self.options["suite"] in ctx:
            suite = None
            if "DUT" in ctx and ctx["DUT"] is not None and self.options["dut"] is None:
                self.setDUT(ctx["DUT"])
            if ctx[self.options["suite"]] != None:
                if ctx[self.options["suite"]].__class__ == TestSuite:
                    suite = ctx[self.options["suite"]]
                    if suite.DUT is None:
                        suite.setDUT(self.options["dut"])
                    if self.options["mode"] is None:
                        self.options["mode"] = suite.mode
                    elif suite.mode is None:
                        suite.mode = self.options["mode"]
                else:
                    suite = TestSuite(*ctx[self.options["suite"]], **{"DUT": self.options["dut"], "mode": self.options["mode"]})
            else:
                logger.log(f"Sorry, but I can't find any tests inside the suite '{self.options['suite']}'")
        else:
            logger.log("Sorry, but there was no test-suite in the file")
        return suite

    def loadSuite(self, fname: os.PathLike = None) -> TestSuite:
        """Loads a python based suite from a file"""
        if fname is not None:
            self.options["bench"] = fname
        if self.options["bench"] is not None and self.options["bench"] != "" and os.path.exists(self.options["bench"]):
            logger.log("\nReading testfile ...")
            if self.options["relative"]:
                os.chdir(os.path.dirname(os.path.abspath(self.options["bench"])))
                logger.log(f"Current Working Dir is: {os.getcwd()}")
                self.options["bench"] = os.path.basename(self.options["bench"])
            if self.options["arnold"]:
                self.runsuite = self.loadArnold()
            else:
                self.runsuite = self.loadPython()
            if self.runsuite is not None:
                self.runsuite.options["commands"] = self.options["commands"]
                self.runsuite.setAll(
                    state=TestState.InfoOnly if self.options["info"] else TestState.Waiting,
                    pipe=self.options["pipe"],
                    out=self.options["output"],
                    diff=self.options["diff"],
                    timeout=self.options["timeout"],
                    linesep=self.options["linesep"],
                    ignoreEmptyLines=self.options["ignoreEmptyLines"],
                )
                self.testCount = len(self.runsuite.testList)
                logger.log(f"I have loaded {self.testCount} Testcase{'s' if self.testCount > 0 else ''}")

            else:
                logger.log("Sorry, but I failed to load the requested suite")
        else:
            logger.log(f"Sorry, but I couldn't find the file '{self.options['bench']}'")
        logger.flush(self.options["quiet"])
        return self.runsuite

    # def start(self, finished=None, test=-1):
    #     """start the runner-thread"""
    #     self.finished = finished
    #     self.options['test'] = test
    #     Thread.start(self)

    def run(self):
        """Thread run function"""
        if self.options["length"]:
            print(len(self.runsuite.getTests()))
        elif len(self.options["save"]) == 1:
            logger.log(f"Saving Suite to {self.options['save'][0]}")
            self.saveToFile(self.options["save"][0])
        else:
            logger.flush(self.options["quiet"])
            self.runsuite.setMode(self.options["mode"])
            for test in self.runsuite.run(self.options["quiet"], tests=self.options["test"]):
                yield test
            self.runsuite.stats(self.options["quiet"])
        if self.finished is not None:
            self.finished()
        logger.flush(self.options["quiet"])

    def countTests(self):
        return len(self.runsuite.testList)

    def __str__(self):
        self.toString()

    def toString(self):
        s = self.options["suite"] + " = " + self.runsuite.toString()

    def saveToFile(self, fn: str):
        """
        Save the testsuite into a file
        """
        fHnd = open(fn, "w")
        fHnd.write("#!/usr/bin/env python\n\n")
        fHnd.write("# nightmare - Testbench\n")
        fHnd.write(f"# Saved at {time.strftime('%H:%M:%S')}\n")
        fHnd.write("# \n\n")
        # fHnd.write("# Author: {}\n")
        if self.options["dut"] is not None:
            fHnd.write("# Device Under Test\n")
            fHnd.write(f"DUT = \"{os.path.relpath(self.options['dut'])}\"\n\n")
        fHnd.write("# Test definitions\n")
        fHnd.write(f"{self.options['suite']} = [\n")
        tests = []
        for test in self.getSuite().getTests():
            tests.append(f"\t{test.toString()}")
        fHnd.write(",\n".join(tests))
        fHnd.write("\n]\n")
        fHnd.close()
