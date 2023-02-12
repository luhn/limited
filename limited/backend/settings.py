from abc import ABC
from typing import Mapping, Any, Callable, Type, Generic, Literal, TypeVar, cast


SettingType = type | Setting | Type[Setting]
SettingMap = Mapping[str, SettingType]


X = TypeVar('X')


class Setting(Generic[X]):
    MISSING: Literal['SettingMissing'] = 'SettingMissing'

    def __init__(
        self,
        nullable: bool = False,
        optional: bool = False,
        default: X | None = None,
    ):
        self.nullable = nullable
        self.optional = optional
        self.default = default
        if not self.nullable and self.optional:
            assert self.default is not None

    @classmethod
    def cast(cls, val: Any) -> X:
        raise NotImplementedError

    def __call__(self, value: Any) -> X | None:
        if value is Setting.MISSING:
            if self.optional:
                return self.default
            else:
                raise ValueError('Value is required.')
        elif value is None:
            if self.nullable:
                return None
            else:
                raise ValueError('Value cannot be null.')
        elif isinstance(value, str):
            return self.cast(value)
        else:
            return cast(X, value)


class StrSetting(Setting[str]):
    cast = staticmethod(str)


class IntSetting(Setting[int]):
    cast = staticmethod(int)


class FloatSetting(Setting[float]):
    cast = staticmethod(float)


class BoolSetting(Setting[bool]):
    @classmethod
    def cast(cls, val: Any) -> bool:
        return bool(val)


TYPE_MAP: dict[type, type[Setting]] = {
    str: StrSetting,
    int: IntSetting,
    float: FloatSetting,
    bool: BoolSetting,
}


def _make_setting(setting: SettingType) -> Setting:
    """
    Given a ``SettingType`` (A ``Setting`` object, a ``Setting`` subclass, or a
    base ``type``), return a ``Setting`` object.

    """
    if isinstance(setting, Setting):
        return setting
    elif issubclass(setting, Setting):
        return setting()
    else:
        return TYPE_MAP[setting]()


def parse_settings(settings: SettingMap, values: Mapping[str, Any]) -> Mapping[str, Any]:
    output: Mapping[str, Any] = dict()
    for name, setting in settings.items():
        s = _make_setting(setting)
        value = values.get(name, Setting.MISSING)
        output[name] = s(value)
    return output
