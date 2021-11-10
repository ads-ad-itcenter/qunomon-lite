import pathlib
import json
from qunomon_lite import print_helper
from rich.console import Console, Group
from rich.tree import Tree


class AitOutput:
    def __init__(self, ait_output_json_path: pathlib.Path):
        self.file_path = ait_output_json_path
        self.dict = json.loads(ait_output_json_path.read_bytes())

    def print(self) -> None:
        console = Console()

        tree = Tree("[bold red]%s" % str(self.file_path))

        print_helper.tree_for_dict(tree.add("[bold]AIT[/]"), self.dict.get("AIT", {}))
        print_helper.tree_for_dict(
            tree.add("[bold]ExecuteInfo[/]"), self.dict.get("ExecuteInfo", {})
        )
        node_result = tree.add("[bold]Result[/]")
        node_result.add(
            Group(
                "[bold]Measures[/]",
                print_helper.table_for_list_of_dict(
                    self.dict.get("Result", {}).get("Measures", [])
                ),
            )
        )
        node_result.add(
            Group(
                "[bold]Resources[/]",
                print_helper.table_for_list_of_dict(
                    self.dict.get("Result", {}).get("Resources", [])
                ),
            )
        )
        node_result.add(
            Group(
                "[bold]Downloads[/]",
                print_helper.table_for_list_of_dict(
                    self.dict.get("Result", {}).get("Downloads", [])
                ),
            )
        )
        console.print(tree)


class Result:
    def __init__(self, ait_output_dir_path: pathlib.Path):
        self.dir_path = ait_output_dir_path
        self.ait_output = AitOutput(self.dir_path / "ait.output.json")

    def show(self) -> None:
        self.ait_output.print()


if __name__ == "__main__":
    # ait_output = AitOutput(pathlib.Path("tests/data/output1/ait.output.json"))
    # ait_output.print()
    result = Result(pathlib.Path("tests/data/output1/"))
    result.show()
