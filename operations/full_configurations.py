import logging
from typing import cast

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature
from flamapy.metamodels.pysat_metamodel.operations import PySATCoreFeatures
from flamapy.metamodels.fm_metamodel.operations import FMVariationPoints


LOGGER = logging.getLogger('FullConfigurations')


class FullConfigurations(Operation):
    """Full configurations is similar to the filter operation which takes as input a 
    feature model and a partial configuration and returns the set of full configurations that 
    can be derived from the model.
    
    The different aspect of this new operation is that it takes into account the already decided
    variation points, so, they are not considered as in the resulting full configurations.
    For example, let us consider an 'or-group' where some features of such group have been already
    selected in the provided partial configuration. The full configurations derived will not
    contain any other features under such group.
    As result, the number of configurations returned by this operation is fewer than the original
    filter operation.

    This operation assumes that the provided partial configuration is valid in the sense that all
    features in the configuration are valid feature in the model.
    """

    def __init__(self) -> None:
        self.result: list[Configuration] = []
        self.configuration: Configuration = None
        self.sat_model = None
        self.solver = None

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: VariabilityModel) -> 'FullConfigurations':
        sat_model = cast(PySATModel, model)
        self.result = full_configurations(self.configuration, sat_model.original_model, sat_model)
        return self

    def full_configurations(self) -> list[Configuration]:
        return self.get_result()

    def get_result(self) -> list[Configuration]:
        return self.result


def full_configurations(configuration: Configuration,
                        fm_model: FeatureModel, 
                        sat_model: PySATModel) -> list[Configuration]:
    # Select required features (core and parents)
    core_features = set(PySATCoreFeatures().execute(sat_model).get_result())
    parent_features = [get_all_parents(fm_model.get_feature_by_name(f)) 
                       for f in configuration.get_selected_elements()]
    parent_features = set().union(*parent_features)
    config = Configuration(dict(configuration.elements))
    for feature in core_features.union(parent_features):
        config.elements[feature] = True
    selected_elements = config.get_selected_elements()
    # Avoid decided variation points
    vps = FMVariationPoints().execute(fm_model).get_result()
    for vp, variants in vps.items():
        if vp.is_group() and vp.name in selected_elements and any(v.name in selected_elements 
                                                                  for v in variants):
            for variant in variants:
                if variant.name not in selected_elements:
                    config.elements[variant.name] = False
    # Create assumptions
    assumptions = []
    for feature, selected in config.elements.items():
        variable = sat_model.variables.get(feature)
        if selected:
            assumptions.append(variable)
        else:
            assumptions.append(-variable)
    # Use the solver to enumerate the configurations
    new_configurations = []
    with Solver(name='glucose3') as solver:
        for clause in sat_model.get_all_clauses():
            solver.add_clause(clause)
        for solution in solver.enum_models(assumptions=assumptions):
            new_config = {}
            for variable in solution:
                if variable is not None and variable > 0:
                    new_config[sat_model.features.get(variable)] = True
            new_configurations.append(Configuration(new_config))
    return new_configurations


def get_all_parents(feature: Feature) -> set[str]:
    parent = feature.get_parent()
    return set() if parent is None  else {parent.name}.union(get_all_parents(parent))
