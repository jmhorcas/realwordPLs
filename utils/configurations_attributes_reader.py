import csv
from typing import Any

from flamapy.core.transformations import TextToModel
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.models import FeatureModel
from utils import utils


CSV_SEPARATOR = ','
LINE_SEPARATOR = '\n'
DOUBLE_PRECISION = 4
MIN_INT = 1
MAX_INT = 100


class ConfigurationsAttributesReader(TextToModel):
    """Read a list of configurations along with their attributes in a CSV format.

    The CSV format is as follows:
    Feature1, Feature2, Feature3,...,FeatureN, Attribute1, Attribute2, Attribute3,..., AttributeM
    true, true, false,..., true, 100, 1.5,..., false
    true, false, false,..., false, 200, 1.0,..., true
    true, true, true,..., true, 50, 0.25,..., true
    ...

    """

    @staticmethod
    def get_source_extension() -> str:
        return 'csv'

    def __init__(self, path: str, source_model: FeatureModel) -> None:
        self.path = path
        self.source_model = source_model

    def set_configurations(self, configurations: list[Configuration]):
        self.configurations = configurations

    def transform(self) -> str:
        with open(self.path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)

            content_list = []
            index = 1
            for row in reader:
                content_list.append(from_csv_to_configurations(self.source_model, row, index))
                index += 1
        return content_list


def from_csv_to_configurations(fm: FeatureModel, content: dict[str, str], index: int) -> tuple[list[Configuration], dict[int, dict[str, Any]]]:
    # content: CSV completo
    """
        Returns a tuple that consists in:
            - a list of configurations.
            - a dictionary (key -> value), where:
                - key is the index of the configuration.
                - value is a dictionary of attributes' names -> attributes values.
    """
    configuration_list = []
    attributes_dict = {}
    index_attributes_dict = {}
    for key, value in content.items():
        feature = fm.get_feature_by_name(key)
        if not feature is None:
            if value.lower() == "true":
                configuration_list.append(feature)
        else:
            attributes_dict[key] = parse_value(value)
            index_attributes_dict[index] = attributes_dict
    return configuration_list, index_attributes_dict


def parse_value(value: str) -> Any:
    """Given a value represented in a string, returns the associated value instance."""
    result = None
    try:
        result = int(value)
    except ValueError:
        try:
            result = float(value)
        except ValueError:
            if value.lower() in ['true', 'false']:
                result = True if value.lower() == 'true' else False
            else:
                result = value
    return result
