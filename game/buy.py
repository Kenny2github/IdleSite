import argparse
from typing import Optional
from . import dynamic_completion
from .slot import Advertisement, Boost, CDNSetup, SaveSlot, Transaction
from .i18n import i18n

parser = argparse.ArgumentParser(prog='buy', description=i18n('buy-desc'))
clear = parser.add_mutually_exclusive_group()
clear.add_argument('-c', '--clear-after', type=int, default=5, metavar='days',
                   help=i18n('buy-clear-after-opt'))
clear.add_argument('-o', '--clear-on', type=int, default=None, metavar='day',
                   help=i18n('buy-clear-on-opt'))
parser.add_argument('-q', '--quote', action='store_true',
                   help=i18n('buy-quote-opt'))
subparsers = parser.add_subparsers(dest='cmd', required=True)

ads_parser = subparsers.add_parser(
    'advertisement', description=i18n('buy-advertisement-desc'))
expiry = ads_parser.add_mutually_exclusive_group()
expiry.add_argument('-e', '--expires', type=int, default=7, metavar='days',
                    help=i18n('buy-expires-opt'))
expiry.add_argument('-t', '--until', type=int, default=None, metavar='day',
                    help=i18n('buy-until-opt'))
power = ads_parser.add_mutually_exclusive_group()
power.add_argument('-p', '--power', type=int, default=100, metavar='power',
                   help=i18n('buy-power-opt'))
power.add_argument('-f', '--fraction', type=float, default=None, metavar='multiplier',
                   help=i18n('buy-fraction-opt'))

cdn_parser = subparsers.add_parser(
    'cdn', description=i18n('buy-cdn-desc'))
cdn_parser.add_argument('lat', type=int, metavar='latitude',
                        help=i18n('buy-lat-opt'))
cdn_parser.add_argument('long', type=int, metavar='longitude',
                        help=i18n('buy-long-opt'))

completion = "-o nosort -C 'buy complete'"

def complete_callback(subcmd: Optional[str], words: list[str]) -> list[str]:
    if subcmd is None:
        OPTS = '-c --clear-after -o --clear-on -q --quote'.split()
        if len(words) > 1 and words[-2] in OPTS[:-2]:
            return []
        opts = []
        if not (set(OPTS[:-2]) & set(words[:-1])):
            opts.extend(OPTS[:-2])
        if not (set(OPTS[-2:]) & set(words[:-1])):
            opts.extend(OPTS[-2:])
        return ['-h', '--help', 'advertisement', 'cdn'] + opts
    if subcmd == 'advertisement':
        OPTS = '-e --expires -t --until -p --power -f --fraction'.split()
        if words[-2] in OPTS:
            return []
        opts = []
        if not (set(OPTS[:4]) & set(words[:-1])):
            opts.extend(OPTS[:4])
        if not (set(OPTS[4:]) & set(words[:-1])):
            opts.extend(OPTS[4:])
        return opts
    if subcmd == 'cdn':
        return []
    return []

def advertisement(cmdargs: argparse.Namespace, slot: SaveSlot) -> Boost:
    if cmdargs.until is not None:
        expires = cmdargs.until
    else:
        expires = slot.today + cmdargs.expires
    if expires <= slot.today:
        ads_parser.error('expiry is on or before today')
    if cmdargs.fraction is not None:
        power = slot.views_today * cmdargs.fraction
    else:
        power = cmdargs.power
    if power <= 0:
        ads_parser.error('power is non-positive')
    return Advertisement(expires=expires, power=power)

def cdn(cmdargs: argparse.Namespace, slot: SaveSlot) -> CDNSetup:
    if not (-90 <= cmdargs.lat <= 90):
        cdn_parser.error('latitude out of range [-90, +90]')
    if not (-180 <= cmdargs.long <= 180):
        cdn_parser.error('longitude out of range [-180, +180]')
    return CDNSetup(cmdargs.lat, cmdargs.long)

def main(args: list[str], slot: SaveSlot):
    if 'complete' in args:
        dynamic_completion(['advertisement', 'cdn'], complete_callback)
    cmdargs = parser.parse_args(args[1:])
    if cmdargs.clear_on is not None:
        clear = cmdargs.clear_on
    else:
        clear = slot.today + cmdargs.clear_after
    action = globals()[cmdargs.cmd](cmdargs, slot)
    trans = Transaction(clear_date=clear, action=action)
    if cmdargs.quote:
        print(trans.description(slot))
    else:
        slot.transactions_pending.append(trans)
