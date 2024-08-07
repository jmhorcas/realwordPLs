import logging
from typing import cast

from pysat.solvers import Solver

from flamapy.core.models import VariabilityModel
from flamapy.core.operations import Operation
from flamapy.core.exceptions import FlamaException
from flamapy.metamodels.configuration_metamodel.models.configuration import Configuration
from flamapy.metamodels.pysat_metamodel.models.pysat_model import PySATModel
from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature


LOGGER = logging.getLogger('CompleteConfiguration')


class CompleteConfiguration(Operation):
    """Complete a partial configuration until a full configuration is found.
    
    The rules to complete the configuration are:

    
    This operation assumes that the provided partial configuration is valid in the sense that all
    features in the configuration are valid feature in the model.
    """

    def __init__(self) -> None:
        self.result: Configuration = None
        self.configuration: Configuration = None
        self.sat_model = None
        self.solver = None

    def set_configuration(self, configuration: Configuration) -> None:
        self.configuration = configuration

    def execute(self, model: VariabilityModel) -> 'CompleteConfiguration':
        sat_model = cast(PySATModel, model)
        self.result = self._complete_configuration(sat_model)
        return self

    def complete_configuration(self) -> Configuration:
        return self.get_result()

    def get_result(self) -> Configuration:
        return self.result

    def _complete_configuration(self, sat_model: PySATModel) -> Configuration:
        try:
            fm_model = cast(FeatureModel, sat_model.original_model)
        except FlamaException:
            LOGGER.exception("The transformation didn't attach the source model, " 
                             "which is required for this operation.")
        # For efficiency, reuse of model and solver
        if self.sat_model is None or self.sat_model != sat_model:
            self.sat_model = sat_model
            self.solver = Solver(name='glucose3')
            for clause in sat_model.get_all_clauses():
                self.solver.add_clause(clause)

        configuration = self.configuration
        # First check if the configuration is full
        assumptions = []
        for feature in sat_model.features.values():
            if configuration.elements.get(feature, False):
                assumptions.append(sat_model.variables[feature])
            else:
                assumptions.append(-sat_model.variables[feature])
                
        if not self.solver.solve(assumptions=assumptions):
            selected_elements = configuration.get_selected_elements()
            all_selected_elements = list(selected_elements)
            new_selected_elements = []
            for element in selected_elements:
                feature = fm_model.get_feature_by_name(element)
                parent = feature.get_parent()
                while parent is not None:
                    if parent not in all_selected_elements:
                        new_selected_elements.append(parent.name)
                        all_selected_elements.append(parent.name)
                        configuration.elements[parent.name] = True
                        assumptions.append(sat_model.variables[parent.name])
                        assumptions.remove(-sat_model.variables[parent.name])
                    parent = parent.get_parent()
                
        if not self.solver.solve(assumptions=assumptions):
            # Select children for each parent

                configuration = complete_configuration_with_parents(configuration, feature_model)
            



def complete_configuration_with_parents(configuration: Configuration, fm_model: FeatureModel) -> Configuration:
    configs_elements = dict(configuration.elements)
    for element in configuration.get_selected_elements():
        feature = fm_model.get_feature_by_name(element)
        configs_elements.update({parent: True for parent in get_all_parents(feature)})
    return Configuration(configs_elements)


def get_all_parents(feature: Feature) -> list[str]:
    parent = feature.get_parent()
    return [] if parent is None  else [parent.name] + get_all_parents(parent)

    

def check_satisfiability(configuration: Configuration, 
                         sat_model: PySATModel, 
                         solver: Solver) -> bool:
    assumptions = []
    for feature in sat_model.features.values():
        if configuration.elements.get(feature, False):
            assumptions.append(sat_model.variables[feature])
        else:
            assumptions.append(-sat_model.variables[feature])
    return solver.solve(assumptions=assumptions)