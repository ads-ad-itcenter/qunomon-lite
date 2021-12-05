from typing import Dict, List, Union

from rich import box
from rich.table import Table
from rich.tree import Tree


def tree_for_dict(
    tree: Tree,
    dict_obj: Dict[str, Union[str, dict]],
) -> None:
    for k, v in dict_obj.items():
        if isinstance(v, dict):
            node = tree.add("[bold]%s[/]" % k)
            tree_for_dict(node, v)
        else:
            node = tree.add("[bold]%s[/]: %s" % (k, v))


def table_for_list_of_dict(
    list_of_dict_obj: List[dict],
) -> Table:
    table = Table(
        show_edge=False,
        show_header=True,
        expand=False,
        box=box.SIMPLE,
    )
    keys = list({k: None for d in list_of_dict_obj for k in d})
    for i, k in enumerate(keys):
        if i == 0:
            table.add_column(k, no_wrap=True, justify="center")
        else:
            table.add_column(k, overflow="fold")
    for d in list_of_dict_obj:
        cells = []
        for k in keys:
            cells.append(d.get(k))
        table.add_row(*cells)
    return table
