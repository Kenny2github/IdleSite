import sys
import os
import importlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
except ImportError:
    sys.exit('invalid command %r' % command)

if completion:
    print(game.completion)
else:
    game.main(sys.argv)
