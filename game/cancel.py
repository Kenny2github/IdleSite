import argparse
from .slot import SaveSlot
from .i18n import i18n

TYPES = {
    'transaction': 'transactions_pending',
}

parser = argparse.ArgumentParser(
    prog='cancel', description=i18n('cancel-desc'))
parser.add_argument('type', choices=list(TYPES.keys()),
                    help=i18n('cancel-type-opt'))
parser.add_argument('indexes', nargs='+', type=int, metavar='index',
                    help=i18n('cancel-index-opt'))

completion = f"-o nosort -W '-h --help {' '.join(TYPES)}'"

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    attr = TYPES[cmdargs.type]
    # slot.<attr> = [<all items not matching indexes>]
    setattr(slot, attr, [
        v for i, v in enumerate(getattr(slot, attr), start=1)
        if i not in cmdargs.indexes])