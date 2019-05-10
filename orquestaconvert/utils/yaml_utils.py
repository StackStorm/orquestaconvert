import ruamel.yaml
import ruamel.yaml.comments
import six
import yaml
import yamlloader


def yaml_to_obj(stream):
    return yaml.load(stream, Loader=yamlloader.ordereddict.CSafeLoader)


def read_yaml(yaml_filename):
    # parse data in a format that preserves ordering
    with open(yaml_filename, 'r') as stream:
        # safe load with ordered dicts
        ruamel_data = ruamel.yaml.round_trip_load(stream)

    # parse YAML into a dict
    with open(yaml_filename, 'r') as stream:
        data = yaml_to_obj(stream)

    return (data, ruamel_data)


def obj_to_yaml(obj, indent=2):
    # use this different library because PyYAML doesn't handle indenting properly
    # rt = round-trip
    ruyaml = ruamel.yaml.YAML(typ='rt')
    ruyaml.explicit_start = True
    # this crazyness basically sets indents to 'indent'
    # 'sequence' is always supposed to be 'offset' + 2
    ruyaml.indent(mapping=indent, sequence=(indent + 2), offset=indent)
    # prevent line-wrap
    ruyaml.width = 99999999999
    stream = six.StringIO()
    ruyaml.dump(obj, stream)
    return stream.getvalue()
