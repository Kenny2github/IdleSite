import argparse

choices = ['hi', 'hello', 'hey']

parser = argparse.ArgumentParser(description='Hello World!')
parser.add_argument('word', nargs='?', choices=choices,
                    help='The greeting word')

completion = "-W '%s'" % ' '.join(choices)

def main(args: list[str]):
    cmdargs = parser.parse_args(args[1:])
    print('Hello World!', (cmdargs.word or '').title())