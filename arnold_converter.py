#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys

try:
    from pyparsing import *
    from pyTest import Test

    def syntax():
        ParserElement.setDefaultWhitespaceChars(" \t")
        LN = LineEnd().suppress()
        eqSym = Literal("=").suppress()
        lBrace, rBrace = Literal("{").suppress(), Literal("}").suppress()
        text = ZeroOrMore(Word(printables)) + LN
        enclosedText = lBrace + ZeroOrMore(CharsNotIn("}")) + rBrace
        testSym = CaselessKeyword("test")
        typeParam = Group(CaselessKeyword("type") + eqSym + text)
        nameParam = Group(CaselessKeyword("name") + eqSym + text)
        commentParam = Group(CaselessKeyword("comment") + eqSym + text)
        cmdParam = Group(CaselessKeyword("cmd") + enclosedText) + LN
        expectParam = Group(CaselessKeyword("expect") + ZeroOrMore(Literal("-i")).suppress() + enclosedText) + LN

        params = Group((nameParam & commentParam & typeParam & cmdParam & expectParam))
        testCase = Group(testSym + lBrace + LN + params + rBrace + LN) + ZeroOrMore(LN)

        testList = ZeroOrMore(testCase)
        # testList.ignore("#" + SkipTo("\n", include=True))
        return testList

    def buildTest(elem):
        attrs = {"name": "", "comment": "", "cmd": "", "expect": ""}
        for a in elem[1]:
            attrs[a[0]] = " ".join(a[1:])
        stdout = "regex:" + attrs["expect"]
        t = Test(name=attrs["name"], description=attrs["comment"], command=attrs["cmd"].replace("DUT", "$DUT"), stdout=stdout)
        return t

    def buildTestList(ast):
        return map(buildTest, ast)


except:
    syntax = None
    buildTest = None
    buildTestList = None
