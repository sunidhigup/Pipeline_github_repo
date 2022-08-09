from jsonschema import validate
import jsonschema


def validateJson(jsonData,Schema):
    try:
        validate(instance=jsonData, schema=Schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True





