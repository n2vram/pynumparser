# content of test_time.py

import pytest
import argparse
import collections
import sys

import pynumparser


def _perror(*args, **kwds):
    raise StopIteration("PARSER FAIL({}, {})".format(args, kwds))


def _happy_test(parse_args, name, token, expected):
    testname = 'pynumparser.Number({}).parse("{}")'.format(parse_args, token)

    # Test as a stand-alone parser:
    num_parser = pynumparser.Number(*parse_args)
    directly = num_parser.parse(token)
    assert directly == expected, "Direct result error"

    parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                     description="pynumrange test")
    parser.add_argument('--number', type=pynumparser.Number(*parse_args))
    parser.error = _perror
    try:
        parsed = parser.parse_args(['--number=' + token]).number
        assert parsed == expected, "ArgumentParser result error"
    except StopIteration as exc:
        assert False, "{} expected: {}\n{}".format(testname, expected, exc)


    # And validate the name:
    repr_name = repr(num_parser)
    assert repr_name == name, "Representation error."


def test_numsrange_happy():
    _happy_test((), "Integer", '1234',            1234)
    _happy_test((), "Integer", '-123',            -123)
    _happy_test((float,), "Float", '1.25e3',      1250.0)
    _happy_test((float,), "Float", '-125e-2',      -1.25)

    _happy_test((float,(0,3210)), "Float (from 0 to 3210)", '1253', 1253)
    _happy_test((float,(None,3210)), "Float (not over 3210)", '-1e9', -1e9)
    _happy_test((float,(123,None)), "Float (at least 123)", '123', 123)


def _failed_test(parse_args, name, token, expected, direxpected=None):
    testname = 'pynumparser.Number({}).parse("{}")'.format(parse_args, token)
    if direxpected is None:
        direxpected = expected
    with pytest.raises(ValueError) as exc:
        # Test as a stand-alone parser:
        num_parser = pynumparser.Number(*parse_args)
        directly = num_parser.parse(token)
    assert direxpected in exc.value.message, "ArgException did not match:\n\t{}\n\t{}".format(expected, exc.value.message)

    with pytest.raises(Exception) as exc:
        parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                         description="pynumrange test")
        parser.add_argument('--number', type=pynumparser.Number(*parse_args))
        parser.error = _perror
        parsed = parser.parse_args(['--number=' + token]).number
    if expected not in exc.value.message:
        raise exc.value
    assert expected in exc.value.message, "ArgException did not match:\n\t{}\n\t{}".format(expected, exc.value.message)

    # And validate the name:
    if name is not None:
        repr_name = repr(num_parser)
        assert repr_name == name, "Representation error."


def test_numsequence_throws():
    BADINT = "Integer: Parse Error invalid Integer value: '%s'"
    BADFLOAT = "Float: Parse Error invalid Float value: '%s'"

    _failed_test((bytes,), None, None, "Invalid numeric type")
    _failed_test((), 'Integer, ERROR: "Parse Error"', 'junk', "Parse Error")
    _failed_test((float,), 'Float, ERROR: "Parse Error"', 'junk', "Parse Error")

    _failed_test((), 'Integer, ERROR: "Parse Error"', '12.5', "Parse Error")
    _failed_test((float,), 'Float, ERROR: "Parse Error"', '12e', "Parse Error")
    _failed_test((float,), 'Float, ERROR: "Infinite Value"', '1e999',
                 'ERROR: "Infinite Value"', "values cannot be infinite")

    _failed_test((int,(10,20)), 'Integer (from 10 to 20), ERROR: "Too Low"', '5', "Too Low")
    _failed_test((int,(10,20)), 'Integer (from 10 to 20), ERROR: "Too High"', '30', "Too High")
    _failed_test((int,(10,None)), 'Integer (at least 10), ERROR: "Too Low"', '5', "Too Low")
    _failed_test((int,(None,20)), 'Integer (not over 20), ERROR: "Too High"', '30', "Too High")

    _failed_test((float,(10,20)), 'Float (from 10 to 20), ERROR: "Too Low"', '5', "Too Low")
    _failed_test((float,(10,20)), 'Float (from 10 to 20), ERROR: "Too High"', '30', "Too High")
    _failed_test((float,(10,None)), 'Float (at least 10), ERROR: "Too Low"', '5', "Too Low")
    _failed_test((float,(None,20)), 'Float (not over 20), ERROR: "Too High"', '30', "Too High")


