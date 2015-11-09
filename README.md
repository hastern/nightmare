
NIGHTMARE
=========
Nightmare Is of Generous Help when Testing; May Arnold be Remembered Eternally

You must really, really love to test!

---

nightmare is a tool for automatic testing of non-interactive commandline
applications.

    usage: nightmare-2.0-py2.7.egg [-h] [--bench BENCH] [--suite SUITE]
                                   [--dut DUT] [--test TEST [TEST ...]]
                                   [--timeout TIMEOUT] [--arnold] [--save FILE]
                                   [--limit LIMIT] [--quiet] [--verbose]
                                   [--commands] [--length] [--info-only]
                                   [--pipe-streams] [--output-fails]
                                   [--unify-fails] [--no-color] [--continue]
                                   [--error] [--ignoreEmptyLines] [--relative]
                                   [--cr] [--ln] [--crln] [--gui] [--no-gui]
                                   [--version]

    A test tool for non-interactive commandline programms

    optional arguments:
      -h, --help            show this help message and exit
      --gui                 Use the GUI (experimental and unstable).
      --no-gui              Don't use the GUI.
      --version             Display version information

    Test selection:
      --bench BENCH         File which contains the testbench.
      --suite SUITE         Use testsuite SUITE from the testbench.
      --dut DUT, --DUT DUT  Set the device under test.
      --test TEST [TEST ...]
                            Run only the specified tests
      --timeout TIMEOUT     Set a global timeout for all tests.
      --arnold, -a          Use the arnold mode (requires pyparsing module)
      --save FILE           Save the testsuite as FILE

    Output Control:
      --limit LIMIT         Set a (soft) limit for a number of Bytes, after which
                            output piping will we stopped. Checks are made after
                            each line.
      --quiet, -q           Quiet mode. There will be no output except results.
      --verbose, -v         Verbose mode. The program gets chatty (default).
      --commands, -C        Show the command executed for each test.
      --length, -l          Print only the number of tests in the suite.
      --info-only, -i       Display only test information, but don't run them.
      --pipe-streams, -p    Redirect DUT output to their respective streams.
      --output-fails, -o    Redirect DUT output from failed tests to their
                            respective streams.
      --unify-fails, -u     Display the unified diff of output and expectation.
      --no-color            Don't use any colored output.

    Test Flow:
      --continue, -c        Continuous mode (Don't halt on failed tests).
      --error, -e           Same as '-c', but will halt if an error occurs.
      --ignoreEmptyLines, -L
                            Ignore empty lines
      --relative, -r        Use a path relative to the testbench path.
      --cr                  Force the line separation character (Mac OS).
      --ln                  Force the line separation character (Unix / Mac OS-X).
      --crln                Force the line separation character (Windows).


Additional to the commandline interface there is a GUI using the
wxPython. The GUI is limited in its capabilities compared to the CLI,
especially when it comes to testbench editing.

Be careful when you save your testbench! You might loose data, if it originates
from a handwritten testbench.


Testbench files
---------------

A collection of test is called a "testbench".
Inside a testbench there are a number of suites grouping tests together.

The testbench files a normal python files, which get evaluated by calling
the internal "`execfile`" function. This might not be the savest approach, but
it is definitly one of the easiest ones.

Here is a example for a minimal testbench.

    #!/usr/bin/env python

    # pyTest - Testsuite
    # Saved at 21:12:26
    #

    # Device Under Test
    DUT = "echo"

    # Test definitions
    suite = [
        Test (
            name = "Test 1",
            description = "A successfull run",
            command = "$DUT pyTest",
            stdout = "pyTest",
            returnCode = 0
        ),
        Test (
            name = "Test 2",
            description = "Testing output on stderr",
            command = "$DUT pyTest 1>&2",
            stderr = "pyTest"
        )
    ]

This example contains on testsuite name "suite" with two tests.
I hope the syntax is selfexplanatory.

The Pattern $DUT is a substitute for the application that gets tested.

Here's a list of all possible fields in a test definition:

- *name:* The (brief) name of the test.
- *description:* A longer description, about the purpose of this test.
- *command:* The command to be executed.
- *stdout:* The expected result on stdout.
- *stderr:* The expected result on stderr.
- *returnCode:* The expected returncode.
- *timeout:* Time in seconds before the process gets automatically killed.

Almost every field in the test is optional expect the command. The reason
should be obvious.

One reason for the testfiles to be real python script is the possibility to use
lambda functions for testing the output against an expectation.

The following example shows a test using a lambda function:

    Test (
        name "Lambda",
        description = "A test with lambda function",
        command = "echo Hello World",
        stdout = lambda x : x.find("o") > 0
    )

All expectation fields (stdout, stderr, returnCode) may contain lambda
a lambda expression.

In addition it is possible to use regular expression as expectation.
This is done by a simple `"regex:"`-prefix followed by the regular
expression.

The following example shows a test using a regular expression:

    Test (
        name "Regex",
        description = "A test with regular expression",
        command = "echo Hello World",
        stdout = "regex:^[a-zA-Z ]+$"
    )

In addition nightmare supports so called `Expecation`-objects as value
for *stdout* and *stderr*.
These classes must have a `__call__` method with a single argument,
which is the output of the corresponding stream.
The method should compare the output with the expectation and return
a boolean value.

Another special type are so called `Stringifier`-objects. They also must
implement a `__call__` method, but their result is a 2-tuple containing
2 lists of strings, that are passed onto nightmare's internal *diff*
(`-u`) tool.

There are three predefined Expectations/ Stringifiers:

- `ExpectFile(filename)`: compares the output byte-wise with a given
  file.

        Test (
            ...
            stdout = ExpectFile("output.txt")
        )

- `Stringifier(object)`: compares the output with the
  string-representation of the given object.

        # Assumption: there exists a class Image
        img = Image.read("image.png")

        Test (
            ...
            stdout = Stringifier(img)
        )

- `StringifiedFile(filename)`: loads the contents of a text-file for
  line by line comparison.

        Test (
            ...
            stdout = StringifiedFile("output.txt")
        )

History / Background
--------------------

The development started in 2012 at FH-Wedel as a addition / replacement to the
aging "[arnold](http://stud.fh-wedel.de/~arnold)"-tool, which is a tcl-script.
Since I'm a notorious windows user I was annoyed by the fact, that tcl/expect
barely works on windows. Being a fan of the python language I decided to
develop a new tool which fulfills the same requirements but by using a (in my
humble opinion) more modern language.

As part of my job at the FH Wedel it was successfully used as the primary
testing tool, to check if the implementation of the programming exercise meet
the required specifications.
Since "arnold" is an acronym, this tool's name needed to be equally ridiculous.
The name "*nightmare*" was given as a consequence, because most of the students
in the exercises absolutely hated the strictness of my tests.
