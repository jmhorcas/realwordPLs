import argparse

from flamapy.metamodels.fm_metamodel.transformations import UVLReader, UVLWriter
from flamapy.metamodels.fm_metamodel.operations import FMVariationPoints
from flamapy.metamodels.bdd_metamodel.transformations import FmToBDD
from flamapy.metamodels.bdd_metamodel.operations import BDDConfigurationsNumber, BDDSampling, BDDCoreFeatures
from flamapy.metamodels.pysat_metamodel.transformations import FmToPysat
from flamapy.metamodels.pysat_metamodel.operations import PySATSatisfiableConfiguration
from flamapy.metamodels.bdd_metamodel.operations import BDDSatisfiableConfiguration
from utils import (
    ConfigurationsCSVWriter, 
    ConfigurationsCSVReader, 
    ConfigurationsListWriter, 
    ConfigurationsListReader,
    ConfigurationsAttributesReader
)
from utils import utils
from flamapy.metamodels.productline_metamodel.models import ProductLineModel
from flamapy.metamodels.productline_metamodel.operations import (
    FullConfigurations,
    PLProductDistribution,
    PLFeatureInclusionFrequency,
    PLFeatureInclusionProbability
)


def main(fm_filepath: str) -> None:
    fm = UVLReader(fm_filepath).transform()

    print(f'#Features: {len(fm.get_features())}')
    print(f'#Constraints: {len(fm.get_constraints())}')
    print(fm)
    print(f'#Food with omega-3: {sum(attribute.name == 'Omega-3' for feature in fm.get_features() for attribute in feature.get_attributes())}')
    UVLWriter('mi-model.uvl', fm).transform()
    raise Exception

    sat_model = FmToPysat(fm).transform()
    bdd_model = FmToBDD(fm).transform()

    n_configs = BDDConfigurationsNumber().execute(bdd_model).get_result()
    print(f'#Configs: {utils.int_to_scientific_notation(n_configs)}')

    core_features = BDDCoreFeatures().execute(bdd_model).get_result()
    print(f'Core features: ({len(core_features)}) {core_features}')

    variation_points = FMVariationPoints().execute(fm).get_result()
    print(f'Variations points:')
    for vp, variant in variation_points.items():
        print(f'{vp} -> {variant}')

    sampling_op = BDDSampling()
    sampling_op.set_sample_size(5)
    sample = sampling_op.execute(bdd_model).get_result()
    configs_writer = ConfigurationsCSVWriter('configs.csv')
    configs_writer.set_elements([f.name for f in fm.get_features()])
    configs_writer.set_configurations(sample)
    configs_writer.transform()

    configs_reader = ConfigurationsCSVReader('configs.csv')
    configs_reader.store_only_selected_elements(False)
    sample2 = configs_reader.transform()
    print(f'Equals: {set(sample) == set(sample2)}')

    config_writer = ConfigurationsListWriter('configs.txt')
    config_writer.set_configurations(sample)
    config_writer.transform()

    configs_reader.store_only_selected_elements(True)
    sample3 = configs_reader.transform()
    sample4 = ConfigurationsListReader('configs.txt').transform()
    print(f'Equals: {set(sample3) == set(sample4)}')
    
    configs_attributes = ConfigurationsAttributesReader('models/NamasteRincon_configs_simple.csv').transform()
    print(f'#Products in portfolio: {len(configs_attributes)}')

    pl_model = ProductLineModel()
    pl_model.configurations = {config[0] for config in configs_attributes}
    print(pl_model)
    prod_dist_op = PLProductDistribution().execute(pl_model)
    prod_dist = prod_dist_op.get_result()
    desc_stats = prod_dist_op.descriptive_statistics()
    print(f'Product distribution: {prod_dist}')
    print(f'#Product dist: {sum(prod_dist)}')
    print(desc_stats)
    
    fif = PLFeatureInclusionFrequency().execute(pl_model).get_result()
    fif = dict(sorted(fif.items(), key=lambda item: item[1]))
    print(f'Feature Inclusion Frequency:\n')
    for feature, freq in fif.items():
        print(f'{feature}: {freq}')
    raise Exception
    
    for config_attr in configs_attributes:
        satis_config_op = BDDSatisfiableConfiguration()
        satis_config_op.set_configuration(config_attr[0], is_full=False)
        satis = satis_config_op.execute(bdd_model).get_result()
        print(f'{config_attr[0]} -> {satis}')
    
    print("full configurations:")
    false_configs = []
    full_configs = []
    for config_attr in configs_attributes:
        full_config_op = FullConfigurations()
        full_config_op.set_configuration(config_attr[0])
        new_configs = full_config_op.execute(sat_model).get_result()
        print(new_configs)
        full_configs.extend(new_configs)
        for config in new_configs:
            satis_config_op = BDDSatisfiableConfiguration()
            satis_config_op.set_configuration(config, is_full=True)
            satis = satis_config_op.execute(bdd_model).get_result()
            print(f'{config} -> {satis}')
            if not satis:
                false_configs.append((config_attr, config))
    config_writer = ConfigurationsListWriter('full_configs.txt')
    config_writer.set_configurations(full_configs)
    config_writer.transform()
    print(f'Invalid configs: {false_configs}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Product Line analysis.')
    parser.add_argument(metavar='fm', dest='fm_filepath', type=str, help='Input feature model (.uvl).')
    args = parser.parse_args()

    main(args.fm_filepath)
