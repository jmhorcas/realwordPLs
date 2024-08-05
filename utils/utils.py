from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature


def complete_configuration(configuration: Configuration, fm_model: FeatureModel) -> Configuration:
    configs_elements = dict(configuration.elements)
    for element in configuration.get_selected_elements():
        feature = fm_model.get_feature_by_name(element)
        configs_elements.update({parent: True for parent in get_all_parents(feature)})
    return Configuration(configs_elements)


def get_all_parents(feature: Feature) -> list[str]:
    parent = feature.get_parent()
    return [] if parent is None  else [parent.name] + get_all_parents(parent)
