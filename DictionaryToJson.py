import json

json_str = '{"name": "Mohit", "age": 30}'
data = json.loads(json_str)

print(data["name"])