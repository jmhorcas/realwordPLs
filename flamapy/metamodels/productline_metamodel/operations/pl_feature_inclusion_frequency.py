from typing import Any, cast
from collections import defaultdict

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.productline_metamodel.models import ProductLineModel


class PLFeatureInclusionFrequency(Operation):
    """The Feature Inclusion Frecuency (FIF) operation determines the frequency
    for a variable to be included in a valid solution.
    That is, in how many products are present each variable.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models.
    (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self) -> None:
        self._result: dict[Any, int] = {}

    def execute(self, model: VariabilityModel) -> 'PLFeatureInclusionFrequency':
        pl_model = cast(ProductLineModel, model)
        self._result = feature_inclusion_frequency(pl_model)
        return self

    def get_result(self) -> dict[Any, int]:
        return self._result

    def feature_inclusion_frequency(self) -> dict[Any, int]:
        return self.get_result()


def feature_inclusion_frequency(pl_model: ProductLineModel) -> dict[Any, int]:
    n_configs = len(pl_model.configurations)
    if n_configs == 0:
        return {feature: 0 for feature in pl_model.features()}
    fip: dict[Any, int] = defaultdict(int)
    for config in pl_model.configurations:
        for feature in config.get_selected_elements():
            fip[feature] += 1
    return {feature: fip[feature] for feature in pl_model.features()}
