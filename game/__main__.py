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

if not completion: # all this machinery needs to be ignored for --completion
    from game.i18n import i18n
    open('saves/.current', 'a').close() # create empty if not exists
    try:
        idx = sys.argv.index('--save-slot')
    except ValueError: # not specified at command line
        with open('saves/.current', 'r') as current:
            slot = current.read().strip()
        if not slot: # none currently selected
            slots = [name for name in os.listdir('saves')
                    if name not in {'README.md', '.current', '.lang'}]
            slot_count = len(slots)
            if slot_count == 0:
                slot = '1'
                print(i18n('no-save-slots', slot))
            elif slot_count == 1:
                slot = slots[0]
                print(i18n('one-save-slot', slot))
            else:
                print(i18n('many-save-slots'))
                print('\n'.join(slots))
                while slot not in slots:
                    slot = input(i18n('save-slot-prompt'))
            with open('saves/.current', 'w') as current:
                current.write(slot) # save current slot
    else: # specified at command line
        del sys.argv[idx] # pop --save-slot argument
        try:
            slot = sys.argv[idx] # argument value shifted left
            del sys.argv[idx] # pop argument value after reading
        except IndexError:
            sys.exit('--save-slot option requires an argument')

try:
    game = importlib.import_module('game.' + command)
    if completion:
        print(game.completion)
    else:
        game.main(sys.argv)
except (ImportError, AttributeError):
    sys.exit('invalid command %r' % command)
