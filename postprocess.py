import sys
import json
import os
import csv


def read_annonated_model(results_dir):
    path = os.path.join(results_dir, 'annotated_model.json')

    if not os.path.exists(path):
        raise Exception('Annonated model file does not exist.')

    with open(path, 'r') as f:
        data = json.load(f)

        # flatten "type_activities_count"
        type_activities_count = data['type_activities_count']

        for type, activities_count in type_activities_count.items():
            data['type_activities_count_' + type] = activities_count

        # exclude "type_activities_count"
        del data['type_activities_count']

        # flatten type_events_count
        type_events_count = data['type_events_count']

        for type, events_count in type_events_count.items():
            data['type_events_count_' + type] = events_count

        # exclude "type_events_count"
        del data['type_events_count']

        # flatten type_gateways_count
        type_gateways_count = data['type_gateways_count']

        for type, gateways_count in type_gateways_count.items():
            data['type_gateways_count_' + type] = gateways_count

        # exclude "type_gateways_count"
        del data['type_gateways_count']

        return data


def read_basic_eval(results_dir):
    path = os.path.join(results_dir, 'basic_eval.json')

    if not os.path.exists(path):
        raise Exception('Basic eval file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def read_parameters(results_dir):
    path = os.path.join(results_dir, 'parameters.json')

    if not os.path.exists(path):
        raise Exception('Parameters file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def read_generation_result(results_dir):
    path = os.path.join(results_dir, 'generation_result.json')

    if not os.path.exists(path):
        raise Exception('Generation result file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def read_taasc_result(results_dir):
    path = os.path.join(results_dir, 'taasc_results.json')

    if not os.path.exists(path):
        raise Exception('TAASC results file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def read_taasc_sca_result(results_dir):
    path = os.path.join(results_dir, 'taasc_results_sca.json')

    if not os.path.exists(path):
        raise Exception('TAASC SCA results file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def read_taasc_components_result(results_dir):
    path = os.path.join(results_dir, 'taasc_results_components.json')

    if not os.path.exists(path):
        raise Exception('TAASC Components results file does not exist.')

    with open(path, 'r') as f:
        return json.load(f)


def postprocess(base_results_dir):

    # read all folders
    folders = [f for f in os.listdir(base_results_dir) if os.path.isdir(
        os.path.join(base_results_dir, f))]

    # exclude "descriptiosn"
    folders = [f for f in folders if f != 'descriptions']

    results = []

    for uid in folders:
        results_dir = os.path.join(base_results_dir, uid)
        print(results_dir)

        # read annonated model
        annonated_model = read_annonated_model(results_dir)

        # read parameters
        parameters = read_parameters(results_dir)

        # read generation result
        generation_result = read_generation_result(results_dir)

        # read taasc result
        taasc_result = read_taasc_result(results_dir)

        # read taasc sca result
        taasc_sca_result = read_taasc_sca_result(results_dir)

        # read taasc components result
        taasc_components_result = read_taasc_components_result(results_dir)

        # read basic eval
        basic_eval = read_basic_eval(results_dir)

        # flatten out
        result = {
            'uid': uid,
            "dataset": parameters['dataset_name'],
            "model_id": parameters['model_id'],
            "chatgpt_model": parameters['chatgpt_model'],
            "temperature": parameters['temperature'],
            "prompt_name": parameters['prompt_name'],
            "seed": parameters['seed'],

            # flatten basic eval
            **basic_eval,

            # flatten annonated model, excluding "model_id", and "serialized_model"
            **{"md_" + k: v for k, v in annonated_model.items() if k != 'model_id' and k != 'serialized_model' and k != 'supported_chatgpt_models' and k != 'chatgpt_model_pricings_usd'},

            # flatten generation result with a prefix, hiding "generated_description"
            **{'genres_' + k: v for k, v in generation_result.items() if k != 'generated_description'},

            # flatten taasc result with a prefix
            **{'taasc_' + k: v for k, v in taasc_result.items()},

            # flatten taasc sca result with a prefix
            **{'taasc_sca_' + k: v for k, v in taasc_sca_result.items()},

            # flatten taasc components result with a prefix
            **{'taasc_components_' + k: v for k, v in taasc_components_result.items()}
        }

        results.append(result)

    # write to csv
    csv_path = os.path.join(base_results_dir, 'final_results.csv')

    with open(csv_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()

        for result in results:
            writer.writerow(result)


def main():
    print('Pre-processing phase of the experiment.')

    if len(sys.argv) < 2:
        raise Exception('Results directory not specified.')

    # Get dataset dir from command line
    dataset_dir = sys.argv[1]

    if dataset_dir is None:
        raise Exception('Results directory not specified.')

    if not os.path.exists(dataset_dir):
        raise Exception('Results directory does not exist.')

    postprocess(dataset_dir)


if __name__ == '__main__':
    main()
