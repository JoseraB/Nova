import json

file_path = "C:\\Users\\maxca\\Documents\\code\\Nova\\NeoCity-Data\\Neocity_Academy.json"

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

for idx, item in enumerate(data):
    content = item.get("content")
    if isinstance(content, dict):
        text = content.get("text", "[No text found]")
        if text == "[No text found]":
            text = content.get("pathway_description", "[No pathway description found]")
        if text == "[No pathway description found]":
            text = content.get("project_description", "[No project description found]")
        if text == "[No project description found]":
            text = content.get("pdf_url", "[No PDF URL found]")
        print(f"{idx}: {text}\n")
    else:
        print(f"{idx}: content is not a dict, it's a {type(content)}")
