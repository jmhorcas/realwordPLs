import csv
from typing import Any

from flamapy.core.transformations import TextToModel
from flamapy.metamodels.configuration_metamodel.models import Configuration


class ConfigurationsAttributesReader(TextToModel):
    """Read a list of configurations in a csv file.

    The file format is as follows:
    Configuration, Attribute1, Attribute2,..., AttributeN
    "['Element1', 'Element2',..., 'ElementX']", value1, value2,..., valueN 
    "['Element1', 'Element2',..., 'ElementY']", value1, value2,..., valueY
    "['Element1', 'Element2',..., 'ElementZ']", value1, value2,..., valueZ
    ...

    Each list represents the selected elements in a configuration.
    The 'Configuration' column does not need to be the first column in the file,
    but the configuration column must be called 'Configuration'.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'csv'

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> list[tuple[Configuration, dict[str, Any]]]:
        with open(self.path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
            
            content_list = []
            for row in reader:
                content_list.append(from_csv_to_configurations(row))
        return content_list


def from_csv_to_configurations(content: dict[str, str]) -> tuple[Configuration, dict[str, Any]]:
    """
        Returns a tuple that consists in:
            - the configuration.
            - a dictionary (key -> value), where:
                - key is the attribute name.
                - value is the attribute value.
    """
    attributes_dict = {}
    elements = {element: True for element in eval(content['Configuration'])}
    config = Configuration(elements)
    for key, value in content.items():
        if key != 'Configuration':
            attributes_dict[key] = parse_value(value)
    return config, attributes_dict


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