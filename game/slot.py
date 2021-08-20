from __future__ import annotations
from time import time
import math
from decimal import Decimal
from dataclasses import dataclass, field
from .i18n import i18n, pi18n

END = 8_000_000_000

class _JL(type):
    """Metaclass that enables a class to be loaded from JSON."""

    cls_names: dict[str, _JL] = {}

    # mcls: _JL
    def __new__(mcls, name: str, bases: tuple, attrs: dict) -> type:
        if name.startswith('None'):
            return None
        mname = '__%s__' % name.casefold()
        attrs['__mname__'] = mname
        cls = type(name, bases, attrs)
        mcls.cls_names[mname] = cls
        return cls

    @classmethod
    def unserialize(cls, self):
        """Load a class object from JSON."""
        if isinstance(self, (str, int, float, Decimal, bool, type(None))):
            return self
        if getattr(type(self), '__mname__', None) in cls.cls_names:
            return self
        if isinstance(self, dict):
            if '__decimal__' in self:
                return Decimal(self['__decimal__'])
            for key in list(self.keys()):
                self[key] = cls.unserialize(self[key])
            if self.get('__mname__') in cls.cls_names:
                ocls = cls.cls_names[self.pop('__mname__')]
                return ocls(**self)
            return self
        if isinstance(self, list):
            for i in range(len(self)):
                self[i] = cls.unserialize(self[i])
            return self
        if isinstance(self, tuple):
            return tuple(map(cls.unserialize, self))
        raise TypeError('cannot unserialize %r of type %r' % (
            self, type(self).__name__))

class _JS:
    __mname__: str

    @classmethod
    def serialize(cls, self):
        """Transform this object into JSON natives."""
        if isinstance(self, (str, int, float, bool, type(None))):
            return self
        if isinstance(self, Decimal):
            return {'__decimal__': str(self)}
        if isinstance(self, dict):
            for key in list(self.keys()):
                self[key] = cls.serialize(self[key])
            return self
        if isinstance(self, list):
            for i in range(len(self)):
                self[i] = cls.serialize(self[i])
            return self
        if isinstance(self, tuple):
            return tuple(map(cls.serialize, self))
        if isinstance(self, _JS): # any _JS subclass, not just cls
            obj = {}
            for attr in self.__annotations__:
                obj[attr] = cls.serialize(getattr(self, attr))
            obj['__mname__'] = self.__mname__
            return obj
        raise TypeError('cannot serialize %r of type %r' % (
            self, type(self).__name__))

class Boost(_JS):
    """ABC for view-*rate* boosts"""

    expires: int # day number when boost expires

    def activate(self, slot: SaveSlot) -> None:
        """Activate this boost."""
        raise NotImplementedError

    def boost(self, slot: SaveSlot) -> int:
        """The amount of view boost, in views per day."""
        raise NotImplementedError

    def cost(self, slot: SaveSlot) -> Decimal:
        """The cost of this much of a view boost."""
        raise NotImplementedError

    def description(self, slot: SaveSlot) -> str:
        """Human-readable description of this boost."""
        raise NotImplementedError

    @property
    def type(self) -> str:
        """The type of boost. Equivalent to type(boost).__name__.casefold()."""
        # apparently this is not an infinite recursion
        return type(self).__name__.casefold()

@dataclass
class Advertisement(Boost, metaclass=_JL):
    expires: int # day number
    power: int # in views/day

    def activate(self, slot: SaveSlot) -> None:
        slot.boosts.append(self)

    def boost(self, slot: SaveSlot) -> int:
        return self.power

    def cost(self, slot: SaveSlot) -> Decimal:
        """The cost of this much of a view boost for this long."""
        return (self.expires - slot.today) * self.boost(slot) \
            * slot.difficulty_multiplier

    def description(self, slot: SaveSlot) -> str:
        return i18n('advertisement-desc', self.power, self.expires)

@dataclass
class CDNSetup(Boost, metaclass=_JL):
    # no more specificity needed than integer degrees
    latitude: int # degrees north (+) / south (-)
    longitude: int # degrees east (+) / west (-)

    @property
    def coords(self) -> tuple[int, int]:
        """The coordinates of this CDN server."""
        return (self.latitude, self.longitude)

    expires = None
    K = 1

    def activate(self, slot: SaveSlot) -> None:
        slot.view_rate += self.boost(slot)
        slot.cdn_servers.append(self.coords)

    def boost(self, slot: SaveSlot) -> int:
        # boost is proportional to minimum spherical orthogonal
        # distance between this new server and any other
        if len(slot.cdn_servers) == 1 and slot.cdn_servers[0] == self.coords:
            # no boost when this is the only server
            return 0
        return self.K * min(
            abs(self.latitude - lat) + abs(self.longitude - long)
            for lat, long in slot.cdn_servers
            if (lat, long) != self.coords)

    def cost(self, slot: SaveSlot) -> Decimal:
        # 540 is the maximum possible spherical orthogonal
        # distance between any two points
        return (540 * self.K - self.boost(slot)) \
            * slot.difficulty_multiplier

    def description(self, slot: SaveSlot) -> str:
        return i18n('cdnsetup-desc', *self.str_coords(
            *self.coords), self.boost(slot))

    @staticmethod
    def str_coords(lat: int, long: int, fmt: str = '%s') -> tuple[str, str]:
        unit_lat = unit_long = '\N{DEGREE SIGN}'
        if lat >= 0:
            unit_lat += 'N'
        else:
            unit_lat += 'S'
        if long >= 0:
            unit_long += 'E'
        else:
            unit_long += 'W'
        return (
            (fmt + '%s') % (abs(lat), unit_lat),
            (fmt + '%s') % (abs(long), unit_long))

@dataclass
class Transaction(_JS, metaclass=_JL):
    # day number on which the transaction clears
    clear_date: int
    # what happens when it clears
    action: Boost

    def clear(self, slot: SaveSlot):
        self.action.activate(slot)
        slot.money -= self.action.cost(slot)

    def description(self, slot: SaveSlot) -> str:
        return i18n('transaction-desc', self.action.description(slot),
                    self.clear_date, self.action.cost(slot))

@dataclass
class SaveSlot(_JS, metaclass=_JL):
    """The data saved in a save slot."""

    # [(views, cumulative), (views next day, cumulative)]
    views: list[tuple[int, int]] = field(default_factory=list)
    view_rate: int = 0 # views per day, permanent rate
    # temporary boosts only
    boosts: list[Boost] = field(default_factory=list)

    transactions_pending: list[Transaction] = field(default_factory=list)

    # [(lat, long), (lat, long)]
    cdn_servers: list[tuple[int, int]] = field(
        default_factory=lambda: [(41, 74)])

    money: Decimal = Decimal()

    difficulty_multiplier: Decimal = Decimal('1')
    friends_pinged: int = 0
    promos_used: int = 0

    day_length: int = 60 * 60 * 24 # length of in-game day, default real day
    first_touch: int = field(default_factory=lambda: int(time()))
    last_touch: int = field(default_factory=lambda: int(time()))

    continued: bool = False

    @property
    def friends_available(self) -> int:
        """The number of friends available to advertise to."""
        return int(100 * self.difficulty_multiplier)
    @property
    def promo_available(self) -> int:
        """The number of self-promo channels available to advertise to."""
        return 10000

    @property
    def views_today(self) -> int:
        """The number of views during the most recent day."""
        if self.views:
            return self.views[-1][0]
        return 0
    @property
    def views_total(self) -> int:
        """The number of views during the lifetime of the site."""
        if self.views:
            return self.views[-1][-1]
        return 0
    @property
    def today(self) -> int:
        """The current day number."""
        return (self.last_touch - self.first_touch) // self.day_length

    def update(self):
        """Perform updates since last day checked"""
        last_touch = self.last_touch
        self.last_touch = int(time())
        old_day_number = (last_touch - self.first_touch) // self.day_length
        day_number = (self.last_touch - self.first_touch) // self.day_length
        if len(self.views) != old_day_number:
            raise RuntimeError(i18n('wrong-view-day-count'))
        warned_trans = []
        for day in range(old_day_number+1, day_number+1):
            # expire boosts
            self.boosts = [boost for boost in self.boosts
                           if boost.expires is None
                           or boost.expires > day]
            # clear transactions
            transactions_pending: list[Transaction] = []
            cleared_transactions: list[Transaction] = []
            money = self.money
            for transaction in self.transactions_pending:
                cost = transaction.action.cost(self)
                if transaction.clear_date > day:
                    transactions_pending.append(transaction)
                elif cost <= money:
                    cleared_transactions.append(transaction)
                    money -= cost
                else:
                    if transaction not in warned_trans:
                        warned_trans.append(transaction)
                    transactions_pending.append(transaction)
            self.transactions_pending = transactions_pending
            for transaction in cleared_transactions:
                transaction.clear(self)
            # update views
            view_rate = self.view_rate + sum(
                boost.boost(self) for boost in self.boosts)
            if self.views:
                bonus = math.floor(math.log10(self.views[-1][-1] or 1))
                self.view_rate += bonus
                view_rate += bonus
                self.views.append((
                    view_rate, self.views[-1][-1] + view_rate))
            else:
                self.views.append((view_rate, view_rate))
        for transaction in warned_trans:
            pi18n('transaction-not-cleared',
                  self.transactions_pending.index(transaction) + 1)
        if self.views_total >= END and not self.continued:
            pi18n('game-won', self.views_total, self.today)
            conf = input(i18n('game-continue'))
            if conf[0].casefold() != 'y':
                pi18n('game-done')
                with open('saves/.current', 'w'):
                    # wipe the "current" pointer.
                    # if this was their only save, trying to use it
                    # will at least still show a warning that it is
                    # being selected.
                    # otherwise, they will have to choose or create a save,
                    # and hopefully not choose this one again.
                    pass
                raise SystemExit(1)
            pi18n('game-continued')
            self.continued = True
