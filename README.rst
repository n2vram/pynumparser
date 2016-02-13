pynumparser
=============

Summary
-------

This library provides two classes for parsing simple integer or floating piont numbers and numeric
sequences, optionally enforcing value limits. These can be used directly or as the *type*
parameter of an argument within an *argparse.ArgumentParser*.

- **NumberSequence** parses an input string and yields a sequence of numbers, optionally ensuring
  they are within the given limits. It will also convert a sequence of numbers into the string form
  *[as of version 1.2]*.
- **Number** parses an input string and returns a single number; ensuring they are within the given
  limits.
- Both classes take a **numtype** parameter (*int* or *float*), and a **limits** parameter which
  can be *None* or a 2-tuple; the 2-tuple imposes limits on the parsed values.

Installation
------------
Install the package using **pip**, eg:

     sudo pip install pynumparser

Or for a specific version:

     sudo python3 -m pip install pynumparser

*NumberSequence* Syntax
-----------------------

Allowed inputs are comprised of one (1) or more subsequences separated by a comma (",").
Subsequences can be simple numbers or number ranges with or without a **stride** value.

- Simple number values yield a single value.

- A range is expressed as two (2) number values separated by either a dash/hyphen ("-") or a plus
  sign ("+") *[as of version 1.3]*, optionally followed by a slash ("/") and a **stride** value.

  - A range will usually yield multiple values *including both bounds*.  This is in contrast to
    the builtin Python *range()* behaviour.

    - A **lower bound** and **upper bound** may be separated by a single dash/hyphen ("-").  Note
      that it is legal for the upper bound be negative (eg: "-5--3").

    - A **lower bound** and **range size** may be separated by a single plus sign ("+").  Note that
      it is legal for the range size be start with a plus sign (eg: "8++5" is equivalent to "8+5").
      *[As of version 1.3]* 

  - Only monotonically increasing ranges are allowed:

    - The **stride** must be positive (eg: "5-8/0" is illegal).

    - An **upper range** value must not be less than the lower range value (eg: "5-4" is illegal).

    - A **range size** must not be negative (eg: "8+-4" is illegal) *[as of version 1.3]*.

- By default numbers are of *int* type. But if *numtype=float* is passed to the constructor, the
  inputs are parsed as floating point numbers *with a dot/peroid for a decimial mark*.  In other
  words, the representation of *5/4* must be "*1.2*" and not "*1,2*" since the comma is used as the
  subsequence separator.

- If the difference between the limits is not an even mulitiple of the *stride* value, then the
  second range will *not* be included in the result.

- The parser has a *contains* method, which can be used to for a number versus a text range
  *[as of version 1.1]*.

- **NumberSequence** has a classmethod *encode* that will convert a sequence into a simplified text
  representation.
  *[as of version 1.2]*.

  .. code:: python

      >>> import pynumparser
      >>> pynumparser.NumberSequence.encode([1, 2, 3, 7, 13, 19, 25])
      '1-3,7-25/6'
      >>> pynumparser.NumberSequence.encode([1.00, 1.25, 1.5, 1.75, 2, 2.25])
      '1.0-2.25/0.25'
      >>> pynumparser.NumberSequence.encode(range(10, 100, 5))
      '10-95/5'


**Exceptions**:
^^^^^^^^^^^^^^^

These apply to both the **NumberSequence** and **Number** classes:

- If the optional constructor **limits** parameter is provided, then a *ValueError* will be raised
  in the constructor if any of the following are violated.

  - The **limits** parameter must be either *None* or else a tuple with two (2) values, a *lower
    limit* then an *upper limit*.

  - Both of the *limit* values may be either *None* or a valid value of the **numtype**.

  - If *lower limit* and *upper limit* are numbers, then the *lower limit* must be less than the
    *upper limit*.

- If **limits** parameter was provided to the constructor, then a *ValueError* will be raised
  during parsing if any of the following are violated.

  - If the *lower limit* is a number, then parsed values must not be less than the *lower limit*.

  - If the *upper limit* is a number, then parsed values must not be greater than the *upper limit*.

- If any input cannot be parsed as a valid number of given the **numtype** a *ValueError* is raised.

- If any floating point number equates to positive or negative infinity (eg: *"1e9999"*) a
  *ValueError* is raised.

These apply only to the **NumberSequence** class, during parsing:

- If the *upper bound* is less than the *lower bound* (eg: "*8-5*") or *[as of version 1.3]* if the
  *range size* is negative (eg: "*8+-3*"), then a *ValueError* is raised.

- If the **stride** value is zero or negative, *ValueError* is raised, even if the upper and lower
  limit values are equal (eg: "*8-8/0*").


If used within an **argparse.ArgumentParser**, invalid input will raise a *ValueError* and result in
an error message indicating the specific problem, such as:

.. code:: bash

    $ demo.py --fnum 1e20
    usage: demo.py [-h] [-i ISEQ] [-f FSEQ] [-I INUM] [-F FNUM]
    demo.py: error: argument -F/--fnum: invalid Float (from -100 to 1000), ERROR: "Too High" value: '1e20'

    $ demo.py -i 200-100
    usage: demo.py [-h] [-i ISEQ] [-f FSEQ] [-I INUM] [-F FNUM]
    demo.py: error: argument -i/--iseq: invalid IntSequence (at least -1000), ERROR: "UPPER<LOWER" value: '200-100'

Note that a deficiency in the **argparse.ArgumentParser** package can cause problems with legal
values that start with a dash, even for flags with mandatory arguments.  Although not always true,
for some values (eg: "*-1e5*") the **argparser** package will incorrectly abort with an error
message of "*expected on argument*".

To demonstrate (using code from *Example* section saved as "demo.py") for a short flag with a valid
argument and a long flag with an invalid one:

.. code:: bash

    $ demo.py -f -1e2+2
    usage: demo.py [-h] [-i ISEQ] [-f FSEQ] [-I INUM] [-F FNUM]
    demo.py: error: argument -f/--fseq: expected one argument

    $ demo.py -f-1e2+2
    Namespace(fnum=[], fseq=(-100.0, -99.0, -98.0), inum=[], iseq=[])

.. code:: bash

    $ demo.py --fnum -1..5
    usage: demo.py [-h] [-i ISEQ] [-f FSEQ] [-I INUM] [-F FNUM]
    demo.py: error: argument -F/--fnum: expected one argument

    $ demo.py --fnum=-1..5
    usage: demo.py [-h] [-i ISEQ] [-f FSEQ] [-I INUM] [-F FNUM]
    demo.py: error: argument -F/--fnum: invalid Float (from -100 to 1000), ERROR: "Parse Error" value: '-1..5'


Example with *argparse.ArgumentParser*:
---------------------------------------

.. code::

    import argparse
    import pynumparser

    # Note:  Typical values would likely include 'help' and  'default' parameters.
    parser = argparse.ArgumentParser(description="Number printer")

    # Add a simple int parameter, requiring it be between -40 and 130, inclusive:
    parser.add_argument('-a', '--age', type=pynumparser.Number(limits=(-40, 130)))

    # Add int sequence, requiring values to be non-negative:
    parser.add_argument('-i', '--ints', type=pynumparser.NumberSequence(limits=(0, None)))

    # Add a simple float parameter, requiring it be a positive value less than 1000:
    parser.add_argument('-s', '--seconds', type=pynumparser.Number(numtype=float, limits=(1e-230, 1000)))

    # Add a float sequence, requiring the numbers be between 0 and 365.25 inclusive:
    parser.add_argument('-d', '--days', type=pynumparser.NumberSequence(numtype=float, limits=(0, 365.25)))

    print(parser.parse_args())

Examples *NumberSequence* Results:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
With the default parameters (*numtype=int, limits=None*):

- **"5"** yields a result of *(5)*.

- **"5-8"** is equivalent to **"5-8/1"** and both yield a result of *(5, 6, 7, 8)*.

- **"3-9/3"** would give a result of *(3, 6, 9)*.

- **"-3-2"** would yield a result of *(-3, -2, -1, 0, 1, 2)*.

- **"-3--2"** would yield a result of *(-3, -2)*.

- **"-5-5/5"** would yield a result of *(-5, 0, 5)*.

- **"-8,-9-9/6,12-30/12,5,2,3"** would yield *(-8, -9, -3, 3, 9, 12, 24, 5, 2, 3)*.

With parameters (*numtype=float*, *limits=None*) the results are floating point numbers:

- **"5.125"** yields a result of *(5.125)*.

- **"5,125"** yields a result of *(5.0, 125.0)* since the comma is a subsequence separator.

- **"5-7"** is equivalent to **"5-7/1"** and both yield a result of *(5.0, 6.0, 7.0)*.

- **"0-1/.25"** would give a result of *(0.0, 0.25, 0.5, 0.75, 1.0)*.


Releases:
^^^^^^^^^
   +-------------+----------------------------------------------------------------------------+
   | **Version** | **Description**                                                            |
   +-------------+----------------------------------------------------------------------------+
   |    1.0.1    | Initial release                                                            |
   +-------------+----------------------------------------------------------------------------+
   |     1.1     | Added the **NumberSequence.contains()** method.                            |
   +-------------+----------------------------------------------------------------------------+
   |   1.2.0.0   | Added the **NumberSequence.encode()** method, fixed documentation on PyPi. |
   +-------------+----------------------------------------------------------------------------+
   |     1.3     | Added the **NumberSequence** format "+" to specify a *range size*.         |
   +-------------+----------------------------------------------------------------------------+


Known Issues:
^^^^^^^^^^^^^

- Under some circumstances, floating point representation errors cause the upper range to be
  (unexpectedly) omitted.  This happens due to the internal representation of floating point
  numbers, and is not limited to this package, or even to Python.  For more information, see:
  `Floating Point Arithmetic: Issues and Limitations
  <https://docs.python.org/2/tutorial/floatingpoint.html#representation-error>`_.

  - In the first example (**"0-13/1.3"**), the value of **13** is not included since the previous
    value was larger than **11.7**.
  - In the second example (**"1.2-2.0/0.2"**) the final value is slightly less than
    **2.0** due to representation error.

  .. code:: python

      >>> import pynumparser
      >>> parser = pynumparser.NumberSequence(float)
      >>> parser.parse("0-13/1.3")
      (0.0, 1.3, 2.6, 3.9000000000000004, 5.2, 6.5, 7.8, 9.1, 10.4, 11.700000000000001)
      >>> parser.parse("1.2-2.0/0.2")
      (1.2, 1.4, 1.5999999999999999, 1.7999999999999998, 1.9999999999999998)
