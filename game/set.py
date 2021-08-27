import argparse
from decimal import Decimal
from .slot import SaveSlot
from .i18n import i18n

parser = argparse.ArgumentParser(prog='set', description=i18n('set-desc'))
subparsers = parser.add_subparsers(
    dest='cmd', required=True, title=i18n('subcommands'))

ads_parser = subparsers.add_parser(
    'ads', description=i18n('set-ads-desc'))
ads_parser.add_argument(
    'proportion', nargs='?', type=Decimal,
    help=i18n('set-ads-proportion-opt'))

difficulty_parser = subparsers.add_parser(
    'difficulty', description=i18n('set-difficulty-desc'))
difficulty_parser.add_argument(
    'multiplier', nargs='?', type=Decimal,
    help=i18n('set-difficulty-multiplier-opt'))

completion = "-o nosort -W '-h --help ads difficulty'"

def ads(cmdargs: argparse.Namespace, slot: SaveSlot):
    if cmdargs.proportion is None:
        print(slot.ad_proportion)
        return
    if not (0 <= cmdargs.proportion <= 1):
        ads_parser.error(i18n('error-proportion-oor'))
    slot.ad_proportion = cmdargs.proportion

def difficulty(cmdargs: argparse.Namespace, slot: SaveSlot):
    if cmdargs.multiplier is None:
        print(slot.difficulty_multiplier)
        return
    if cmdargs.multiplier <= 0:
        difficulty_parser.error(i18n('error-difficulty-oor'))
    slot.difficulty_multiplier = cmdargs.multiplier

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    return globals()[cmdargs.cmd](cmdargs, slot)