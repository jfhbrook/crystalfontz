"""
This type stub file was generated by pyright.
"""

from typing import Any, Dict, TYPE_CHECKING, Tuple
from .sd_bus_internals import SdBusBaseError

if TYPE_CHECKING:
    ...
class DbusErrorMeta(type):
    def __new__(cls, name: str, bases: Tuple[type, ...], namespace: Dict[str, Any]) -> DbusErrorMeta:
        ...
    


class DbusFailedError(SdBusBaseError, metaclass=DbusErrorMeta):
    dbus_error_name: str = ...


class DbusNoMemoryError(DbusFailedError):
    dbus_error_name = ...


class DbusServiceUnknownError(DbusFailedError):
    dbus_error_name = ...


class DbusNameHasNoOwnerError(DbusFailedError):
    dbus_error_name = ...


class DbusNoReplyError(DbusFailedError):
    dbus_error_name = ...


class DbusIOError(DbusFailedError):
    dbus_error_name = ...


class DbusBadAddressError(DbusFailedError):
    dbus_error_name = ...


class DbusNotSupportedError(DbusFailedError):
    dbus_error_name = ...


class DbusLimitsExceededError(DbusFailedError):
    dbus_error_name = ...


class DbusAccessDeniedError(DbusFailedError):
    dbus_error_name = ...


class DbusAuthFailedError(DbusFailedError):
    dbus_error_name = ...


class DbusNoServerError(DbusFailedError):
    dbus_error_name = ...


class DbusTimeoutError(DbusFailedError):
    dbus_error_name = ...


class DbusNoNetworkError(DbusFailedError):
    dbus_error_name = ...


class DbusAddressInUseError(DbusFailedError):
    dbus_error_name = ...


class DbusDisconnectedError(DbusFailedError):
    dbus_error_name = ...


class DbusInvalidArgsError(DbusFailedError):
    dbus_error_name = ...


class DbusFileNotFoundError(DbusFailedError):
    dbus_error_name = ...


class DbusFileExistsError(DbusFailedError):
    dbus_error_name = ...


class DbusUnknownMethodError(DbusFailedError):
    dbus_error_name = ...


class DbusUnknownObjectError(DbusFailedError):
    dbus_error_name = ...


class DbusUnknownInterfaceError(DbusFailedError):
    dbus_error_name = ...


class DbusUnknownPropertyError(DbusFailedError):
    dbus_error_name = ...


class DbusPropertyReadOnlyError(DbusFailedError):
    dbus_error_name = ...


class DbusUnixProcessIdUnknownError(DbusFailedError):
    dbus_error_name = ...


class DbusInvalidSignatureError(DbusFailedError):
    dbus_error_name = ...


class DbusInvalidFileContentError(DbusFailedError):
    dbus_error_name = ...


class DbusInconsistentMessageError(DbusFailedError):
    dbus_error_name = ...


class DbusMatchRuleNotFound(DbusFailedError):
    dbus_error_name = ...


class DbusMatchRuleInvalidError(DbusFailedError):
    dbus_error_name = ...


class DbusInteractiveAuthorizationRequiredError(DbusFailedError):
    dbus_error_name = ...


