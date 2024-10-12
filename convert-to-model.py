import json
from collections import defaultdict

# Function to convert snake_case to camelCase
def convert_to_camel_case(snake_str):
    snake_str = snake_str.replace('-', '_')  # Replace hyphens with underscores
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

# Function to map JSON types to Swift types
def map_json_type(value):
    if isinstance(value, bool):
        return 'Bool'
    elif isinstance(value, int):
        return 'Int'
    elif isinstance(value, float):
        return 'Double'
    elif isinstance(value, list):
        # Check if the list contains dictionaries (JSON objects)
        if len(value) > 0 and isinstance(value[0], dict):
            return '[SubModel]'  # Placeholder, will be replaced dynamically
        return '[String]'  # Assuming list of strings for simple case
    elif isinstance(value, dict):
        return 'SubModel'  # Placeholder, will be replaced dynamically
    return 'String'

# Recursive function to generate Swift structs from JSON
def generate_swift_structs(json_data, struct_name="RootModel"):
    merged_keys = defaultdict(lambda: None)
    additional_structs = []  # Store additional structs for nested objects

    for key, value in json_data.items():
        if isinstance(value, dict):  # Nested JSON object
            sub_struct_name = key.capitalize() + "Model"
            additional_structs.append(generate_swift_structs(value, sub_struct_name))
            merged_keys[key] = sub_struct_name
        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):  # List of JSON objects
            sub_struct_name = key.capitalize() + "Model"
            additional_structs.append(generate_swift_structs(value[0], sub_struct_name))
            merged_keys[key] = f'[{sub_struct_name}]'
        else:
            merged_keys[key] = map_json_type(value)

    swift_struct = f"public struct {struct_name}: Codable {{\n"
    coding_keys = "\n    enum CodingKeys: String, CodingKey {\n"

    for key, swift_type in merged_keys.items():
        swift_key = convert_to_camel_case(key)
        swift_struct += f"    let {swift_key}: {swift_type}?\n"  # Optional `?` for safety
        if swift_key != key:
            coding_keys += f"        case {swift_key} = \"{key}\"\n"
        else:
            coding_keys += f"        case {swift_key}\n"

    coding_keys += "    }\n"
    swift_struct += coding_keys + "}"

    # Combine current struct with any additional nested structs
    full_struct = swift_struct + "\n\n" + "\n\n".join(additional_structs)
    return full_struct

# Function to merge and generate Swift structs for the entire JSON list
def merge_json_keys_from_string(json_string):
    json_list = json.loads(json_string)

    # Start with generating structs for the first object
    swift_struct = generate_swift_structs(json_list[0])
    return swift_struct

# Sample input with nested JSON and lists of JSON
json_string = '''
[
    {
      "enabled": true,
      "example": {
        "nested": "value"
      },
    }
  ]
'''

# Generate Swift structs
merged_struct = merge_json_keys_from_string(json_string)
print(merged_struct)
