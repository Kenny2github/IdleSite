import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game import import_game

# not using argparse here because there's no good way to use
# argparse.REMAINDER *and* allow --completion and --save-slot
# to be specified after the command name

if len(sys.argv) < 2:
    # untranslated: should not be encountered by regular users
    sys.exit('game: error: cannot directly run '
             'the game module with no arguments')

del sys.argv[0]

command = sys.argv[0]
completion = False
if '--completion' in sys.argv:
    completion = True
    sys.argv.remove('--completion')

try:
    game = import_game(command)
except ImportError:
    # untranslated: should not be encountered by regular users
    raise SystemExit('game: error: invalid command %r' % command) from None
else:
    if not (hasattr(game, 'completion') and hasattr(game, 'main')):
        # untranslated: should not be encountered by regular users
        sys.exit('game: error: invalid command %r' % command)
    if completion:
        print(game.completion)
    elif hasattr(game, 'no_load_slot'):
        # some commands need to not load save slots initially
        sys.exit(game.main(sys.argv) or 0)
    else:
        from game import get_slot, load_slot, save_slot
        slot_name = get_slot(sys.argv)
        slot = load_slot(slot_name)
        slot.update()
        try:
            sys.exit(game.main(sys.argv, slot) or 0)
        finally:
            save_slot(slot_name, slot)
