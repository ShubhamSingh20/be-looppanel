import os

def mock_search(query):
    # For now, we are using the example folder to mock the search, Passing the entire transcript as context
    print(f"\033[94m[MOCK SEARCH] {query}\033[0m")

    files = os.listdir("example")
    content = []

    for file in files:
        file_content = f"File: {file}\n"
        with open(f"example/{file}", "r") as f:
            file_content += f.read()

        if query in file_content:
            content.append(file_content)

    return "\n\n".join(content)
