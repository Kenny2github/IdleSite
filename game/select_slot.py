import argparse
from decimal import Decimal
import os
from . import save_slot
from .slot import SaveSlot
from .i18n import i18n, pi18n

parser = argparse.ArgumentParser(
    prog='select-slot', description=i18n('select-slot-desc'))
parser.add_argument('slot', help=i18n('select-slot-slot-opt'))
parser.add_argument(
    '-f', '--force-create', action='store_true', dest='force',
    help=i18n('select-slot-force-create-opt'))
parser.add_argument(
    '-I', '--non-interactive', action='store_false', dest='interactive',
    help=i18n('select-slot-non-interactive-opt'))

completion = "-o nosort -W '-f --force-create -I --non-interactive'"
no_load_slot = True

def main(args: list[str], slot: None = None) -> int:
    cmdargs = parser.parse_args(args[1:])
    slot = cmdargs.slot
    if not os.path.exists('saves/%s' % slot) and not cmdargs.force:
        if not cmdargs.interactive:
            return 1
        conf = input(i18n('select-slot-create-conf', slot))
        if conf[0].casefold() == 'y':
            pass
        else:
            return 1
    with open('saves/.current', 'w') as slotfile:
        slotfile.write(slot)
    return 0