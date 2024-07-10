from fastavro.schema import load_schema
parsed_schema = load_schema("./schemas/playlist2.avsc")

print(parsed_schema)