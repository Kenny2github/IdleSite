import argparse
from .slot import SaveSlot

choices = ['hi', 'hello', 'hey']

parser = argparse.ArgumentParser(description='Hello World!')
parser.add_argument('word', nargs='?', choices=choices,
                    help='The greeting word')

completion = "-W '%s'" % ' '.join(choices)

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    print('Hello World!', (cmdargs.word or '').title())