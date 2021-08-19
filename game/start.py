import argparse
from .i18n import i18n, pi18n

parser = argparse.ArgumentParser(prog='start', description=i18n('start-desc'))

completion = "-W ''"
no_load_slot = True

def main(args: list[str], slot: None = None):
    parser.parse_args(args[1:])
    pi18n('start')