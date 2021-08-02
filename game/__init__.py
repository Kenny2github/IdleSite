import sys
import os
import json
from .i18n import i18n, pi18n
from .slot import SaveSlot, _JL

def get_slot(argv: list[str]) -> str:
    open('saves/.current', 'a').close() # create empty if not exists
    try:
        idx = argv.index('--save-slot')
    except ValueError: # not specified at command line
        with open('saves/.current', 'r') as current:
            slot = current.read().strip()
        if not slot: # none currently selected
            slots = [name for name in os.listdir('saves')
                    if name not in {'README.md', '.current', '.lang'}]
            slot_count = len(slots)
            if slot_count == 0:
                slot = '1'
                pi18n('no-save-slots', slot)
            elif slot_count == 1:
                slot = slots[0]
                pi18n('one-save-slot', slot)
            else:
                pi18n('many-save-slots')
                print('\n'.join(slots))
                while slot not in slots:
                    slot = input(i18n('save-slot-prompt'))
            with open('saves/.current', 'w') as current:
                current.write(slot) # save current slot
    else: # specified at command line
        del argv[idx] # pop --save-slot argument
        try:
            slot = argv[idx] # argument value shifted left
            del argv[idx] # pop argument value after reading
        except IndexError:
            sys.exit('--save-slot option requires an argument')
    return slot

def load_slot(slot: str) -> SaveSlot:
    open('saves/%s' % slot, 'a').close()
    with open('saves/%s' % slot, 'r') as slotfile:
        data = slotfile.read()
    if not data:
        pi18n('creating-slot', slot)
        data = SaveSlot()
        save_slot(slot, data)
    else:
        data = json.loads(data, object_hook=_JL.unserialize)
    return data

def save_slot(slot: str, data: SaveSlot):
    with open('saves/%s' % slot, 'w') as slotfile:
        json.dump(data.serialize(data), slotfile)