
import sys
import json
import os
import csv
import nltk

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag

nltk.download('punkt')


def evaluate(base_results_dir):

    # read all folders
    folders = [f for f in os.listdir(base_results_dir) if os.path.isdir(
        os.path.join(base_results_dir, f))]

    # exclude "descriptiosn"
    folders = [f for f in folders if f != 'descriptions']

    results = []

    for uid in folders:
        results_dir = os.path.join(base_results_dir, uid)

        # read the generate description
        description_file = os.path.join(
            results_dir, 'generated_description.txt')

        if not os.path.exists(description_file):
            raise Exception('description file does not exist.')

        with open(description_file, 'r') as f:
            description = f.read()

            sentences = sent_tokenize(description)
            words = word_tokenize(description)

            sent_count = len(sentences)
            word_count = len(words)

            # save to basic

            save_path = os.path.join(results_dir, 'basic_eval.json')

            with open(save_path, 'w') as f:
                json.dump({
                    'sent_count': sent_count,
                    'word_count': word_count
                }, f)


def main():
    print('Basic evaluation phase of the experiment.')

    if len(sys.argv) < 2:
        raise Exception('directory not specified.')

    # Get dataset dir from command line
    dataset_dir = sys.argv[1]

    if dataset_dir is None:
        raise Exception('directory not specified.')

    if not os.path.exists(dataset_dir):
        raise Exception('directory does not exist.')

    evaluate(dataset_dir)


if __name__ == '__main__':
    main()
