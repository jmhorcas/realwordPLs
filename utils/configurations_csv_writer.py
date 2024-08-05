from flamapy.core.transformations import ModelToText
from flamapy.metamodels.configuration_metamodel.models import Configuration


CSV_SEPARATOR = ','
LINE_SEPARATOR = '\n'


class ConfigurationsCSVWriter(ModelToText):
    """Write a list of configurations to a CSV file.
    
    The CSV format is as follows:
    Element1, Element2, Element3,..., ElementN
    True, True, False,..., True
    True, False, False,..., False
    True, True, True,..., True
    ...
    
    """

    @staticmethod
    def get_destination_extension() -> str:
        return 'csv'

    def __init__(self, path: str) -> None:
        self.path = path
        self.elements = []
        self.configurations = []

    def set_elements(self, elements: list[str]) -> None:
        """Elements to be appeared as header in the CSV file."""
        self.elements = elements

    def set_configurations(self, configurations: list[Configuration]) -> None:
        """Configurations to be serialized."""
        self.configurations = configurations

    def transform(self) -> str:
        configs_str = configurations_to_csv(self.elements, self.configurations)
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(configs_str)
        return configs_str


def configurations_to_csv(elements: list[str], configurations: list[Configuration]) -> str:
    header = CSV_SEPARATOR.join(elements)

    configs_str = []
    for config in configurations:
        configs_elements = [f for f in config.get_selected_elements()]
        row = CSV_SEPARATOR.join((str(f in configs_elements) for f in elements))
        configs_str.append(row)
    return f'{header}{LINE_SEPARATOR}{LINE_SEPARATOR.join(configs_str)}'
