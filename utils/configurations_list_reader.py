from flamapy.core.transformations import TextToModel
from flamapy.metamodels.configuration_metamodel.models import Configuration


class ConfigurationsListReader(TextToModel):
    """Read a list of configurations in a text file.

    The file format is as follows:
    ['Element1', 'Element2',..., 'ElementX']
    ['Element1', 'Element2',..., 'ElementY']
    ['Element1', 'Element2',..., 'ElementZ']
    ...

    Each list represents the selected elements in a configuration.
    """

    @staticmethod
    def get_source_extension() -> str:
        return 'txt'

    def __init__(self, path: str) -> None:
        self.path = path

    def transform(self) -> list[Configuration]:
        with open(self.path, newline='', encoding='utf-8') as file:
            configurations = []
            for line in file.readlines():
                elements = {element: True for element in eval(line)}
                config = Configuration(elements)
                configurations.append(config)
        return configurations
