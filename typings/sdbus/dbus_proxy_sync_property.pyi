"""
This type stub file was generated by pyright.
"""

from typing import Any, Callable, Generic, Optional, TYPE_CHECKING, Type, TypeVar
from .dbus_common_elements import DbusPropertyCommon, DbusSomethingSync
from .dbus_proxy_sync_interface_base import DbusInterfaceBase

if TYPE_CHECKING:
    ...
T = TypeVar('T')
class DbusPropertySync(DbusPropertyCommon, DbusSomethingSync, Generic[T]):
    def __init__(self, property_name: Optional[str], property_signature: str, property_getter: Callable[[DbusInterfaceBase], T], property_setter: Optional[Callable[[DbusInterfaceBase, T], None]], flags: int) -> None:
        ...
    
    def __get__(self, obj: DbusInterfaceBase, obj_class: Optional[Type[DbusInterfaceBase]] = ...) -> T:
        ...
    
    def __set__(self, obj: DbusInterfaceBase, value: T) -> None:
        ...
    


def dbus_property(property_signature: str = ..., flags: int = ..., property_name: Optional[str] = ...) -> Callable[[Callable[[Any], T]], DbusPropertySync[T]]:
    ...

