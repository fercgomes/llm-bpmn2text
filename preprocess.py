import os
import json
import sys

import bpmn_python.bpmn_diagram_metrics as metrics
import bpmn_python.bpmn_diagram_rep as diagram

from xml.etree import ElementTree as ET

from transformers import GPT2Tokenizer

# as of 12/01/2024
openai_token_limits = {
    "gpt-4-1106-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4": 8192,
    "gpt-3-32k": 32768,
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo-instruct": 4096
}

# as of 12/01/2024, in USD
openai_pricing_per_1k_input_tokens = {
    "gpt-4-1106-preview": 0.01,
    "gpt-4-vision-preview": 0.01,
    "gpt-4": 0.03,
    "gpt-3-32k": 0.006,
    "gpt-3.5-turbo-1106": 0.001,
    "gpt-3.5-turbo-instruct": 0.0015
}


def tokenize(serialized_model):
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

    tokens = tokenizer.encode(serialized_model)

    return tokens


def get_token_count(tokens):
    return len(tokens)


def get_extra_metrics(serialized_model):

    # Parse as XML
    root = ET.fromstring(serialized_model)

    namespaces = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}

    # Get all bpmn:collaboration elements
    collaborations = root.findall(
        './/bpmn:participant', namespaces)

    num_pools = len(collaborations)

    # Get all bpmn:laneSet elements
    lanes = root.findall(
        './/bpmn:lane', namespaces)

    num_lanes = len(lanes)

    model_id = root.attrib['id']

    return num_pools, num_lanes, model_id


def annotate_dataset_dir(dataset_dir: str):
    # Get a list of directories within dataset_dir

    dirs = os.listdir(dataset_dir)

    total = len(dirs)  # M

    annotated_dataset = []

    for dir in dirs:
        test_path = os.path.join(dataset_dir, dir)
        # Get the only file with bpmn format using regex
        bpmn_files = [file for file in os.listdir(
            test_path) if file.endswith('.bpmn')]

        if len(bpmn_files) > 1 or len(bpmn_files) == 0:
            raise Exception(
                'Malformed dataset. Each test should have exactly one bpmn file.')

        bpmn_file = bpmn_files[0]

        serialized_model = open(os.path.join(test_path, bpmn_file), 'r').read()

        print(bpmn_file)

        bpmn_graph = diagram.BpmnDiagramGraph()
        bpmn_graph.load_diagram_from_xml_file(
            os.path.join(test_path, bpmn_file))

        activities_count = metrics.all_activities_count(bpmn_graph)         # A
        events_count = metrics.all_events_count(bpmn_graph)                 # E
        gateways_count = metrics.all_gateways_count(bpmn_graph)             # G
        type_activities_count = metrics.get_activities_counts(
            bpmn_graph)                                                     # TA
        type_events_count = metrics.get_events_counts(
            bpmn_graph)                                                     # TE
        type_gateways_count = metrics.get_gateway_counts(
            bpmn_graph)                                                     # TG
        cnc = metrics.CoefficientOfNetworkComplexity_metric(
            bpmn_graph)                                                     # CNC
        durfee = metrics.DurfeeSquare_metric(bpmn_graph)                    # D

        nodes_count = activities_count + events_count + gateways_count      # N

        sequence_flows_count = metrics.all_control_flow_elements_count(
            bpmn_graph)  # F

        # number of different symbols
        # ns = type_activities_count + type_events_count + type_gateways_count  # NS

        # P, L
        pools_count, lanes_count, model_id = get_extra_metrics(
            serialized_model)

        tokens = tokenize(serialized_model)
        tokens_count = get_token_count(tokens)

        characters_count = len(serialized_model)

        supported_chatgpt_models = []

        for model in openai_token_limits:
            if openai_token_limits[model] >= tokens_count:
                supported_chatgpt_models.append(model)

        chatgpt_model_pricings_usd = {
            model: openai_pricing_per_1k_input_tokens[model] * tokens_count / 1000 for model in supported_chatgpt_models
        }

        testcase = {
            "model_id": model_id,
            "serialized_model": serialized_model,
            "activities_count": activities_count,
            "events_count": events_count,
            "gateways_count": gateways_count,
            "type_activities_count": type_activities_count,
            "type_events_count": type_events_count,
            "type_gateways_count": type_gateways_count,
            "cnc": cnc,
            "durfee": durfee,
            "nodes_count": nodes_count,
            "sequence_flows_count": sequence_flows_count,
            "pools_count": pools_count,
            "lanes_count": lanes_count,
            "tokens_count": tokens_count,
            "characters_count": characters_count,
            "supported_chatgpt_models": supported_chatgpt_models,
            "chatgpt_model_pricings_usd": chatgpt_model_pricings_usd,
            "dir": test_path
        }

        annotated_dataset.append(testcase)

        # Save as testcase.json in the same directory
        with open(os.path.join(test_path, 'annotated_model.json'), 'w') as f:
            # With pretty printing
            serialized_json = json.dumps(testcase, indent=4)

            f.write(serialized_json)


def preprocess(dataset_dir: str):
    """
    Pre-processing phase of the experiment.

    - Prepare the dataset
    - For each model:
      - Tokenize the serialized model.
      - Calculate number of tokens.
      - Calculate number of flow objects, connecting objects and data objects.
    """

    print(f"Using dataset directory: {dataset_dir}")

    annotate_dataset_dir(dataset_dir)


def main():
    print('Pre-processing phase of the experiment.')

    if len(sys.argv) < 2:
        raise Exception('Dataset directory not specified.')

    # Get dataset dir from command line
    dataset_dir = sys.argv[1]

    if dataset_dir is None:
        raise Exception('Dataset directory not specified.')

    if not os.path.exists(dataset_dir):
        raise Exception('Dataset directory does not exist.')

    preprocess(dataset_dir)


if __name__ == '__main__':
    main()
