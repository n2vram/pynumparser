#
# Fix the bug where "pytest" does not prepend PYTHONPATH with the current
# directory.
#
import os.path
import sys

_mydir = os.path.dirname(os.path.abspath(__file__))
_parent = os.path.dirname(_mydir)
sys.path.insert(0, _parent)
