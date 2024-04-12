import tiktoken
import os


def tiktoken_len(string: str, encoding_name: str = 'cl100k_base') -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def load_json(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        json_str = file.read()
    return json_str


def dump_json(name: str, dir: str, json_str: str) -> None:
    file_name = f"{name}.json"
    counter = 1
    while os.path.exists(os.path.join(dir, file_name)):
        file_name = f"{name}_{counter}.json"
        counter += 1
    file_path = os.path.join(dir, file_name)
    with open(file_path, 'w') as file:
        file.write(json_str)
    print(f"Successfully dumped {file_name}.")
