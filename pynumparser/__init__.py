#!/usr/bin/python
#
# Works with either Python v2.7+ or v3.3+
#
import math

"""
This module is designed for use with argparse to allow simple specification for
complex number sequences, and also provides a simple way to impose limits on
the numbers passed to the parser.

Example Usage:

    #!/usr/bin/env python
    import argparse
    import pynumrange
    import sys

    parser = argparse.ArgumentParser(description="pynumrange example")
    parser.add_argument('-n', '--numbers', help="A Sequence", default=[],
                        type=pynumrange.NumberSequence(int, limits=(0, 100))
    parser.add_argument('direct', nargs='*')
    opts = parser.parse_args()
    print("ArgumentParser: numbers = %s" % opts.numbers)

    ## Or just create a parser and call it directly:
    num_parser = pynumrange.NumberSequence(float, limits=(-1000, +1000))
    for number in opts.direct:
        num_range = num_parser(number)
        print('Direct from ("%s"): %s' % (number, num_range))
"""

class NumberSequence(object):
    """This class parses concise numeric patterns into a numeric
    sequence, intended to be used directly, or with
    argparse.ArgumentParser. Numeric patterns are of the form:

       SEQUENCE :=  SUBSEQ [ ',' SEQUENCE ]
       SUBSEQ   :=  LOWER [ '-' UPPER [ '/' SKIP ]]

    Where all terminals (LOWER, UPPER, SKIP) must be valid numbers.
    Example:   "1,5-7,20-30/5" would return: (1, 5, 6, 7, 20, 25, 30)
    Example:   "10-40/17,1-3"  would return: (10, 27, 34, 1, 2, 3)

    Note that for limits the value None is equivalent to (None, None)"""

    def __init__(self, numtype=int, limits=None, generator=False):
        self.numtype = numtype
        self.generator = generator
        if not numtype in (int, float):
            raise ValueError("NumberSequence: Invalid numeric type: " +
                             str(numtype))
        self.lowest, self.highest = limits or (None, None)
        self.error = None

    def __repr__(self):
        text = self.numtype.__name__.capitalize() + "Sequence"
        if None not in (self.lowest, self.highest):
            text += " (from %s to %s)" % (self.lowest, self.highest)
        elif self.lowest is not None:
            text += " (at least %s)" % self.lowest
        elif self.highest is not None:
            text += " (not over %s)" % self.highest
        if self.error:
            text += ', ERROR: "%s"' % self.error
        self.error = None
        return text

    @classmethod
    def _range(cls, lower, upper, delta):
        while lower <= upper:
            yield lower
            lower += delta

    def _error(self, tag, fmt, *args):
        self.error = tag
        raise ValueError("NumberSequence: " + (tag and tag + " ") +
                         (fmt.format(args) if args else fmt))

    def parse(self, text):
        """This returns a tuple of numbers."""
        return tuple(self.xparse(text))

    def xparse(self, text):
        """This is a generator for the numbers that 'parse()' returns.
        Use this (rather than 'parse()') in the same way you would use
        'xrange()' in lieu of 'range()'."""
        self.error = None
        for nss, subseq in enumerate(text.split(',')):
            step = None
            if not subseq:
                self._error("Empty subsequence", "Subsequence #{} is empty", nss)
            tag = "Subsequence \"{}\": ".format(subseq)
            if '/' in subseq:
                if '-' not in subseq[1:]:
                    self._error("Missing UPPER", tag + "STEP(\"{}\") w/o UPPER", step)
                lowup, step = subseq.split('/')
                try:
                    step = self.numtype(step)
                except Exception as exc:
                    self._error("Invalid STEP", tag + "Invalid STEP(\"{}\")", step)
                if step <= 0:
                    self._error("STEP must be positive", tag + "STEP must be positive (\"{}\")".format(step))
            else:
                lowup, step = subseq, 1

            # We must handle all of: ("-5", "2", "-3-5", "-3--1", "3-21")
            if '-' in lowup[1:]:
                ind = lowup.index('-', 1)
                try:
                    lower = lowup[:ind]
                    lower = self.numtype(lower)
                except ValueError:
                    self._error("Invalid LOWER", tag + "LOWER({}) is invalid".format(lower))
                try:
                    upper = lowup[ind + 1:]
                    upper = self.numtype(upper)
                except ValueError:
                    self._error("Invalid UPPER", tag + "UPPER({}) is invalid".format(upper))
                if upper < lower:
                    self._error("UPPER<LOWER", tag + "UPPER({}) is less than LOWER({})".format(upper, lower))
            else:
                try:
                    lower = upper = self.numtype(lowup)
                except ValueError:
                    self._error("Parse Error", "invalid {} value: '{}'".format(
                        self.numtype.__name__, lowup))
                    
            if any(map(math.isinf, (lower, upper, step))):
                self._error("Infinite Value", tag + "Numeric values cannot be infinite ({})".format(subseq))
            if self.lowest is not None and lower < self.lowest:
                self._error("LOWER too small", tag + "LOWER({}) cannot be less than ({})".format(lower, self.lowest))
            if self.highest is not None and upper > self.highest:
                self._error("UPPER too large", tag + "UPPER({}) cannot be greater than ({})".format(upper, self.highest))
            for num in self._range(lower, upper, step):
                yield num

    def __call__(self, text):
        if self.generator:
            return self.xparse(text)
        return self.parse(text)


class Number(object):
    """This class can be  used directly or with argparse.ArgumentParser,
    to parse numbers and enforce lower and/or upper limits on their values.

    Example:
      - Number(limits=(0,100))
            Would return an int value, which must be from 0 to 100, inclusive.
      - Number(limits=(5,None))
           Would return an int value, which must be no less than 5.
      - Number(numtype=float, limits=(-1000, 1000))
           Would return a float value, which must be from 0 to 100, inclusive.
    """
    def __init__(self, numtype=int, limits=None):
        if not numtype in (int, float):
            raise ValueError("Number: Invalid numeric type: " +
                             str(numtype))
        self.lowest, self.highest = limits or (None, None)
        self.numtype = numtype
        self.typename = {int:'Integer', float:'Float'}.get(self.numtype)
        self.error = None

    def __repr__(self):
        text = self.typename
        if None not in (self.lowest, self.highest):
            text += " (from %s to %s)" % (self.lowest, self.highest)
        elif self.lowest is not None:
            text += " (at least %s)" % self.lowest
        elif self.highest is not None:
            text += " (not over %s)" % self.highest
        if self.error:
            text += ', ERROR: "%s"' % self.error
        self.error = None
        return text

    def _error(self, tag, fmt, *args):
        self.error = tag
        raise ValueError("{}: {}{}".format(self.typename, (tag and tag + " "), fmt.format(args) if args else fmt))

    def parse(self, text):
        """This returns a tuple of numbers."""
        try:
            value = self.numtype(text)
        except ValueError:
            self._error("Parse Error", "invalid {} value: '{}'".format(self.typename, text))

        if math.isinf(value):
            self._error("Infinite Value", "Numeric values cannot be infinite ({})".format(text))
        if self.lowest is not None and value < self.lowest:
            self._error("Too Low", "Value ({}) must not be less than {}".format(value, self.lowest))
        if self.highest is not None and value > self.highest:
            self._error("Too High", "Value ({}) must not be higher than {}".format(value, self.highest))
        return value

    def __call__(self, text):
        return self.parse(text)

