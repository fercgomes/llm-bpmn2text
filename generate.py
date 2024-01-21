import sys
import re
from uuid import uuid1
import json
import os

import dotenv
import os
import openai

dotenv.load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

# as of 12/01/2024, in USD
openai_pricing_per_1k_input_tokens = {
    "gpt-4-1106-preview": 0.01,
    "gpt-4-vision-preview": 0.01,
    "gpt-4": 0.03,
    "gpt-3-32k": 0.06,
    "gpt-3.5-turbo-1106": 0.001,
    "gpt-3.5-turbo-instruct": 0.0015
}


# as of 12/01/2024, in USD
openai_pricing_per_1k_output_tokens = {
    "gpt-4-1106-preview": 0.03,
    "gpt-4-vision-preview": 0.03,
    "gpt-4": 0.06,
    "gpt-3-32k": 0.12,
    "gpt-3.5-turbo-1106": 0.0020,
    "gpt-3.5-turbo-instruct": 0.0020
}


def read_experiment_parameters(metadata_path):

    if not os.path.exists(metadata_path):
        raise Exception('Metadata file not found.')

    testcases = []

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

        chatgpt_models = metadata['chatgpt_models']
        temperatures = metadata['temperatures']
        annotated_dataset_dir = metadata['annotated_dataset_dir']
        prompts_dir = metadata['prompts_dir']

        dataset_name = annotated_dataset_dir.split('/')[-1]

        # Read annotated models
        annotated_models = []

        # List all folders within dataset dir
        dirs = os.listdir(annotated_dataset_dir)

        for dir in dirs:
            test_path = os.path.join(annotated_dataset_dir, dir)

            annotated_model_path = os.path.join(
                test_path, 'annotated_model.json')

            data = json.load(open(annotated_model_path, 'r'))

            annotated_models.append(data)

        # Read prompts
        prompts = []

        # List all txt files in prompts dir
        prompt_txt_files = [file for file in os.listdir(
            prompts_dir) if file.endswith('.txt')]

        for prompt_name in prompt_txt_files:
            prompt_data = open(os.path.join(
                prompts_dir, prompt_name), 'r').read()

            item = (prompt_name, prompt_data)

            prompts.append(item)

        # Prepare testcases
        for model in annotated_models:
            model_id = model['model_id']
            serialized_model = model['serialized_model']
            activities_count = model['activities_count']
            gateways_count = model['gateways_count']
            events_count = model['events_count']
            type_activities_count = model['type_activities_count']
            type_gateways_count = model['type_gateways_count']
            type_events_count = model['type_events_count']
            cnc = model['cnc']
            durfee = model['durfee']
            nodes_count = model['nodes_count']
            sequence_flows_count = model['sequence_flows_count']
            pools_count = model['pools_count']
            lanes_count = model['lanes_count']
            tokens_count = model['tokens_count']
            characters_count = model['characters_count']
            supported_chatgpt_models = model['supported_chatgpt_models']
            chatgpt_model_pricings_usd = model['chatgpt_model_pricings_usd']

            directory = model['dir']

            for (prompt_name, prompt_data) in prompts:

                for temperature in temperatures:
                    for chatgpt_model in chatgpt_models:
                        testcase = {
                            "model_id": model_id,
                            "dataset_name": dataset_name,
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
                            "prompt_name": prompt_name,
                            "prompt_data": prompt_data,
                            "temperature": temperature,
                            "chatgpt_model": chatgpt_model,
                            "supported_chatgpt_models": supported_chatgpt_models,
                            "chatgpt_model_pricings_usd": chatgpt_model_pricings_usd,
                            "dir": directory
                        }

                        testcases.append(testcase)
    return testcases


def generate(serialized_model, prompt, temperature, seed, chatgpt_model):
    print(f"Generating with chatgpt_model {chatgpt_model}")
    completion = openai.ChatCompletion.create(model=chatgpt_model,
                                              temperature=temperature,
                                              seed=seed,
                                              messages=[
                                                  {
                                                      "role": "system",
                                                      "content": prompt
                                                  }, {
                                                      "role": "user",
                                                      "content": serialized_model
                                                  }
                                              ])

    description = completion.choices[0].message.content
    usage = completion.usage

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    # Estimate billing

    billed_prompt_tokens = prompt_tokens * \
        openai_pricing_per_1k_input_tokens[chatgpt_model] / 1000
    billed_completion_tokens = completion_tokens * \
        openai_pricing_per_1k_output_tokens[chatgpt_model] / 1000

    billed_estimate = billed_prompt_tokens + billed_completion_tokens

    return description, prompt_tokens, completion_tokens, total_tokens, billed_estimate


def main():
    print('Generation phase of the experiment.')

    if len(sys.argv) < 2:
        raise Exception('Parameters metadata not specified.')

    # Get dataset dir from command line
    parameters_metadata_path = sys.argv[1]

    if parameters_metadata_path is None:
        raise Exception('Parameters metadata not specified.')

    if not os.path.exists(parameters_metadata_path):
        raise Exception('Parameters metadata does not exist.')

    testcases = read_experiment_parameters(parameters_metadata_path)

    print(f"Generated {len(testcases)} testcases.")

    for testcase in testcases:
        print(f"Generating testcase {testcase['model_id']}")
        print(
            f"Parameters: chatgpt_model={testcase['chatgpt_model']}, temperature={testcase['temperature']}")

        serialized_model = testcase['serialized_model']
        prompt_name = testcase['prompt_name']
        prompt = testcase['prompt_data']
        temperature = testcase['temperature']
        chatgpt_model = testcase['chatgpt_model']
        seed = 123

        description, prompt_tokens, completion_tokens, total_tokens, billed_estimate = generate(
            serialized_model, prompt, temperature, seed, chatgpt_model)

        parameters = {
            "model_id": testcase['model_id'],
            "dataset_name": testcase['dataset_name'],
            "prompt": prompt,
            "temperature": temperature,
            "chatgpt_model": chatgpt_model,
            "seed": seed,
            "prompt_name": prompt_name
        }

        result = {}

        result['generated_description'] = description
        result['real_prompt_tokens'] = prompt_tokens
        result['real_completion_tokens'] = completion_tokens
        result['real_total_tokens'] = total_tokens
        result['billed_estimate'] = billed_estimate

        testcase_uid = str(uuid1()).split('-')[0]

        parameters['uid'] = testcase_uid

        save_dir = os.path.join(
            "results", testcase["dataset_name"], testcase_uid)

        # Check folder exists
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # Save results
        save_path = os.path.join(save_dir, 'generation_result.json')
        with open(save_path, 'w') as fp:
            # With pretty printing
            serialized_json = json.dumps(result, indent=4)

            fp.write(serialized_json)

        print(f"Generated result in {save_path}")

        # Save description as txt
        save_path = os.path.join(save_dir, 'generated_description.txt')

        with open(save_path, 'w') as fp:
            fp.write(description)

        # Also save the txt description in a folder within the dataset folder, name is the uid
        alternative_save_path = os.path.join(
            "results", testcase['dataset_name'], 'descriptions', f"desc_{testcase_uid}.txt")

        # Check folder exists
        if not os.path.exists(os.path.dirname(alternative_save_path)):
            os.makedirs(os.path.dirname(alternative_save_path))

        with open(alternative_save_path, 'w') as fp:
            fp.write(description)

        # Copy annotated model to results folder
        annotated_model_path = os.path.join(
            testcase['dir'], 'annotated_model.json')

        save_path = os.path.join(save_dir, 'annotated_model.json')

        with open(annotated_model_path, 'r') as fp:
            annotated_model = json.load(fp)

            with open(save_path, 'w') as fp:
                serialized_json = json.dumps(annotated_model, indent=4)

                fp.write(serialized_json)

        # Save parameters in the testcase folder
        save_path = os.path.join(save_dir, 'parameters.json')

        with open(save_path, 'w') as fp:
            serialized_json = json.dumps(parameters, indent=4)

            fp.write(serialized_json)


if __name__ == '__main__':
    main()
