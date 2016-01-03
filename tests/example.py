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
