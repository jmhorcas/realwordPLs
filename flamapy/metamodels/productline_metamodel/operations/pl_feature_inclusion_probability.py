from typing import Any, cast
from collections import defaultdict

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.productline_metamodel.models import ProductLineModel


class PLFeatureInclusionProbability(Operation):
    """The Feature Inclusion Probability (FIP) operation determines the probability
    for a variable to be included in a valid solution.

    Ref.: [Heradio et al. 2019. Supporting the Statistical Analysis of Variability Models.
    (https://doi.org/10.1109/ICSE.2019.00091)]
    """

    def __init__(self) -> None:
        self._result: dict[Any, float] = {}

    def execute(self, model: VariabilityModel) -> 'PLFeatureInclusionProbability':
        pl_model = cast(ProductLineModel, model)
        self._result = feature_inclusion_probability(pl_model)
        return self

    def get_result(self) -> dict[Any, float]:
        return self._result

    def feature_inclusion_probability(self) -> dict[Any, float]:
        return self.get_result()


def feature_inclusion_probability(pl_model: ProductLineModel) -> dict[Any, float]:
    n_configs = len(pl_model.configurations)
    if n_configs == 0:
        return {feature: 0.0 for feature in pl_model.features()}
    fip: dict[Any, float] = defaultdict(float)
    for config in pl_model.configurations:
        for feature in config.get_selected_elements():
            fip[feature] += 1
    return {feature: fip[feature] / n_configs for feature in pl_model.features()}
