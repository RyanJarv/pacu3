import tinydb
import typer
from tinydb import where
import botocore
from rich import print
from rich.console import Console
from rich.columns import Columns

from pacu.aws.lib.boto import get_model, output_shape

console = Console(markup=False, highlighter=False)
app = typer.Typer()


#def list(svc: str = typer.Argument(None)):
@app.command()
def list(svc: str = typer.Argument(None)):
    db = tinydb.TinyDB('/tmp/test.db')

    if svc:
        for item in db.search(where('_svc') == svc):
            console.print(Columns(map(str, [item['_svc'], item['_shape'], *item['key']])))
    else:
        for item in db.all():
            try:
                console.print(Columns(map(str, [item['_svc'], item['_shape'], *item['key']])))
            except Exception as e:
                import pdb; pdb.set_trace()
                continue

# def shape_from_item(item):


# def get_id(item):
#     # shape = shape._shape_resolver.get_shape_by_name(shape.name).members
#     id = _get_id(item)
#     if not id:
#         return False
#
#
#
# def _get_id(item):
#     model = get_model(item['_svc'])
#     if type(item['_shape']) is list:
#         return item['value']
#     model.shape_for(item['_shape'])
#     shape = shape_from_item(item)
#     if shape.type_name == 'string':
#         return item['value']
#
#     if shape.type_name == 'map':
#         # TODO: remove when map handling in ingest is fixed
#         return item['value']
#     else:
#         try:
#             id_key, id_shape = shape.members.popitem(0)
#         except Exception as e:
#             print(e)
#             # import pdb; pdb.set_trace()
#             return
#
#         if id_shape.type_name == 'structure':
#             return '-'.join(item['value'].get(id_key, {}).values())
#         else:
#             try:
#                 if len(shape.members.keys()) == 0:
#                     # import pdb; pdb.set_trace()
#                     return
#             except Exception as e:
#                 print(e)
#                 # import pdb; pdb.set_trace()
#                 return
#             return item['value'][id_key]
#         # print(f"{item['_svc']}:{item['_op']}:{item['_shape']}: {shape.required_members}")
#         # exit(0)
#         # print_json(data=item['value'])
#
