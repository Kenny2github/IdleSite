import os
import time
import argparse
from typing import Union
from .slot import Boost, CDNSetup, SaveSlot
from .i18n import i18n, pi18n

SUBCMDS = [
    'complete',
    'boosts', 'cdn', 'stats', 'transactions', 'views'
]

parser = argparse.ArgumentParser(description=i18n('check-desc'))
subparsers = parser.add_subparsers(dest='cmd', required=True)

views_parser = subparsers.add_parser(
    'views', description=i18n('check-views-desc'))
views_parser.add_argument(
    '-g', '--graph', nargs='?', metavar='days', const=7, type=int,
    help=i18n('check-graph-opt'))
views_parser.add_argument(
    '-o', '--output', metavar='filename',
    help=i18n('check-output-opt'))
views_parser.add_argument(
    '-t', '--table', nargs='?', metavar='days', const=7, type=int, default=1,
    help=i18n('check-table-opt'))
views_parser.add_argument('--csv', action='store_true', help=i18n('check-csv-opt'))

STAT_TYPES = [
    'all', 'today', 'views', 'cumulative', 'money', 'boosts', 'pending',
    'cdn', 'friends', 'promos', 'difficulty', 'day', 'ctime', 'mtime'
]
stats_parser = subparsers.add_parser(
    'stats', description=i18n('check-stats-desc'))
stats_parser.add_argument('-n', '--stats', choices=STAT_TYPES, nargs='*',
                          help=i18n('check-stat-opt'))

BOOST_TYPES = ['advertisement']
boosts_parser = subparsers.add_parser(
    'boosts', description=i18n('check-boosts-desc'))
boosts_parser.add_argument('-t', '--type', choices=BOOST_TYPES,
                           help=i18n('check-type-opt'))

trans_parser = subparsers.add_parser(
    'transactions', description=i18n('check-trans-desc'))

cdn_parser = subparsers.add_parser(
    'cdn', description=i18n('check-cdn-desc'))

complete_parser = subparsers.add_parser('complete')
complete_parser.add_argument('args', nargs=argparse.REMAINDER)

completion = "-o nosort -C 'check complete'"

TIME_FMT = '%Y-%m-%d %H:%M:%S (UTC)'

def get_complete_words() -> Union[int, list[str]]:
    import re
    point = int(os.environ['COMP_POINT'])
    split = '[' + os.environ.get('COMP_WORDBREAKS', ' "\'@><=;|&(:') + ']'
    words = re.split(split, os.environ['COMP_LINE'][:point])
    wc = len(words)
    subcmds = SUBCMDS[1:]
    if not words or words[0] != 'check':
        return 1
    if wc == 1:
        print('\n'.join(subcmds))
        return 0
    if wc == 2 and words[1] not in subcmds:
        print('\n'.join(word for word in subcmds
                        if word.startswith(words[1])))
        return 0
    if wc == 2:
        words.append('')
    return words

def complete(cmdargs: argparse.Namespace, slot: SaveSlot):
    """Generate completions. Not intended for user use."""
    if 'COMP_KEY' not in os.environ:
        return 1
    words = get_complete_words()
    if isinstance(words, int):
        return words
    subcmd = words[1]
    opts = []
    test = words[-1]
    if subcmd == 'boosts':
        OPTS = '-t --type'.split()
        if words[-2] in OPTS:
            # check boosts -t/--type <complete, may be empty>
            opts = BOOST_TYPES
        else:
            # check boosts [-t/--type advertisement] <complete>
            opts = OPTS
    elif subcmd == 'stats':
        OPTS = '-n --stats'.split()
        opts = OPTS
        dashopts = [word for word in words if word.startswith('-')]
        if words[-2] in OPTS:
            opts = STAT_TYPES
        elif dashopts and dashopts[-1] in OPTS:
            # check stats -n/--stats ... <complete>
            opts.extend(STAT_TYPES)
    elif subcmd == 'views':
        OPTS = '-g --graph -o --output -t --table --csv'.split()
        OUTOPTS = '-o --output'.split()
        if words[-2] in OUTOPTS:
            # check views -o/--output <complete>
            opts = [] # should autocomplete filenames, but idk how
        else:
            opts = OPTS
    if len(words) == 3 and (test or '-').startswith('-'):
        opts.insert(0, '-h')
        opts.insert(1, '--help')
    print('\n'.join(opt for opt in opts if opt.startswith(test)))

def graph(days: int, slot: SaveSlot, outfile: str):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise SystemExit(i18n('check-views-needs-matplotlib')) from None
    x = list(range(slot.today))[-days:]
    if slot.views:
        views, cumulative = zip(*slot.views[-days:])
    else:
        views, cumulative = (), ()
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    plot1, = ax1.plot(x, views, 'r-')
    plot2, = ax2.plot(x, cumulative, 'b-')
    ax1.set_xlabel(i18n('check-views-key-day'))
    ax1.set_ylabel(i18n('check-views-key-views'))
    ax1.yaxis.label.set_color(plot1.get_color())
    ax2.set_ylabel(i18n('check-views-key-cumulative'))
    ax2.yaxis.label.set_color(plot2.get_color())
    if outfile is None:
        fname = 'views-graph.png'
        i = 0
        while os.path.exists(fname):
            i += 1
            fname = f'views-graph.{i}.png'
    else:
        fname = outfile
    fig.savefig(fname, bbox_inches='tight')
    pi18n('check-views-fig-saved', fname)

def views(cmdargs: argparse.Namespace, slot: SaveSlot):
    if cmdargs.graph is not None:
        graph(cmdargs.graph, slot, cmdargs.output)
    if cmdargs.csv:
        sep = ','
    else:
        sep = '\t'
    header = sep.join((
        i18n('check-views-key-day'),
        i18n('check-views-key-views'),
        i18n('check-views-key-cumulative')
    ))
    print(header)
    if not cmdargs.csv:
        print('-' * (16 + len(header.rsplit(sep, 1)[-1])))
    for i, (day, (views, cumulative)) in enumerate(
        reversed(tuple(enumerate(slot.views)))
    ):
        if cmdargs.table > 0 and i >= cmdargs.table:
            break
        print(day, views, cumulative, sep=sep)

def stats(cmdargs: argparse.Namespace, slot: SaveSlot):
    data = {
        'today': slot.today,
        'views': slot.views_today,
        'cumulative': slot.views_total,
        'money': str(slot.money),
        'boosts': len(slot.boosts),
        'pending': len(slot.transactions_pending),
        'cdn': len(slot.cdn_servers),
        'friends': f'{slot.friends_pinged}/{slot.friends_available}',
        'promos': f'{slot.promos_used}/{slot.promo_available}',
    }
    config = {
        'difficulty': str(slot.difficulty_multiplier),
        'day': slot.day_length,
        'ctime': time.strftime(TIME_FMT, time.gmtime(slot.first_touch)),
        'mtime': time.strftime(TIME_FMT, time.gmtime(slot.last_touch))
    }
    if cmdargs.stats:
        if 'all' in cmdargs.stats:
            for value in data.values():
                print(value)
            for value in config.values():
                print(value)
            return
        for stat in cmdargs.stats:
            if stat in data:
                print(data[stat])
            elif stat in config:
                print(config[stat])
        return
    pi18n('check-stats-data')
    for key, value in data.items():
        pi18n(f'check-stats-key-{key}', value)
    pi18n('check-stats-config')
    for key, value in config.items():
        pi18n(f'check-stats-key-{key}', value)

def boost_list(args: list[Boost], slot: SaveSlot):
    print('\n'.join(' ' + i18n('boost-desc', boost.boost(slot), boost.expires)
                    for boost in args))

def boosts(cmdargs: argparse.Namespace, slot: SaveSlot):
    boosts: list[Boost] = slot.boosts[:]
    typed: dict[str, list[Boost]]
    if cmdargs.type is not None:
        boosts = [boost for boost in boosts
                  if boost.type == cmdargs.type]
        boost_list(boosts, slot)
    else:
        typed = {}
        for boost in boosts:
            typed.setdefault(boost.type, []).append(boost)
        for btype, boosts in typed.items():
            print(i18n('boost-%s-name' % btype))
            boost_list(boosts, slot)

def transactions(cmdargs: argparse.Namespace, slot: SaveSlot):
    digits = len(str(len(slot.transactions_pending)))
    for i, trans in enumerate(slot.transactions_pending, 1):
        print(str(i).zfill(digits), trans.description(slot), sep=')\t')

def cdn(cmdargs: argparse.Namespace, slot: SaveSlot):
    digits = len(str(len(slot.cdn_servers)))
    for i, (lat, long) in enumerate(slot.cdn_servers, 1):
        boost = CDNSetup(lat, long).boost(slot)
        lat, long = CDNSetup.str_coords(lat, long, '%3d')
        pi18n('check-cdn-line', str(i).zfill(digits), lat, long, boost)

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    return globals()[cmdargs.cmd](cmdargs, slot)
