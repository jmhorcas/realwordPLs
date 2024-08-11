import statistics
from collections import defaultdict
from typing import cast, Any, Optional

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.productline_metamodel.models import ProductLineModel


class PLProductDistribution(Operation):
    """""The product distribution computes the number of activated features per product.

     The operation returns a list that stores:
        + In index 0, the number of products with 0 features activated.
        + In index 1, the number of products with 1 feature activated.
        ...
        + In index n, the number of products with n features activated.

    For detailed information, see the paper: 
        Heradio, R., Fernandez-Amoros, D., Mayr-Dorn, C., Egyed, A.:
        Supporting the statistical analysis of variability models. 
        In: 41st International Conference on Software Engineering (ICSE), pp. 843-853. 2019.
        DOI: https://doi.org/10.1109/ICSE.2019.00091
    """

    def __init__(self) -> None:
        self._result: list[int] = []
        self._prod_dist: dict[int, int] = dict()
        self._desc_stats: dict[str, Any] = dict()

    def execute(self, model: VariabilityModel) -> 'PLProductDistribution':
        pl_model = cast(ProductLineModel, model)
        self._prod_dist = product_distribution(pl_model)
        self._desc_stats = descriptive_statistics(self._prod_dist)
        self._result = [self._prod_dist[i] for i in range(0, len(pl_model.features()) + 1)]
        return self

    def get_result(self) -> list[int]:
        return self._result

    def product_distribution(self) -> list[int]:
        return self.get_result()

    def descriptive_statistics(self) -> dict[str, Any]:
        return self._desc_stats


def product_distribution(pl_model: ProductLineModel) -> dict[int, int]:
    dist: dict[int, int] = defaultdict(int)
    for config in pl_model.configurations:
        dist[len(config.get_selected_elements())] += 1
    return dist
   

def descriptive_statistics(prod_dist: dict[int, int]) -> dict[str, Any]:
    desc_stats: dict[str, Any] = dict()
    desc_stats['Min'] = min(prod_dist.keys())
    desc_stats['Max'] = max(prod_dist.keys())
    desc_stats['Range'] = desc_stats['Max'] - desc_stats['Min']
    desc_stats['Mode'] = max(prod_dist, key=prod_dist.get)
    expanded_list = [elem for list in ([i] * count for i, count in prod_dist.items()) 
                     for elem in list]
    desc_stats['Mean'] = statistics.mean(expanded_list)
    desc_stats['Standard deviation'] = statistics.stdev(expanded_list)
    desc_stats['Median'] = statistics.median(expanded_list)
    #desc_stats['Median absolute deviation'] = None
    return desc_stats
