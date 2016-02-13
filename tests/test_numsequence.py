# content of test_time.py

import argparse
import pytest
import types

import pynumparser


def _perror(*args, **kwds):
    raise StopIteration("PARSER FAIL({}, {})".format(args, kwds))


def _frange(lower, upper, step=1.0):
    while lower < upper:
        yield lower
        lower += step


def _happy_test(parse_args, name, token, expected):
    testname = 'pynumparser.NumberSequence({}).parse("{}")'.format(
        parse_args, token)
    expected = tuple(expected)
    # Test as a stand-alone parser:
    num_parser = pynumparser.NumberSequence(*parse_args)
    directly = num_parser.parse(token)
    assert directly == expected, "Direct result error for: " + token

    parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                     description="pynumrange test")
    parser.add_argument('--number',
                        type=pynumparser.NumberSequence(*parse_args))
    parser.error = _perror
    try:
        parsed = parser.parse_args(['--number=' + token]).number
        assert parsed == expected, "ArgumentParser result error for: " + token
    except StopIteration as exc:
        assert False, "{} expected: {}\n{}".format(testname, expected, exc)

    # And validate the name:
    repr_name = repr(num_parser)
    assert repr_name == name, "Representation error."


def _failed_test(parse_args, name, token, expected, direxpected=None):
    if direxpected is None:
        direxpected = expected
    with pytest.raises(ValueError) as exc_info:
        # Test as a stand-alone parser:
        num_parser = pynumparser.NumberSequence(*parse_args)
        directly = num_parser.parse(token)
        print("{}.parse({}) returned: {}".format(num_parser, token, directly))
    print("Dir.Exp: " + str(expected))
    print("Dir.Got: " + str(exc_info.value))
    assert direxpected in str(exc_info.value), "DirException did not match" \
        ":\n\t{}\n\t{}".format(expected, str(exc_info.value))

    with pytest.raises(Exception) as exc_info:
        parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                         description="pynumrange test")
        num_parser = pynumparser.NumberSequence(*parse_args)
        parser.add_argument('--number', type=num_parser)
        parser.error = _perror
        parsed = parser.parse_args(['--number=' + token]).number
        print("{}.parse({}) returned: {}".format(num_parser, token, parsed))

    print("Arg.Exp: " + str(expected))
    print("Arg.Got: " + str(exc_info.value))
    assert expected in str(exc_info.value), "ArgException did not match" \
        ":\n\t{}\n\t{}".format(expected, str(exc_info.value))

    # And validate the name:
    if name is not None:
        repr_name = repr(num_parser)
        print("Rep.Exp: " + name)
        print("Rep.Got: " + repr_name)
        assert repr_name == name, "Representation error."


def test_happy():
    _happy_test((), "IntSequence", '1234', (1234,))
    _happy_test((), "IntSequence", '-123', (-123,))
    _happy_test((), "IntSequence", '+123', (+123,))
    _happy_test((), "IntSequence", '12-20', range(12, 21))
    _happy_test((), "IntSequence", '1,3,7', (1, 3, 7))
    _happy_test((), "IntSequence", '1-3,7', (1, 2, 3, 7))
    _happy_test((), "IntSequence", '1-3,7-9', (1, 2, 3, 7, 8, 9))
    _happy_test((), "IntSequence", '1-8/3,7-9', (1, 4, 7, 7, 8, 9))
    _happy_test((), "IntSequence", '12-20', range(12, 21))
    _happy_test((), "IntSequence", '12-20/4', range(12, 21, 4))
    _happy_test((), "IntSequence", '7-11,5-8',
                list(range(7, 12)) + list(range(5, 9)))
    _happy_test((), "IntSequence", '-2-2', range(-2, 3))
    _happy_test((), "IntSequence", '-4--2', range(-4, -1))
    _happy_test((), "IntSequence", '+8-+12', range(8, 13))
    _happy_test((), "IntSequence", '12+8', range(12, 21))
    _happy_test((), "IntSequence", '8+22/5', range(8, 31, 5))

    _happy_test((float, ), "FloatSequence", '105+10/5', (105.0, 110.0, 115.0))
    _happy_test((float, (0, 3210)), "FloatSequence (from 0 to 3210)",
                '0-21/3.5', (0.0, 3.5, 7.0, 10.5, 14.0, 17.5, 21.0))
    _happy_test((float, (0, 3210)), "FloatSequence (from 0 to 3210)",
                '0-21/3.5,3e2-3.1e2/5',
                (0.0, 3.5, 7.0, 10.5, 14.0, 17.5, 21.0, 300.0, 305.0, 310.0))
    _happy_test((float, (0, None)), "FloatSequence (at least 0)", '0-21/8',
                (0.0, 8.0, 16.0))
    _happy_test((float, (None, 20)), "FloatSequence (not over 20)", '0-20/8',
                (0.0, 8.0, 16.0))

    # This is hideous, but actually parses correctly:
    _happy_test((float, ), "FloatSequence", '-1.8e-1--1.3e-1/0.1e-1',
                _frange(-1.8e-1, -1.31e-1, 0.1e-1))


def test_sequence_throws():
    _failed_test((bytes,), None, None, "Invalid numeric type")
    _failed_test((), 'IntSequence, ERROR: "Parse Error"', 'junk',
                 'IntSequence, ERROR: "Parse Error"',
                 "invalid int value: 'junk'")
    _failed_test((float,), 'FloatSequence, ERROR: "Parse Error"', 'junk',
                 'FloatSequence, ERROR: "Parse Error"',
                 "invalid float value: 'junk'")
    _failed_test((), 'IntSequence, ERROR: "Invalid STEP"', '-123--5/zz',
                 "Invalid STEP")
    _failed_test((), 'IntSequence, ERROR: "Invalid UPPER"', '5-3zz',
                 "Invalid UPPER")
    _failed_test((), 'IntSequence, ERROR: "Invalid LOWER"', 'zz-5',
                 "Invalid LOWER")
    _failed_test((), 'IntSequence, ERROR: "Empty subsequence"', '1-2,,8-9',
                 "Empty subsequence")
    _failed_test((), 'IntSequence, ERROR: "Missing UPPER"', '1/8',
                 "Missing UPPER")

    _failed_test((), 'IntSequence, ERROR: "STEP must be positive"', '1-8/-8',
                 "STEP must be positive")
    _failed_test((), 'IntSequence, ERROR: "STEP must be positive"', '1-8/0',
                 "STEP must be positive")
    _failed_test((), 'IntSequence, ERROR: "UPPER<LOWER"', '8-1', "UPPER<LOWER")
    _failed_test((), 'IntSequence, ERROR: "UPPER<LOWER"', '8+-1', "UPPER<LOWER")

    _failed_test((float,), 'FloatSequence, ERROR: "Infinite Value"', '1e999',
                 'ERROR: "Infinite Value"', "values cannot be infinite")
    _failed_test((int, (4, 8)),
                 'IntSequence (from 4 to 8), ERROR: "LOWER too small"', '1-8',
                 'ERROR: "LOWER too small"', "LOWER too small")
    _failed_test((int, (4, 8)),
                 'IntSequence (from 4 to 8), ERROR: "UPPER too large"', '5-9',
                 'ERROR: "UPPER too large"', "UPPER too large")


def _test_generator(parse_args, name, token, expected):
    # Test as a stand-alone parser:
    num_parser = pynumparser.NumberSequence(*parse_args)
    directly = num_parser.xparse(token)
    assert isinstance(directly, types.GeneratorType), "Not a Generator: " + \
        str(directly)
    assert tuple(directly) == tuple(expected), "Direct result error for: " + token

    parser = argparse.ArgumentParser(prog=('Test({})'.format(parse_args)),
                                     description="pynumrange test")
    num_parser = pynumparser.NumberSequence(*parse_args)
    parser.add_argument('--number', type=num_parser)
    parser.error = _perror
    try:
        parsed = parser.parse_args(['--number=' + token]).number
        assert isinstance(parsed, types.GeneratorType), "Not a Generator: " + \
            str(parsed)
        assert tuple(parsed) == tuple(expected), "Direct result error for: " + token
    except StopIteration as exc:
        assert False, "{} expected: {}\n{}".format(num_parser, expected, exc)

    # And validate the name:
    repr_name = repr(num_parser)
    assert repr_name == name, "Representation error."


def test_generator():
    _test_generator((int, None, True), 'IntSequence', '1-5', (1, 2, 3, 4, 5))
    _test_generator((float, None, True), 'FloatSequence', '20-40/5',
                    tuple(map(float, range(20, 45, 5))))


def _contains(args, token, has, hasnot):
    # Test as a stand-alone parser:
    parser = pynumparser.NumberSequence(*args)
    for element in has:
        contains = parser.contains(token, element)
        message = "NumberSequence({}).contains(\"{}\", {}) should be " + \
                  "True".format(args, token, element)
        assert contains is True, message

    expect = tuple(True for e in has)
    result = parser.contains(token, has)
    message = "NumberSequence({}).contains(\"{}\", {}) should all be " + \
              "True".format(args, token, has)
    assert result == expect, message

    for element in hasnot:
        contains = parser.contains(token, element)
        message = "NumberSequence({}).contains(\"{}\", {}) should be " + \
                  "False".format(args, token, element)
        assert not contains, message
    expect = tuple(False for e in hasnot)
    result = parser.contains(token, hasnot)
    message = "NumberSequence({}).contains(\"{}\", {}) should all be " + \
              "False".format(args, token, hasnot)
    assert result == expect, message


def test_contains():
    _contains((int,), "1,5,8", (1, 5, 8), (0, 3, 4, 7, 9))
    _contains((int,), "10-100000", (10, 100000), (1, 9, 100001))
    _contains((int,), "10-100000/5",
              (10, 15, 20, 99990, 99995, 100000, 55555),
              (5, 11, 99999, 55556))
    _contains((float,), "-1e3-1e3/1e2,100-120",
              (-500, -100, 0, 100, 500), (-999, None, 0.1, 1001))

    # Test rounding to at the 5th digit, above and below.
    FAIL_SMALL = 0.99998999
    OKAY_SMALL = 0.99999000
    OKAY_LARGE = 1.00000999
    FAIL_LARGE = 1.00001001
    _contains((float,), "0-13.0/0.13",
              (0.13, 2.6, 3.90, 0.13 * (5 + OKAY_SMALL),
               0.13 * (5 + OKAY_LARGE)),
              (-1.301e-6, 15.3, 0.13 * (5 + FAIL_SMALL),
               0.13 * (5 + FAIL_LARGE)))


def _encode(_type, string, series=None):
    # Convert from string to a sequence, then make sure we get it back.
    parser = pynumparser.NumberSequence(_type)
    if series is None:
        series = parser.parse(string)
    result = parser.encode(series)
    assert result == string, "Failed in round-trip for: " + string


# Test the encode function.
def test_encode():
    _encode(int, "", [])
    _encode(int, "1,5,8")
    _encode(int, "1-8,10-12")
    _encode(int, "1-100")
    _encode(int, "1,3-8,100,4,5,8-11,13")
    _encode(int, "1,3-5,7-16/3,9")
    _encode(int, "1-5,8-20/4")
    _encode(int, "-20--5/5,-12-3,1000000-1000300")

    _encode(float, "", [])
    _encode(float, "1.25-11.25/2.5")
    _encode(float, "-51.25--11.25/5.0,1000.0-1001.0/0.0625")
    _encode(float, "0.125-0.25/0.0078125")


# NOTE: We skip testing that .contains() raises the validity exceptions
# that .parse() raises, relying on the fact that they share the same
# parsing engine.
