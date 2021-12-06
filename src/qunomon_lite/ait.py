import datetime
import pathlib
import secrets
from typing import Dict

from rich.console import Console, Group
from rich.tree import Tree

from . import ait_core, print_helper

console = Console()

OUTPUT_ROOT_DIR_PATH = pathlib.Path("qunomon_lite_outputs")


class Result:
    def __init__(
        self,
        run_id: str,
        core: ait_core.Result,
    ) -> None:
        self.run_id = run_id
        self.core = core

    @classmethod
    def from_core(
        cls,
        core: ait_core.Result,
    ):
        return cls(
            run_id=core.output_base_dir_path.name,
            core=core,
        )

    @classmethod
    def from_run_id(
        cls,
        run_id: str,
    ):
        return cls.from_core(
            ait_core.Result(
                output_base_dir_path=OUTPUT_ROOT_DIR_PATH / run_id,
            )
        )

    @classmethod
    def _latest_run_id(cls) -> str:
        run_dirname_list = [
            p.name for p in OUTPUT_ROOT_DIR_PATH.iterdir() if p.is_dir()
        ]
        return sorted(run_dirname_list)[-1]

    @classmethod
    def from_latest_run(cls):
        return cls.from_run_id(cls._latest_run_id())

    def show(self) -> None:
        ait_output = self.core.ait_output_json_dict

        tree = Tree("[bold red]%s" % str(self.core.ait_output_json_path))

        print_helper.tree_for_dict(tree.add("[bold]AIT[/]"), ait_output.get("AIT", {}))
        print_helper.tree_for_dict(
            tree.add("[bold]ExecuteInfo[/]"), ait_output.get("ExecuteInfo", {})
        )
        node_result = tree.add("[bold]Result[/]")
        node_result.add(
            Group(
                "[bold]Measures[/]",
                print_helper.table_for_list_of_dict(
                    ait_output.get("Result", {}).get("Measures", [])
                ),
            )
        )
        node_result.add(
            Group(
                "[bold]Resources[/]",
                print_helper.table_for_list_of_dict(
                    ait_output.get("Result", {}).get("Resources", [])
                ),
            )
        )
        node_result.add(
            Group(
                "[bold]Downloads[/]",
                print_helper.table_for_list_of_dict(
                    ait_output.get("Result", {}).get("Downloads", [])
                ),
            )
        )
        console.print(tree)


def result(
    run_id: str = "latest",
) -> Result:
    if run_id == "latest":
        return Result.from_latest_run()
    return Result.from_run_id(run_id)


def _generate_run_id() -> str:
    # ex) '20210709-090432-981577_81b4fb44ed'
    return "%s_%s" % (
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
        secrets.token_hex(5),
    )


def run(
    ait: str,
    *,
    inventories: Dict[str, str] = {},
    params: Dict[str, str] = {},
) -> Result:

    console.print("AIT: %s" % ait)
    console.print("inventories: ", inventories)
    console.print("params: ", params)

    # ex) '20210709-090432-981577_81b4fb44ed'
    run_id = _generate_run_id()

    output_base_dir_path = OUTPUT_ROOT_DIR_PATH / run_id
    console.print("Output directory: ", output_base_dir_path)

    result: Result

    with console.status("[bold green]Working on AIT running..."):
        _result = ait_core.Runner(
            ait=ait_core.Ait.from_image_name(ait),
            inventories=inventories,
            params=params,
        ).run(
            output_base_dir_path=output_base_dir_path,
        )
        result = Result.from_core(_result)

    console.print("[bold]Finished! run-id: [red]", run_id)
    console.print(
        "See output directory for results: ", result.core.output_base_dir_path
    )

    return result
