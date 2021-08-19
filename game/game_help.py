import os
import argparse
from . import import_game
from .i18n import i18n

CMDS = [name for name in os.listdir('commands') if '.' not in name]

parser = argparse.ArgumentParser(
    prog='game-help', description=i18n('game-help-desc'))
parser.add_argument('cmd', nargs='?', default=None, choices=CMDS,
                    help=i18n('game-help-cmd-opt'))

completion = "-W ''"
no_load_slot = True

def main(args: list[str], slot: None = None):
    cmdargs = parser.parse_args(args[1:])
    if cmdargs.cmd is not None:
        if cmdargs.cmd not in CMDS:
            parser.error(f'no such command {cmdargs.cmd!r}')
        game = import_game(cmdargs.cmd)
        return game.main([cmdargs.cmd, '--help'], None)
    width = max(map(len, CMDS))
    for name in CMDS:
        game = import_game(name)
        print(name.ljust(width), game.parser.description)