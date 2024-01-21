from transformers import GPT2Tokenizer
import sys


def get_token_estimate(serialized_model: str) -> int:
    """
    Get the token estimate for a serialized model.
    """
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    tokens = tokenizer.encode(serialized_model)
    count = len(tokens)

    return count


def main():
    if len(sys.argv) < 2:
        raise Exception('Model path not specified.')

    model_path = sys.argv[1]

    with open(model_path, 'r') as f:
        serialized_model = f.read()

        token_estimate = get_token_estimate(serialized_model)

        print(f"Number of tokens in the BPMN model: {token_estimate}")


if __name__ == '__main__':
    main()
