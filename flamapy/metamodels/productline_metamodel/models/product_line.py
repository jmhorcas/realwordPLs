from enum import Enum
from typing import Optional, Any, Union

from flamapy.core.models import VariabilityModel
from flamapy.metamodels.configuration_metamodel.models import Configuration


class ProductLineModel(VariabilityModel):
    """A product line is a set of configurations."""

    @staticmethod
    def get_extension() -> str:
        return 'pl'

    def __init__(self) -> None:
        self._configurations: set[Configuration] = set()
        self._features: set[Any] = set()

    @property
    def configurations(self) -> set[Configuration]:
        return self._configurations

    @configurations.setter
    def configurations(self, configurations: set[Configuration]) -> None:
        self._configurations = configurations
        self._features = set().union(*[set(config.get_selected_elements()) 
                                       for config in configurations])

    def features(self) -> set[Any]:
        return self._features

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, ProductLineModel) 
                and len(self.configurations) == len(other.configurations)
                and all(config in other.configurations for config in self.configurations))

    def __str__(self) -> str:
        res = 'Product Line\n'
        res += f'Features: ({len(self._features)}) {self._features}\n'
        res += f'Products: ({len(self._configurations)})\n'
        for i, config in enumerate(self.configurations):
            res += f'{i}: {config.get_selected_elements()}\n'
        return res

    def __hash__(self) -> int:
        return hash(frozenset(self.configurations))
