import json
from typing import Union, cast
from tinydb import TinyDB, Query

import typer
from pathlib import Path


# def set(key: str, value: any):
#     (Path(typer.get_app_dir('pacu')) / 'config' / key).write_text(json.dumps(value))
#
#
# def append(key: str, value: any):
#     obj = get(key)
#
#     if obj is None:
#         obj = []
#     elif type(obj) is list:
#         raise TypeError(f"existing configuration on disk is of type '{type(obj)}', expected a list.")
#     else:
#         obj = cast(list, obj)
#
#     set(key, obj.append(value))
#
#
# def get(key: str) -> any:
#     try:
#         return json.loads(Path(typer.get_app_dir('pacu')/'config'/ key).read_text())
#     except FileNotFoundError:
#         return None
#
# def config():
#     return TinyDB(Path(typer.get_app_dir('pacu')/'config'))

def resources():
    return TinyDB(Path(typer.get_app_dir('pacu'))/'resources')
