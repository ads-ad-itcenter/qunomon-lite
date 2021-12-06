import pathlib
import re
import sys
import textwrap
from typing import List

import docker
import pytest
from pytest_mock import MockerFixture
from rich.console import Console

from qunomon_lite import ait, ait_core, cli


def _dedent(heredoc: str) -> str:
    return textwrap.dedent(heredoc)[1:-1]


class TestMainCommand:

    MESSAGE_FOR_USAGE = _dedent(
        """
        usage: qunomon-lite [-h] {run,result-show} ...

        positional arguments:
          {run,result-show}
            run              see `run -h`
            result-show      see `run -h`

        optional arguments:
          -h, --help         show this help message and exit

        """
    )
    if sys.version_info >= (3, 10):
        MESSAGE_FOR_USAGE = _dedent(
            """
            usage: qunomon-lite [-h] {run,result-show} ...

            positional arguments:
              {run,result-show}
                run              see `run -h`
                result-show      see `run -h`

            options:
              -h, --help         show this help message and exit

            """
        )

    def test_main(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite"],
        )

        cli.main()

        cap = capsys.readouterr()
        assert cap.out == self.MESSAGE_FOR_USAGE
        assert cap.err == ""

    @pytest.mark.parametrize(
        "args",
        [
            (["-h"]),
            (["--help"]),
        ],
    )
    def test_main_help(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 0

        cap = capsys.readouterr()
        assert cap.out == self.MESSAGE_FOR_USAGE
        assert cap.err == ""

    @pytest.mark.parametrize(
        "args,err_msg",
        [
            (["dummy"], "invalid choice: 'dummy' (choose from 'run', 'result-show')"),
            (["--dummy"], "unrecognized arguments: --dummy"),
            (["-d"], "unrecognized arguments: -d"),
        ],
    )
    def test_main_invalid_args(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
        err_msg: str,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 2

        cap = capsys.readouterr()
        assert cap.out == ""
        assert "usage: qunomon-lite [-h] {run,result-show} ..." in cap.err
        assert err_msg in cap.err


class TestSubCommandForRun:

    MESSAGE_FOR_USAGE = _dedent(
        """
        usage: qunomon-lite run [-h] [--inventories [INVENTORIES [INVENTORIES ...]]]
                                [--params [PARAMS [PARAMS ...]]]
                                ait

        positional arguments:
          ait

        optional arguments:
          -h, --help            show this help message and exit
          --inventories [INVENTORIES [INVENTORIES ...]]
          --params [PARAMS [PARAMS ...]]

        """
    )
    if sys.version_info >= (3, 10):
        MESSAGE_FOR_USAGE = _dedent(
            """
            usage: qunomon-lite run [-h] [--inventories [INVENTORIES ...]]
                                    [--params [PARAMS ...]]
                                    ait

            positional arguments:
              ait

            options:
              -h, --help            show this help message and exit
              --inventories [INVENTORIES ...]
              --params [PARAMS ...]

            """
        )

    @pytest.mark.parametrize(
        "args",
        [
            (["run", "-h"]),
            (["run", "--help"]),
        ],
    )
    def test_main_help(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 0

        cap = capsys.readouterr()
        assert cap.out == self.MESSAGE_FOR_USAGE
        assert cap.err == ""

    @pytest.mark.parametrize(
        "args,err_msg",
        [
            (
                ["run", "--dummy"],
                "the following arguments are required: ait",
            ),
            (
                ["run", "-d"],
                "the following arguments are required: ait",
            ),
        ],
    )
    def test_main_invalid_args(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
        err_msg: str,
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 2

        cap = capsys.readouterr()
        assert cap.out == ""
        assert "usage: qunomon-lite run [-h] [--inventories [INVENTORIES " in cap.err
        assert "[--params [PARAMS " in cap.err
        assert err_msg in cap.err

    def test_main_run(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        tmp_path: pathlib.Path,
        ait_stub: str,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", "run", ait_stub],
        )

        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)

        cli.main()
        cap = capsys.readouterr()
        assert (
            "Running docker container (image: qunomon-lite/ait-stub:latest)" in cap.out
        )
        assert "Finished! run-id: " in cap.out
        assert cap.err == ""

    def test_main_run_full_option(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        tmp_path: pathlib.Path,
        shared_datadir: pathlib.Path,
        ait_stub: str,
    ):

        mocker.patch.object(
            sys,
            "argv",
            [
                "qunomon-lite",
                "run",
                ait_stub,
                "--inventories",
                "inventory_sample=%s" % str(shared_datadir.resolve() / "sample.txt"),
                "--params",
                "p1=ppp1",
            ],
        )

        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)
        mocker.patch.object(ait, "_generate_run_id", return_value="run-id")

        cli.main()
        cap = capsys.readouterr()
        assert (
            "Running docker container (image: qunomon-lite/ait-stub:latest)" in cap.out
        )
        assert "Finished! run-id:  %s" % "run-id" in cap.out
        assert (
            "See output directory for results:  \n%s"
            % str(tmp_path.resolve() / "run-id")
            in cap.out
        )
        assert cap.err == ""
        ait_input_json_expected = {
            "testbed_mount_volume_path": "/usr/local/qai/mnt",
            "job_id": "-",
            "run_id": "-",
            "Inventories": [
                {
                    "Name": "inventory_sample",
                    "Value": "/usr/local/qai/inventory/sample.txt",
                },
            ],
            "MethodParams": [
                {"Name": "p1", "Value": "ppp1"},
            ],
        }
        assert (
            ait_core._load_json_file(tmp_path / "run-id/ait.input.json")
            == ait_input_json_expected
        )

    def test_main_run_execution_error(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        tmp_path: pathlib.Path,
        ait_stub_for_err: str,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", "run", ait_stub_for_err],
        )

        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 1

        cap = capsys.readouterr()
        assert (
            "Running docker container (image: qunomon-lite/ait-stub-for-err:latest)"
            in cap.out
        )
        assert "Finished! run-id: " not in cap.out

        assert (
            "AIT docker container running succeeded, "
            + "but AIT execution error occured. "
            + "Error Code: E901, Error Detail: Traceback (most recent call last):"
            in cap.err
        )

    def test_main_run_docker_error(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        tmp_path: pathlib.Path,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", "run", "repo/name:ver"],
        )

        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)
        mocker.patch.object(
            ait_core.Runner,
            "_docker_run",
            side_effect=docker.errors.APIError("dummy docker api error"),
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 1

        cap = capsys.readouterr()
        assert "Running docker container (image: repo/name:ver)" in cap.out
        assert "Finished! run-id: " not in cap.out

        assert "dummy docker api error" in cap.err


class TestSubCommandForResultShow:

    MESSAGE_FOR_USAGE = _dedent(
        """
        usage: qunomon-lite result-show [-h] run_id

        positional arguments:
          run_id

        optional arguments:
          -h, --help  show this help message and exit

        """
    )
    if sys.version_info >= (3, 10):
        MESSAGE_FOR_USAGE = _dedent(
            """
            usage: qunomon-lite result-show [-h] run_id

            positional arguments:
              run_id

            options:
              -h, --help  show this help message and exit

            """
        )

    @pytest.mark.parametrize(
        "args",
        [
            (["result-show", "-h"]),
            (["result-show", "--help"]),
        ],
    )
    def test_main_help(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 0

        cap = capsys.readouterr()
        assert cap.out == self.MESSAGE_FOR_USAGE
        assert cap.err == ""

    @pytest.mark.parametrize(
        "args,err_msg",
        [
            (
                ["result-show", "--dummy"],
                "the following arguments are required: run_id",
            ),
            (
                ["result-show", "-d"],
                "the following arguments are required: run_id",
            ),
        ],
    )
    def test_main_invalid_args(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        args: List[str],
        err_msg: str,
    ):
        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", *args],
        )

        with pytest.raises(SystemExit) as e:
            cli.main()

        assert e.value.code == 2

        cap = capsys.readouterr()
        assert cap.out == ""
        assert cap.err == _dedent(
            """
            usage: qunomon-lite result-show [-h] run_id
            qunomon-lite result-show: error: %s

            """
            % err_msg
        )

    def test_main_result_show(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        shared_datadir: pathlib.Path,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", "result-show", "latest"],
        )

        mocker.patch.object(ait, "console", Console(width=10000))
        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", shared_datadir / "output_dirs")

        cli.main()

        cap = capsys.readouterr()
        assert (
            str(shared_datadir.resolve() / "output_dirs/output4/-/-/ait.output.json")
            in cap.out
        )
        assert "Name: eval_mnist_acc_tf2.3" in cap.out
        assert "Version: 0.1" in cap.out
        assert re.search(r"Accuracy\s+0.81652", cap.out)
        assert cap.err == ""

    def test_main_result_show_full_option(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture,
        shared_datadir: pathlib.Path,
    ):

        mocker.patch.object(
            sys,
            "argv",
            ["qunomon-lite", "result-show", "output1"],
        )

        mocker.patch.object(ait, "console", Console(width=10000))
        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", shared_datadir / "output_dirs")

        cli.main()

        cap = capsys.readouterr()
        assert (
            str(shared_datadir.resolve() / "output_dirs/output1/-/-/ait.output.json")
            in cap.out
        )
        assert "Name: eval_mnist_acc_tf2.3" in cap.out
        assert "Version: 0.1" in cap.out
        assert re.search(r"Accuracy\s+0.81651", cap.out)
        assert cap.err == ""
