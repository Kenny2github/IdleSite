import sys
import os
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# not using argparse here because there's no good way to use
# argparse.REMAINDER *and* allow --completion and --save-slot
# to be specified after the command name

if len(sys.argv) < 2:
    sys.exit('%s: error: cannot directly run '
             'the game module with no arguments' % sys.argv[0])

del sys.argv[0]

command = sys.argv[0]
if '--completion' in sys.argv:
    completion = True
    sys.argv.remove('--completion')
else:
    completion = False

try:
    game = importlib.import_module('game.' + command)
    if completion:
        print(game.completion)
    else:
        from game import get_slot, load_slot
        slot = load_slot(get_slot(sys.argv))
        slot.update()
        game.main(sys.argv, slot)
except (ImportError, AttributeError):
    sys.exit('invalid command %r' % command)
