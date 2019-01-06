#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Since nightmare is a test tool, it should be possible to validate it's own
functionality, after a new version is build this test should run without
any errors. It should also show of the feature set of nightmare, and replace
the examples in the future.

The GUI is not part of this automated test, due to the difficulty
"""

DUT = "python -m nightmare"

if __name__ == "__main__":
    import sys

    if "sleep" in sys.argv:
        import time

        time.sleep(0.5)
    else:
        from .runner import TestRunner

        sys.argv = ["--no-gui", "--bench", "nightmare/validation.py", "--dut", DUT, "--suite", "validateThisNightmare", "-o"]
        runner = TestRunner()
        runner.parseArgv()
        suite = runner.loadSuite()
        if suite is not None:
            for testcase in runner.run():
                pass
else:
    successTests = [
        Test(
            name="stdout String",
            description="Test if the comparison for simple strings works correctly",
            command="echo this should be a success",
            stdout="this should be a success",
        ),
        Test(
            name="stdout Regular Expression",
            description="Test if the comparison with regular expressions works correctly",
            command="echo this should be a success",
            stdout=Regex("^this [a-z]+ [a-z ]+s.c*.s*$"),
        ),
        Test(
            name="stdout lambda",
            description="Test if the comparison with lambda functions works correctly",
            command="echo this should be a success",
            # The lambda function is written as a string constant, to be
            # displayed correctly. It will be evaluated by the testrunner.
            stdout='lambda s: s.rstrip().split(" ") == ["this","should","be","a","success"]',
        ),
        Test(
            name="stderr String",
            description="Test if the comparison for simple strings works correctly",
            command="echo this should be a success 1>&2",
            stderr="this should be a success",
        ),
        Test(
            name="stderr Regular Expression",
            description="Test if the comparison with regular expressions works correctly",
            command="echo this should be a success 1>&2",
            stderr=Regex("^this [a-z]+ [a-z ]+s.c*.s*$"),
        ),
        Test(
            name="stderr lambda",
            description="Test if the comparison with lambda functions works correctly",
            command="echo this should be a success 1>&2",
            stderr='lambda s: s.strip().split(" ") == ["this","should","be","a","success"]',
        ),
    ]

    failTests = [
        Test(
            name="stdout String",
            description="Test if the comparison for simple strings works correctly",
            command="echo this should be a fail",
            stdout="this should be a success",
        ),
        Test(
            name="stdout Regular Expression",
            description="Test if the comparison with regular expressions works correctly",
            command="echo this should be a fail",
            stdout="regex:^this [a-z]+ [a-z ]+s.c*.s*$",
        ),
        Test(
            name="stdout lambda",
            description="Test if the comparison with lambda functions works correctly",
            command="echo this should be a fail",
            stdout='lambda s: s.rstrip().split(" ") == ["this","should","be","a","success"]',
        ),
        Test(
            name="stderr String",
            description="Test if the comparison for simple strings works correctly",
            command="echo this should be a fail 1>&2",
            stderr="this should be a success",
        ),
        Test(
            name="stderr Regular Expression",
            description="Test if the comparison with regular expressions works correctly",
            command="echo this should be a fail 1>&2",
            stderr="regex:^this [a-z]+ [a-z ]+s.c*.s*$",
        ),
        Test(
            name="stderr lambda",
            description="Test if the comparison with lambda functions works correctly",
            command="echo this should be a fail 1>&2",
            stderr='lambda s: s.strip().split(" ") == ["this","should","be","a","success"]',
        ),
    ]

    timeoutTests = [
        Test(
            name="Timeout 01",
            description="This test should timeout due to insufficient time, also test local timeout",
            command="python nightmare/validation.py sleep",
            stdout="",
            timeout=0.1,
        ),
        Test(
            name="Timeout 02",
            description="This test should not timeout due to insufficient time, also test local timeout",
            command="python nightmare/validation.py sleep",
            stdout="",
            timeout=2.0,
        ),
    ]

    badwordTests = [
        BadWord(
            name="There should be a 'Test()' in one of the python files", path="nightmare/", pattern="*.py", words=["Test\("]
        ),
        BadWord(
            name="There should be a system call in the validation",
            path="nightmare/",
            pattern="validation.py",
            words=["system\("],
        ),
    ]

    # Ported over the old example tests
    suiteInstance = Suite(
        Test(name="Example 1", description="This test should be a success", command="$DUT success", stdout="success"),
        Test(name="Example 2", description="This test is doomed to fail", command="$DUT FAIL", stdout="failed"),
        Test(name="Example 3", description="This test will produce an error"),
        Test(name="Example 4", description="Lambda expression fail", command="$DUT Some more text", stdout=Contains("test")),
        Test(name="Example 5", description="Lambda expression success", command="$DUT Some more text", stdout=Contains("text")),
    )

    suiteWithOptions = Suite(
        Test(name="Example 1", description="This test should be a success", command="$DUT success", stdout="success"),
        Test(name="Example 2", description="This test is doomed to fail", command="$DUT FAIL", stdout="failed"),
        Test(name="Example 3", description="This test will produce an error"),
        Test(name="Example 4", description="Lambda expression fail", command="$DUT Some more text", stdout=Contains("test")),
        Test(name="Example 5", description="Lambda expression success", command="$DUT Some more text", stdout=Contains("text")),
        pipe=True,
        mode=Mode.Continuous,
    )

    suiteWithPython = Suite(
        *[
            Test(
                name="Python Test {:02}".format(nr),
                description="This test is autogenerated",
                command="$DUT Test{:02}".format(nr),
                stdout="Test{:02}".format(nr),
            )
            for nr in range(10)
        ],
        DUT="echo",
    )

    stringifierTests = [
        Test(
            name="Stringifier 01",
            description="This test splits the output into two lines, both match",
            command="echo ham&& echo eggs",
            stdout=Stringifier("ham\r\neggs"),
        ),
        Test(
            name="Stringifier 02",
            description="This test splits the output into two lines with a mismatch",
            command="echo spam&& echo eggs",
            stdout=Stringifier("ham\r\neggs\r\n"),
        ),
    ]

    continuationModeRegression = [
        Test(
            name="Continuation Mode Regression 01",
            description="This test should succeed",
            command="echo success",
            stdout="success",
        ),
        Test(
            name="Continuation Mode Regression 02",
            description="This test should succeed",
            command="echo fail",
            stdout="success",
        ),
        Test(
            name="Continuation Mode Regression 03",
            description="This test should succeed",
            command="echo fail",
            stdout="success",
        ),
        Test(
            name="Continuation Mode Regression 04",
            description="This test should succeed",
            command="echo success",
            stdout="success",
        ),
    ]

    regressionTests = [
        Test(
            name="Continuation Mode 01",
            description="Make sure the testsuite will halt on the first fail",
            command='$DUT --no-gui --bench nightmare/validation.py --dut "$DUT" --suite continuationModeRegression',
            stdout=Contains(f"I ran 2 out of 4 tests in total", f"Success: 1", f"Failed: 1"),
            returnCode=State.Fail.value,  # This reflects the state of the last test (failed)
        ),
        Test(
            name="Continuation Mode 02",
            description="Make sure the testsuite will run all test in continuation mode",
            command='$DUT --no-gui --bench nightmare/validation.py --dut "$DUT" --suite continuationModeRegression -c',
            stdout=Contains(f"I ran 4 out of 4 tests in total", f"Success: 2", f"Failed: 2"),
            returnCode=2,  # Continuation mode will return the number of failed tests: 2
        ),
    ]

    validateThisNightmare = [
        Test(
            name="CLI-01",
            description="All possible comparisons for success, dut from command line",
            command='$DUT --no-gui --bench nightmare/validation.py --dut "$DUT" --suite successTests',
            stdout=Contains(
                f"I ran {len(successTests)} out of {len(successTests)} tests in total", f"Success: {len(successTests)}"
            ),
            returnCode=0,
        ),
        Test(
            name="CLI-02",
            description="All possible comparisons for failure, dut from command line",
            command='$DUT --no-gui --bench nightmare/validation.py --dut "$DUT" --suite failTests -c',
            stdout=Contains(f"I ran {len(failTests)} out of {len(failTests)} tests in total", f"Failed: {len(failTests)}"),
            returnCode=NonZero(),
        ),
        Test(
            name="CLI-03",
            description="All possible comparisons for success, dut from testbench",
            command="$DUT --no-gui --bench nightmare/validation.py --suite successTests",
            stdout=Contains(
                f"I ran {len(successTests)} out of {len(successTests)} tests in total", f"Success: {len(successTests)}"
            ),
            returnCode=0,
        ),
        Test(
            name="CLI-04",
            description="All possible comparisons for failure, dut from testbench",
            command="$DUT --no-gui --bench nightmare/validation.py --suite failTests -c",
            stdout=Contains(f"I ran {len(failTests)} out of {len(failTests)} tests in total", f"Failed: {len(failTests)}"),
            returnCode=NonZero(),
        ),
        Test(
            name="CLI-05",
            description="Badword Tests",
            command="$DUT --no-gui --bench nightmare/validation.py --suite badwordTests -c",
            stdout=Contains(f"I ran {len(badwordTests)} out of {len(badwordTests)} tests in total", "BADWORD", "CLEAN"),
        ),
        Test(
            name="CLI-06",
            description="Timeout Tests",
            command="$DUT --no-gui --bench nightmare/validation.py --suite timeoutTests -c",
            stdout=Contains(
                f"I ran {len(timeoutTests)} out of {len(timeoutTests)} tests in total", "Timeouts: 1", "Success: 1"
            ),
        ),
        Test(
            name="CLI-07",
            description="Suite Instance",
            command="$DUT --no-gui --bench nightmare/validation.py --suite suiteInstance --dut echo -c",
            stdout=Contains(
                f"I ran {len(suiteInstance)} out of {len(suiteInstance)} tests in total", "Errors: 1", "Success: 2", "Failed: 2"
            ),
        ),
        Test(
            name="CLI-08",
            description="Suite Instance with Options",
            command="$DUT --no-gui --bench nightmare/validation.py --suite suiteWithOptions --dut echo",
            stdout=Contains(
                f"I ran {len(suiteWithOptions)} out of {len(suiteWithOptions)} tests in total",
                "Errors: 1",
                "Success: 2",
                "Failed: 2",
                "Some more text",
            ),
        ),
        Test(
            name="CLI-09",
            description="Suite Instance with python code",
            command="$DUT --no-gui --bench nightmare/validation.py --suite suiteWithPython -c",
            stdout=Contains(
                f"I ran {len(suiteWithPython)} out of {len(suiteWithPython)} tests in total", f"Success: {len(suiteWithPython)}"
            ),
        ),
        Test(
            name="CLI-10",
            description="Stringifier Tests",
            command="$DUT --no-gui --bench nightmare/validation.py --suite stringifierTests -c -u",
            stdout=Contains(
                f"I ran {len(stringifierTests)} out of {len(stringifierTests)} tests in total", "Success: 1", "-spam", "+ham"
            ),
        ),
        Test(
            name="CLI-11",
            description="Regression Tests",
            command="$DUT --no-gui --bench nightmare/validation.py --suite regressionTests -c -u",
            stdout=Contains(
                f"I ran {len(regressionTests)} out of {len(regressionTests)} tests in total", f"Success: {len(regressionTests)}"
            ),
        ),
    ]

