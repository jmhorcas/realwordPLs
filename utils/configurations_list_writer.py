from flamapy.core.transformations import ModelToText
from flamapy.metamodels.configuration_metamodel.models import Configuration


LINE_SEPARATOR = '\n'


class ConfigurationsListWriter(ModelToText):
    """Write a list of configurations in a text file.

    The file format is as follows:
    ['Element1', 'Element2',..., 'ElementX']
    ['Element1', 'Element2',..., 'ElementY']
    ['Element1', 'Element2',..., 'ElementZ']
    ...

    Each list represents the selected elements in a configuration.
    """

    @staticmethod
    def get_destination_extension() -> str:
        return 'txt'

    def __init__(self, path: str) -> None:
        self.path = path
        self.configurations = []

    def set_configurations(self, configurations: list[Configuration]):
        """Configurations to be serialized."""
        self.configurations = configurations

    def transform(self) -> str:
        with open(self.path, 'w', encoding='utf-8') as file:
            result = f'{LINE_SEPARATOR.join(str(config.get_selected_elements()) 
                                            for config in self.configurations)}'
            file.write(result)
        return result
