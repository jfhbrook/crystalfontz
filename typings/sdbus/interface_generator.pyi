"""
This type stub file was generated by pyright.
"""

from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Literal, TYPE_CHECKING, Tuple, Union
from xml.etree.ElementTree import Element

if TYPE_CHECKING:
    ...
def camel_case_to_snake_case(camel: str) -> str:
    ...

def interface_name_to_class(interface_name: str) -> str:
    ...

def parse_str_bool(annotation_value: str) -> bool:
    ...

class DbusSigToTyping:
    _DBUS_BASIC_SIG_TO_TYPING = ...
    @classmethod
    def typing_basic(cls, char: str) -> str:
        ...
    
    @staticmethod
    def typing_into_tuple(typing_iter: Iterable[str]) -> str:
        ...
    
    @staticmethod
    def slice_container(dbus_sig_iter: Iterator[str], peek_str: str) -> str:
        ...
    
    @classmethod
    def split_sig(cls, sig: str) -> List[str]:
        ...
    
    @classmethod
    def typing_complete(cls, complete_sig: str) -> str:
        ...
    
    @classmethod
    def result_typing(cls, result_args: List[str]) -> str:
        ...
    
    @classmethod
    def sig_to_typing(cls, signature: str) -> str:
        ...
    


class DbusMemberAbstract:
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def flags_str(self) -> str:
        ...
    
    def iter_sub_elements(self, element: Element) -> None:
        ...
    


class DbusArgsIntrospection:
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def typing(self) -> str:
        ...
    
    def __repr__(self) -> str:
        ...
    


class DbusMethodInrospection(DbusMemberAbstract):
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def dbus_input_signature(self) -> str:
        ...
    
    @property
    def dbus_result_signature(self) -> str:
        ...
    
    @property
    def args_names_and_typing(self) -> List[Tuple[str, str]]:
        ...
    
    @property
    def result_typing(self) -> str:
        ...
    
    @property
    def is_results_args_valid_names(self) -> bool:
        ...
    
    @property
    def result_args_names_repr(self) -> str:
        ...
    
    def __repr__(self) -> str:
        ...
    


class DbusPropertyIntrospection(DbusMemberAbstract):
    _EMITS_CHANGED_MAP: Dict[Union[bool, Literal['const', 'invalidates']], str] = ...
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def typing(self) -> str:
        ...
    


class DbusSignalIntrospection(DbusMemberAbstract):
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def dbus_signature(self) -> str:
        ...
    
    @property
    def typing(self) -> str:
        ...
    
    @property
    def is_args_valid_names(self) -> bool:
        ...
    
    @property
    def args_names_repr(self) -> str:
        ...
    


class DbusInterfaceIntrospection:
    def __init__(self, element: Element) -> None:
        ...
    
    @property
    def has_members(self) -> bool:
        ...
    


SKIP_INTERFACES = ...
INTERFACE_TEMPLATES: Dict[str, str] = ...
def xml_to_interfaces_introspection(root: Element) -> List[DbusInterfaceIntrospection]:
    ...

def interfaces_from_file(filename_or_path: Union[str, Path]) -> List[DbusInterfaceIntrospection]:
    ...

def interfaces_from_str(xml_str: str) -> List[DbusInterfaceIntrospection]:
    ...

def generate_py_file(interfaces: List[DbusInterfaceIntrospection], include_import_header: bool = ..., do_async: bool = ...) -> str:
    ...

