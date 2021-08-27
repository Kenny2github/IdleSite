import argparse
from decimal import Decimal
import os
from . import save_slot
from .slot import SaveSlot
from .i18n import i18n, pi18n

parser = argparse.ArgumentParser(
    prog='create-site', description=i18n('create-site-desc'))
parser.add_argument(
    '-a', '--ad-proportion', type=Decimal, default=Decimal(),
    help=i18n('create-site-ad-proportion-opt'))
parser.add_argument(
    '-d', '--difficulty', type=Decimal, default=Decimal('1'),
    help=i18n('create-site-difficulty-opt'))
parser.add_argument(
    '-t', '--day-length', type=int, default=60*60*24,
    help=i18n('create-site-day-length-opt'))
parser.add_argument(
    '-s', '--save-slot', default=None, dest='slot',
    help=i18n('create-site-save-slot-opt'))
parser.add_argument(
    '-f', '--force-overwrite', action='store_true', dest='force',
    help=i18n('create-site-force-overwrite-opt'))
parser.add_argument(
    '-I', '--non-interactive', action='store_false', dest='interactive',
    help=i18n('create-site-non-interactive-opt'))

completion = "-o nosort -W '-a --ad-proportion -d --difficulty " \
    "-t --day-length -s --save-slot -f --force-overwrite -I --non-interactive'"
no_load_slot = True

def main(args: list[str], slot: None = None) -> int:
    cmdargs = parser.parse_args(args[1:])
    if not (0 <= cmdargs.ad_proportion <= 1):
        parser.error(i18n('error-proportion-oor'))
    if cmdargs.difficulty <= 0:
        parser.error(i18n('error-difficulty-oor'))
    if cmdargs.day_length <= 0:
        parser.error(i18n('error-day-length-oor'))
    slot = cmdargs.slot
    if not slot and not cmdargs.interactive:
        return 1
    while not slot:
        try:
            slot = input(i18n('save-slot-prompt'))
        except (KeyboardInterrupt, EOFError):
            return 1
    if os.path.exists('saves/%s' % slot) and not cmdargs.force:
        if not cmdargs.interactive:
            return 1
        conf = input(i18n('create-site-overwrite-conf', slot))
        if conf[0].casefold() == 'y':
            pass
        else:
            return 1
    data = SaveSlot(ad_proportion=cmdargs.ad_proportion,
                    difficulty_multiplier=cmdargs.difficulty,
                    day_length=cmdargs.day_length)
    save_slot(slot, data)
    if cmdargs.interactive:
        pi18n('create-site-site-created', slot,
            str(data.difficulty_multiplier), data.day_length)
    return 0