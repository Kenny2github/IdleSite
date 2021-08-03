import sys
import os
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# not using argparse here because there's no good way to use
# argparse.REMAINDER *and* allow --completion and --save-slot
# to be specified after the command name

if len(sys.argv) < 2:
    sys.exit('game: error: cannot directly run '
             'the game module with no arguments')

del sys.argv[0]

command = sys.argv[0]
if '--completion' in sys.argv:
    completion = True
    sys.argv.remove('--completion')
else:
    completion = False

try:
    game = importlib.import_module('game.' + command.replace('-', '_'))
except ImportError:
    raise SystemExit('game: error: invalid command %r' % command) from None
else:
    if not (hasattr(game, 'completion') and hasattr(game, 'main')):
        sys.exit('game: error: invalid command %r' % command)
    if completion:
        print(game.completion)
    elif command.startswith('create'):
        # special behavior for "create site"
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
