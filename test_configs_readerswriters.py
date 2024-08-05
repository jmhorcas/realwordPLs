import argparse

from flamapy.metamodels.fm_metamodel.transformations import UVLReader
from flamapy.metamodels.bdd_metamodel.transformations import FmToBDD
from flamapy.metamodels.bdd_metamodel.operations import BDDConfigurationsNumber, BDDSampling
from utils import ConfigurationsCSVWriter, ConfigurationsCSVReader, ConfigurationsListWriter, ConfigurationsListReader


def main(fm_filepath: str) -> None:
    fm = UVLReader(fm_filepath).transform()

    print(f'#Features: {len(fm.get_features())}')
    print(f'#Constraints: {len(fm.get_constraints())}')

    bdd_model = FmToBDD(fm).transform()
    n_configs = BDDConfigurationsNumber().execute(bdd_model).get_result()
    print(f'#Configs: {n_configs}')

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
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Product Line analysis.')
    parser.add_argument(metavar='fm', dest='fm_filepath', type=str, help='Input feature model (.uvl).')
    args = parser.parse_args()

    main(args.fm_filepath)
