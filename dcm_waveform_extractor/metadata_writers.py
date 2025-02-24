import os
import json
import yaml
from collections import OrderedDict

def represent_ordereddict(dumper, data):
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

yaml.add_representer(OrderedDict, represent_ordereddict)

def store_yaml(data:dict,path:str) -> bool:
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path),exist_ok=True)
        
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=4)

    except Exception as e:
        print(e)
        raise(e)
    return True


def store_json(data:dict,path:str) -> bool:
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path),exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        print(e)
        raise(e)
    return True