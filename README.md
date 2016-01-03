pynumparser
=============

Summary
-------
 
This library provides two classes for parsing simple integer or floating piont numbers and numeric sequences, optionally enforcing value limits. These can be used directly or as the **type** of an argument within an **argparse.ArgumentParser**.

- **NumberSequence** parses an input string and yields a sequence of numbers, optionally ensuring they are within the given limits.
- **Number** parses an input string and returns a single number; ensuring they are within the given limits.
- Both classes take a **numtype** parameter (**int** or **float**), and a **limits** parameter which can be *None* or a 2-tuple; the 2-tuple imposes limits on the parameters and the values returned.

Installation
------------
Install the **pynumparser** package using **pip**, eg:

     sudo pip install pynumparser

Or for a specific version:

     sudo python3 -m pip install pynumparser

*NumberSequence* Syntax
---------------------
Allowed inputs are comprised of subsequences separated by a comma (**,**).
Subsequences can be simple numbers, number ranges, or number ranges with a *stride* value.
- Simple number values yield a single value.
- A range is expressed as two (2) number values separated by a dash/hyphen (**-**).
  A range will yield multiple values (usually) **including both boundary values**.
  Numbers in the range differ by the optional *stride* value, which defaults to **1**.
  - The lower and upper range values are separated by a single dash/hyphen,except if the upper value is negative
    (eg: **"-5-**__-3"__).  The upper range value must be greater or equal to the lower range value.
  - The optional *stride* value is separated from the second range value with a forward slash (**/**).
- By default numbers are of **int** type, but if constructed with the parameter (_numtype=_**float**) the inputs are
  parsed as floating point numbers **with a _dot_ for a decimial point**, since the comma is used for subsequence separator.
- If the difference between the limits is not an even mulitiple of the *stride* value, then the second range will *not*
  be included in the result.
**Exceptions**:
- The constructor **limits** parameter must be either *None* or a 2-tuple; the tuple values must be *None* or a value of **numtype**, and:
  - If neither are *None*, then the **limits[0]** value must be less than the **limits[1]** value; or a ValueError is
    raised **by the constructor**.
  - If **limits[0]** not *None*, then if any value is less than **limits[0]** a ValueError is raised.
  - If **limits[1]** not *None*, then if any value is greater than **limits[1]** a ValueError is raised.
- If any input cannot be parsed as a valid number of given the **numtype** a ValueError is raised.
- If the second range value is less than the first range value (eg: **"8-5"**) a ValueError is raised.
- If any floating point number equates to positive or negative infinity (eg: **"1e9999"**) a ValueError is raised.
- Negative *stride* values are not currently allowed  (but please upvote the enhancement via GitHub if you need it).
- If the *stride* value is zero (0) a ValueError is raised, even if the upper and lower limit values are equal.
- When used within **argparse.ArgumentParser** strings that begin with a dash/hyphen values must be part of the flag
  argument.  For example:
    - This would give a parse error:  **foobar --arg -8-12 -N -5e8**
    - Whereas, this could be valid:   **foobar --arg=-8-12 -N-5e8**

If used within an **argparse.ArgumentParser**, the ValueError will result in a rather verbose error message indicating the specific problem, such as:

    $ test.py --days 1000
    usage: test.py [-h] [--age AGE] [--ints INTS] [--seconds SECONDS] [--days DAYS]
    test.py: error: argument --days: invalid FloatSequence (from 0 to 365.25), ERROR: "UPPER too large" value: '1000'

Example with *argparse.ArgumentParser*:
--------------------------------------
    import argparse
    import pynumparser

    # Note:  Typical values would likely include 'help' and  'default' parameters.
    parser = argparse.ArgumentParser(description="Number printer")

    # Add a simple int parameter, requiring it be between 0 and 130, inclusive:
    parser.add_argument('--age', type=pynumparser.Number(limits=(0,130)))
   
    # Add int sequence, requiring values be non-negative:
    parser.add_argument('--ints', type=pynumparser.NumberSequence(limits=(0, None)))
   
    # Add a simple float parameter, requiring it be a positive value less than 1000:
    parser.add_argument('--seconds', type=pynumparser.Number(numtype=float, limits=(1e-230,1000)))
   
    # Add a float sequence, requiring the numbers be between 0 and 365.25 inclusive:
    parser.add_argument('--days', type=pynumparser.NumberSequence(numtype=float, limits=(0,365.25)))

    print(parser.parse_args())

Examples Results:
-----------------
With the default parameters (_numtype=_**int**, _limits=None_):
- **"5"** yields a result of *(5)*.
- **"5-8"** is equivalent to **"5-8/1"** and either yields a result of *(5, 6, 7, 8)*.
- **"3-9/3"** would give a result of *(3, 6, 9)*.
- **"-3-2"** would yield a result of *(-3, -2, -1, 0, 1, 2)*.
- **"-3--2"** would yield a result of *(-3, -2)*.
- **"-5-5/5"** would yield a result of *(-5, 0, 5)*.
- **"-8,-9-9/6,12-30/12,5,2,3"** would yield *(-8, -9, -3, 3, 9, 12, 24, 5, 2, 3)*.

With parameters (_numtype=_**float**, _limits=None_) the results are floating point numbers:
- **"5.125"** yields a result of *(5.125)*.
- **"5,125"** yields a result of *(5.0, 125.0)* since the comma is a subsequence separator.
- **"5-7"** is equivalent to **"5-7/1"** and either yields a result of *(5.0, 6.0, 7.0)*.
- **"0-1/.25"** would give a result of *(0.0, 0.25, 0.5, 0.75, 1.0)*.
- Parsing of hyphens/dashes is the same for ints or floats.

Known Issues:
=============
1. Under some circumstances, floating point rounding error causes the upper range to be unexpectedly
   omitted.  This happens very rarely, but for example a FloatSequence result from **"0-13/1.3"** does
   not include the value **13** as expected, the results are:
   *(0.0, 1.3, 2.6, 3.9000000000000004, 5.2, 6.5, 7.8, 9.1, 10.4, 11.700000000000001)*.
2. Errors during **argparse.ArgumentParser** parsing are akwardly worded.  Improvement suggestions are welcome.

