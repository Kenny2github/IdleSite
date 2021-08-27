import sys
import os
import re
import json
import importlib
from typing import Optional, Callable
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
            slot = get_current_slot()
    else: # specified at command line
        del argv[idx] # pop --save-slot argument
        try:
            slot = argv[idx] # argument value shifted left
            del argv[idx] # pop argument value after reading
        except IndexError:
            sys.exit(i18n('error-save-slot'))
    return slot


def get_current_slot() -> str:
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
        current.write(slot)  # save current slot
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

CCallback = Callable[[Optional[str], list[str]], list[str]]

def dynamic_completion(subcmds: list[str], callback: CCallback):
    if 'COMP_KEY' not in os.environ:
        # untranslated: should not be encountered by regular users
        sys.exit('Missing COMP_KEY environment variable')
    point = int(os.environ['COMP_POINT'])
    split = '[' + os.environ.get('COMP_WORDBREAKS', ' "\'@><=;|&(:') + ']'
    words = re.split(split, os.environ['COMP_LINE'][:point])
    try:
        subcmd = [word for word in words if word in subcmds][0]
    except IndexError:
        subcmd = None
    if words[-1] == subcmd:
        subcmd = None
    opts = callback(subcmd, words)
    print('\n'.join(opt for opt in opts if opt.startswith(words[-1])))
    sys.exit(0)

def import_game(name: str):
    return importlib.import_module('game.' + name.replace('-', '_'))
