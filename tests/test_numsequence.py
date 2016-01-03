# content of test_time.py

import argparse
import collections
import pytest
import sys
import types

import pynumparser
 

def _perror(*args, **kwds):
    raise StopIteration("PARSER FAIL({}, {})".format(args, kwds))


def _happy_test(parse_args, name, token, expected):
    testname = 'pynumparser.NumberSequence({}).parse("{}")'.format(parse_args, token)
    expected = tuple(expected)
    # Test as a stand-alone parser:
    num_parser = pynumparser.NumberSequence(*parse_args)
    directly = num_parser.parse(token)
    assert directly == expected, "Direct result error"

    parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                     description="pynumrange test")
    parser.add_argument('--number', type=pynumparser.NumberSequence(*parse_args))
    parser.error = _perror
    try:
        parsed = parser.parse_args(['--number=' + token]).number
        assert parsed == expected, "ArgumentParser result error"
    except StopIteration as exc:
        assert False, "{} expected: {}\n{}".format(testname, expected, exc)

    # And validate the name:
    repr_name = repr(num_parser)
    assert repr_name == name, "Representation error."


def _failed_test(parse_args, name, token, expected, direxpected=None):
    testname = 'pynumparser.NumberSequence({}).parse("{}")'.format(parse_args, token)
    if direxpected is None:
        direxpected = expected
    with pytest.raises(ValueError) as exc_info:
        # Test as a stand-alone parser:
        num_parser = pynumparser.NumberSequence(*parse_args)
        directly = num_parser.parse(token)
    print("Dir.Exp: " + str(expected))
    print("Dir.Got: " + str(exc_info.value))
    assert direxpected in str(exc_info.value), "DirException did not match:\n\t{}\n\t{}".format(expected, str(exc_info.value))

    with pytest.raises(Exception) as exc_info:
        parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                         description="pynumrange test")
        parser.add_argument('--number', type=pynumparser.NumberSequence(*parse_args))
        parser.error = _perror
        parsed = parser.parse_args(['--number=' + token]).number
    print("Arg.Exp: " + str(expected))
    print("Arg.Got: " + str(exc_info.value))
    assert expected in str(exc_info.value), "ArgException did not match:\n\t{}\n\t{}".format(expected, str(exc_info.value))

    # And validate the name:
    if name is not None:
        repr_name = repr(num_parser)
        print("Rep.Exp: " + name)
        print("Rep.Got: " + repr_name)
        assert repr_name == name, "Representation error."


def test_happy():
    _happy_test((), "IntSequence", '1234',            (1234,))
    _happy_test((), "IntSequence", '-123',            (-123,))
    _happy_test((), "IntSequence", '+123',            (+123,))
    _happy_test((), "IntSequence", '12-20',           range(12,21))
    _happy_test((), "IntSequence", '1,3,7',           (1,3,7))
    _happy_test((), "IntSequence", '1-3,7',           (1,2,3,7))
    _happy_test((), "IntSequence", '1-3,7-9',         (1,2,3,7,8,9))
    _happy_test((), "IntSequence", '1-8/3,7-9',       (1,4,7,7,8,9))
    _happy_test((), "IntSequence", '12-20',           range(12,21))
    _happy_test((), "IntSequence", '12-20/4',         range(12,21,4))
    _happy_test((), "IntSequence", '7-11,5-8',        list(range(7,12)) + list(range(5,9)))
    _happy_test((), "IntSequence", '-2-2',            range(-2,3))
    _happy_test((), "IntSequence", '-4--2',           range(-4,-1))
    _happy_test((float,(0,3210)), "FloatSequence (from 0 to 3210)",
                '0-21/3.5', (0.0, 3.5, 7.0, 10.5, 14.0, 17.5, 21.0))
    _happy_test((float,(0,3210)), "FloatSequence (from 0 to 3210)",
                '0-21/3.5,3e2-3.1e2/5',
                (0.0, 3.5, 7.0, 10.5, 14.0, 17.5, 21.0, 300.0, 305.0, 310.0))
    _happy_test((float,(0,None)), "FloatSequence (at least 0)", '0-21/8',
                (0.0, 8.0, 16.0))
    _happy_test((float,(None,20)), "FloatSequence (not over 20)", '0-20/8',
                (0.0, 8.0, 16.0))


def test_throws():
    BADINT = "invalid literal for int() with base 10: '%s'"
    BADFLOAT = "could not convert string to float: %s"    

    _failed_test((bytes,), None, None, "Invalid numeric type")
    _failed_test((), 'IntSequence, ERROR: "Parse Error"', 'junk',
                 'IntSequence, ERROR: "Parse Error"', "invalid int value: 'junk'")
    _failed_test((float,), 'FloatSequence, ERROR: "Parse Error"', 'junk',
                 'FloatSequence, ERROR: "Parse Error"', "invalid float value: 'junk'")
    _failed_test((), 'IntSequence, ERROR: "Invalid STEP"', '-123--5/zz', "Invalid STEP")
    _failed_test((), 'IntSequence, ERROR: "Invalid UPPER"', '5-zz', "Invalid UPPER")
    _failed_test((), 'IntSequence, ERROR: "Invalid LOWER"', 'zz-5', "Invalid LOWER")
    _failed_test((), 'IntSequence, ERROR: "Empty subsequence"', '1-2,,8-9', "Empty subsequence")
    _failed_test((), 'IntSequence, ERROR: "Missing UPPER"', '1/8', "Missing UPPER")

    _failed_test((), 'IntSequence, ERROR: "STEP must be positive"', '1-8/-8', "STEP must be positive")
    _failed_test((), 'IntSequence, ERROR: "STEP must be positive"', '1-8/0', "STEP must be positive")
    _failed_test((), 'IntSequence, ERROR: "UPPER<LOWER"', '8-1', "UPPER<LOWER")

    _failed_test((float,), 'FloatSequence, ERROR: "Infinite Value"', '1e999',
                 'ERROR: "Infinite Value"', "values cannot be infinite")
    _failed_test((int,(4,8)), 'IntSequence (from 4 to 8), ERROR: "LOWER too small"', '1-8',
                 'ERROR: "LOWER too small"', "LOWER too small")
    _failed_test((int,(4,8)), 'IntSequence (from 4 to 8), ERROR: "UPPER too large"', '5-9',
                 'ERROR: "UPPER too large"', "UPPER too large")


def _test_generator(parse_args, name, token, expected):
    # Test as a stand-alone parser:
    num_parser = pynumparser.NumberSequence(*parse_args)
    directly = num_parser.xparse(token)
    assert isinstance(directly, types.GeneratorType), "Not a Generator: " + str(directly)
    assert tuple(directly) == tuple(expected), "Direct result error"

    parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                     description="pynumrange test")
    parser.add_argument('--number', type=pynumparser.NumberSequence(*parse_args))
    parser.error = _perror
    try:
        parsed = parser.parse_args(['--number=' + token]).number
        assert isinstance(parsed, types.GeneratorType), "Not a Generator: " + str(parsed)
        assert tuple(parsed) == tuple(expected), "Direct result error"
    except StopIteration as exc:
        assert False, "{} expected: {}\n{}".format(testname, expected, exc)

    # And validate the name:
    repr_name = repr(num_parser)
    assert repr_name == name, "Representation error."

def test_generator():
    _test_generator((int,None,True), 'IntSequence', '1-5', (1, 2, 3, 4, 5))
    _test_generator((float,None,True), 'FloatSequence', '20-40/5', tuple(map(float, range(20, 45, 5))))
