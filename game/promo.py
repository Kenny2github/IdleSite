import argparse
from .slot import Channels, Friends, SaveSlot
from .i18n import i18n

parser = argparse.ArgumentParser(prog='promo', description=i18n('promo-desc'))
subparsers = parser.add_subparsers(
    dest='cmd', required=True, title=i18n('subcommands'))

friends_parser = subparsers.add_parser(
    'friends', description=i18n('promo-friends-desc'))
friends_parser.add_argument(
    'count', nargs='?', type=int,
    help=i18n('promo-friends-count-opt'))

channels_parser = subparsers.add_parser(
    'channels', description=i18n('promo-channels-desc'))
channels_parser.add_argument(
    'count', nargs='?', type=int,
    help=i18n('promo-channels-count-opt'))

completion = "-o nosort -W '-h --help friends channels'"

def friends(cmdargs: argparse.Namespace, slot: SaveSlot):
    if cmdargs.count is None:
        print(f'{slot.friends_pinged}/{slot.friends_available}')
        return
    if cmdargs.count <= 0:
        friends_parser.error(i18n('error-count-oor'))
    if cmdargs.count > (slot.friends_available - slot.friends_pinged):
        friends_parser.error(i18n('error-not-enough-friends'))
    Friends(cmdargs.count).activate(slot)

def channels(cmdargs: argparse.Namespace, slot: SaveSlot):
    if cmdargs.count is None:
        print(f'{slot.promos_used}/{slot.promo_available}')
        return
    if cmdargs.count <= 0:
        channels_parser.error(i18n('error-count-oor'))
    if cmdargs.count > (slot.promo_available - slot.promos_used):
        channels_parser.error(i18n('error-not-enough-channels'))
    Channels(cmdargs.count).activate(slot)

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    return globals()[cmdargs.cmd](cmdargs, slot)