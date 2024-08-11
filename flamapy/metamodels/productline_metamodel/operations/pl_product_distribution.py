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

    def execute(self, model: VariabilityModel) -> 'PLProductDistribution':
        pl_model = cast(ProductLineModel, model)
        self._result = product_distribution(pl_model)
        return self

    def get_result(self) -> list[int]:
        return self._result

    def product_distribution(self) -> list[int]:
        return self.get_result()

    def descriptive_statistics(self) -> dict[str, Any]:
        return descriptive_statistics(self._result)


def product_distribution(pl_model: ProductLineModel) -> list[int]:
    dist: dict[int, int] = defaultdict(int)
    for config in pl_model.configurations:
        dist[len(config.get_selected_elements())] += 1
    return [dist[i] for i in range(0, len(pl_model.features()) + 1)]
   

def descriptive_statistics(prod_dist: list[int]) -> dict[str, Any]: # noqa: MC0001
    total_elements = sum(prod_dist)
    if total_elements == 0:
        return {
            'Mean': 0,
            'Standard deviation': 0,
            'Median': 0,
            'Median absolute deviation': 0,
            'Mode': 0,
            'Min': None,
            'Max': None,
            'Range': 0
        }

    total_sum = 0
    running_total = 0
    median1: Optional[float] = None
    median2: Optional[float] = None
    median_pos1 = (total_elements + 1) // 2
    median_pos2 = (total_elements + 2) // 2
    min_val = None
    max_val = None
    mode = None

    sum_squared_diff = 0
    abs_deviation_total = 0
    abs_deviation_running_total = 0
    mad1: Optional[float] = None
    mad2: Optional[float] = None
    mad_pos1 = (total_elements + 1) // 2
    mad_pos2 = (total_elements + 2) // 2

    for i, count in enumerate(prod_dist):
        if count > 0:
            if min_val is None:
                min_val = i
            max_val = i

            total_sum += i * count
            running_total += count

            if mode is None:
                mode = i

            if median1 is None and running_total >= median_pos1:
                median1 = i
            if median2 is None and running_total >= median_pos2:
                median2 = i

    mean = total_sum // total_elements
    median = (median1 + median2) // 2 if median1 is not None and median2 is not None else 0

    running_total = 0
    for i, count in enumerate(prod_dist):
        if count > 0:
            deviation = abs(i - median)
            abs_deviation_total += deviation * count
            running_total += count

            sum_squared_diff += count * (i - mean) ** 2

            abs_deviation_running_total += count
            if mad1 is None and abs_deviation_running_total >= mad_pos1:
                mad1 = deviation
            if mad2 is None and abs_deviation_running_total >= mad_pos2:
                mad2 = deviation
            if mad1 is not None and mad2 is not None:
                break

    std_dev = (sum_squared_diff / total_elements) ** 0.5
    mad = (mad1 + mad2) / 2 if mad1 is not None and mad2 is not None else 0

    statistics = {
        'Mean': mean,
        'Standard deviation': std_dev,
        'Median': median,
        'Median absolute deviation': mad,
        'Mode': mode,
        'Min': min_val,
        'Max': max_val,
        'Range': max_val - min_val if min_val is not None and max_val is not None else 0
    }
    return statistics