import time
import argparse
from .slot import SaveSlot
from .i18n import i18n, pi18n

parser = argparse.ArgumentParser(prog='check', description=i18n('check-desc'))
parser.add_argument('value', choices=['views', 'stats'],
                    help=i18n('check-value-opt'))
parser.add_argument('args', nargs=argparse.REMAINDER,
                    help=i18n('check-args-opt'))
views_parser = argparse.ArgumentParser(
    prog='check views', description=i18n('check-views-desc'))
group = views_parser.add_mutually_exclusive_group()
group.add_argument(
    '-g', '--graph', nargs='?', metavar='days', const=7, type=int,
    help=i18n('check-graph-opt'))
views_parser.add_argument(
    '-t', '--table', nargs='?', metavar='days', const=7, type=int, default=1,
    help=i18n('check-table-opt'))
group.add_argument('--csv', action='store_true', help=i18n('check-csv-opt'))
stats_parser = argparse.ArgumentParser(
    prog='check stats', description=i18n('check-stats-desc'))
stats_parser.add_argument('-n', '--stats', choices=[
    'all', 'views', 'cumulative', 'money', 'boosts', 'pending',
    'cdn', 'friends', 'promos', 'difficulty', 'day', 'ctime', 'mtime'
], nargs='*', help=i18n('check-stat-opt'))

completion = "-o nosort -W 'views stats -g --graph " \
    "-t --table -n --stats'"

TIME_FMT = '%Y-%m-%d %H:%M:%S (UTC)'

def views(args: list[str], slot: SaveSlot):
    cmdargs = views_parser.parse_args(args)
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

def stats(args: list[str], slot: SaveSlot):
    cmdargs = stats_parser.parse_args(args)
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

def main(args: list[str], slot: SaveSlot):
    cmdargs = parser.parse_args(args[1:])
    return globals()[cmdargs.value](cmdargs.args, slot)