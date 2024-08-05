import csv

from flamapy.core.transformations import TextToModel
from flamapy.metamodels.configuration_metamodel.models import Configuration


class ConfigurationsCSVReader(TextToModel):
    """Read a list of configurations in a CSV file.

    The CSV format is as follows:
    Element1, Element2, Element3,..., ElementN
    True, True, False,..., True
    True, False, False,..., False
    True, True, True,..., True
    ...

    It has a "store_only_selected_elements" (default to False) to indicate that configurations
    save only those elements with a True value.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'csv'

    def __init__(self, path: str) -> None:
        self.path = path
        self._only_selected_elements = False

    def store_only_selected_elements(self, only_selected_elements: bool = False) -> None:
        self._only_selected_elements = only_selected_elements

    def transform(self) -> list[Configuration]:
        with open(self.path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)

            configurations = []
            for row in reader:
                configurations.append(from_csv_to_configuration(row, 
                                                                self._only_selected_elements))
        return configurations


def from_csv_to_configuration(content: dict[str, str],
                              store_only_selected_elements: bool) -> Configuration:
    elements = {}
    for element, value in content.items():
        if not element is None:
            if value.lower() == "true":
                elements[element] = True
            else:
                if not store_only_selected_elements:
                    elements[element] = False
    return Configuration(elements)
