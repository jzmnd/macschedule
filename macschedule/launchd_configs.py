from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, TypeVar, Generic

from lxml import etree

T = TypeVar("T")


class LauchdConfigBase(Generic[T], ABC):
    name: str = NotImplemented

    def __init__(self, parent_element, data: T) -> None:
        self.parent_element = parent_element
        self.data = data

    def _generate_key(self) -> None:
        key = etree.SubElement(self.parent_element, "key")
        key.text = self.name

    @abstractmethod
    def _generate_data(self) -> None:
        raise NotImplementedError

    def generate_elements(self) -> None:
        self._generate_key()
        self._generate_data()


class StringConfig(LauchdConfigBase[str]):

    def _generate_data(self) -> None:
        string = etree.SubElement(self.parent_element, "string")
        string.text = self.data


class IntegerConfig(LauchdConfigBase[int]):

    def _generate_data(self) -> None:
        integer = etree.SubElement(self.parent_element, "integer")
        integer.text = str(self.data)


class ArrStringConfig(LauchdConfigBase[List[str]]):

    def _generate_data(self) -> None:
        array = etree.SubElement(self.parent_element, "array")
        for s in self.data:
            string = etree.SubElement(array, "string")
            string.text = s


class DictStringConfig(LauchdConfigBase[Dict[str, str]]):

    def _generate_data(self) -> None:
        dict_elem = etree.SubElement(self.parent_element, "dict")
        for k, v in self.data.items():
            key = etree.SubElement(dict_elem, "key")
            key.text = k
            val = etree.SubElement(dict_elem, "string")
            val.text = v


class ArrDictIntegerConfig(LauchdConfigBase[List[Dict[str, int]]]):

    def _generate_data(self) -> None:
        array = etree.SubElement(self.parent_element, "array")
        for d in self.data:
            dict_elem = etree.SubElement(array, "dict")
            for k, v in d.items():
                key = etree.SubElement(dict_elem, "key")
                key.text = k
                val = etree.SubElement(dict_elem, "integer")
                val.text = str(v)


class Label(StringConfig):
    name: str = "Label"


class ProgramArguments(ArrStringConfig):
    name: str = "ProgramArguments"


class EnvironmentVariables(DictStringConfig):
    name: str = "EnvironmentVariables"


class StartCalendarInterval(ArrDictIntegerConfig):
    name: str = "StartCalendarInterval"


class StartInterval(IntegerConfig):
    name: str = "StartInterval"


class ExitTimeOut(IntegerConfig):
    name: str = "ExitTimeOut"


class WorkingDirectory(StringConfig):
    name: str = "WorkingDirectory"


class StandardErrorPath(StringConfig):
    name: str = "StandardErrorPath"


class StandardOutPath(StringConfig):
    name: str = "StandardOutPath"
