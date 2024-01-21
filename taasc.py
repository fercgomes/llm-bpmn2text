import sys
import re
import json
import os
import csv


def process_taasc_results(results_dir):
    print("Processing TAASC results in directory: " + results_dir)

    # Read the taasc results csv
    base_path = os.path.join(results_dir, 'descriptions')
    csv_path = os.path.join(base_path, 'taasc_results.csv')

    if not os.path.exists(csv_path):
        raise Exception('TAASC results csv does not exist.')

    results_dict = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            filename = row['filename']
            testcase_uid = filename.split('.')[0].split('_')[1]

            if testcase_uid not in results_dict:
                results_dict[testcase_uid] = {}

            # put all other keys
            for key in row.keys():
                if key != 'filename':
                    results_dict[testcase_uid][key] = float(row[key])

            # Save the results in the testcase folder
            testcase_path = os.path.join(results_dir, testcase_uid)
            testcase_json_path = os.path.join(
                testcase_path, 'taasc_results.json')

            with open(testcase_json_path, 'w') as f:
                serialized_json = json.dumps(
                    results_dict[testcase_uid], indent=4)
                f.write(serialized_json)

    csv_path = os.path.join(base_path, 'taasc_results_sca.csv')

    if not os.path.exists(csv_path):
        raise Exception('TAASC results csv does not exist.')

    sca_results_dict = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            filename = row['filename']

            # UID Regex: C:\Users\Fernando\AppData\Local\Temp\_MEI13~1\sca_parsed_files\desc_0202680c.txt
            testcase_uid = re.search(r'desc_(\w+)\.txt', filename).group(1)

            if testcase_uid not in sca_results_dict:
                sca_results_dict[testcase_uid] = {}

            # put all other keys
            for key in row.keys():
                if key != 'filename':
                    sca_results_dict[testcase_uid][key] = float(row[key])

            # Save the results in the testcase folder
            testcase_path = os.path.join(results_dir, testcase_uid)
            testcase_json_path = os.path.join(
                testcase_path, 'taasc_results_sca.json')

            with open(testcase_json_path, 'w') as f:
                serialized_json = json.dumps(
                    sca_results_dict[testcase_uid], indent=4)
                f.write(serialized_json)

    csv_path = os.path.join(base_path, 'taasc_results_components.csv')

    if not os.path.exists(csv_path):
        raise Exception('TAASC results csv does not exist.')

    components_results_dict = {}

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            filename = row['filename']

            # UID Regex: C:\Users\Fernando\AppData\Local\Temp\_MEI13~1\sca_parsed_files\desc_0202680c.txt
            testcase_uid = re.search(r'desc_(\w+)\.txt', filename).group(1)

            if testcase_uid not in components_results_dict:
                components_results_dict[testcase_uid] = {}

            # put all other keys
            for key in row.keys():
                if key != 'filename':
                    components_results_dict[testcase_uid][key] = float(
                        row[key])

            # Save the results in the testcase folder
            testcase_path = os.path.join(results_dir, testcase_uid)
            testcase_json_path = os.path.join(
                testcase_path, 'taasc_results_components.json')

            with open(testcase_json_path, 'w') as f:
                serialized_json = json.dumps(
                    components_results_dict[testcase_uid], indent=4)
                f.write(serialized_json)


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

    process_taasc_results(dataset_dir)


if __name__ == '__main__':
    main()
