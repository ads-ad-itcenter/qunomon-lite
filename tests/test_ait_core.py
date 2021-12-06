import logging
import os
import pathlib

import docker
import pytest
from pytest_mock import MockerFixture

from qunomon_lite import ait_core


class TestAit:
    @pytest.mark.parametrize(
        "repo,name,version,expected",
        [
            ("ait-repo", "ait-name", "ait-ver", "ait-repo/ait-name:ait-ver"),
            ("ait-repo", "ait-name", "", "ait-repo/ait-name:"),
            ("", "ait-name", "", "/ait-name:"),
            ("", "", "", "/:"),
        ],
    )
    def test__make_image_name(
        self,
        name,
        repo,
        version,
        expected,
    ):
        ait = ait_core.Ait(name=name, repo=repo, version=version)

        assert ait._make_image_name() == expected

    @pytest.mark.parametrize(
        "image_name,expected",
        [
            ("ait-repo/ait-name:ait-ver", ("ait-repo", "ait-name", "ait-ver")),
        ],
    )
    def test_from_image_name(
        self,
        image_name,
        expected,
    ):
        ait = ait_core.Ait.from_image_name(image_name)

        assert ait.repo == expected[0]
        assert ait.name == expected[1]
        assert ait.version == expected[2]

    @pytest.mark.parametrize(
        "image_name",
        [
            ("ait-repo/ait-name"),
            ("ait-repo"),
            ("ait-name:ait-version"),
        ],
    )
    def test_from_image_name_error(
        self,
        image_name,
    ):
        with pytest.raises(IndexError):
            ait_core.Ait.from_image_name(image_name)


class TestResult:
    def test_when_execution_succeeded(
        self,
        shared_datadir: pathlib.Path,
    ):
        r = ait_core.Result(output_base_dir_path=shared_datadir / "output_dirs/output1")
        assert r.job_id == "-"
        assert r.run_id == "-"
        assert r.output_base_dir_path == shared_datadir / "output_dirs/output1"
        assert r.output_dir_path == shared_datadir / "output_dirs/output1/-/-"
        assert (
            r.ait_output_json_path
            == shared_datadir / "output_dirs/output1/-/-/ait.output.json"
        )
        assert r.ait_output_json_dict["AIT"]["Name"] == "eval_mnist_acc_tf2.3"
        assert (
            r.ait_output_json_dict["ExecuteInfo"]["EndDateTime"]
            == "2021-11-22T18:17:55+0900"
        )
        assert r.ait_output_json_dict["Result"]["Measures"][1]["Name"] == "Precision"
        assert r.ait_output_json_dict["Result"]["Measures"][1]["Value"] == "0.06327692"
        assert r.execution_errors == {}
        assert r.is_execution_succeeded is True

    @pytest.mark.parametrize(
        "output_base_dir_name, job_id, run_id",
        [
            ("output_dirs/dummy", "-", "-"),
            ("output_dirs/output1", "dummy", "-"),
            ("output_dirs/output1", "-", "dummy"),
            ("output_dirs/output2", "-", "-"),
        ],
    )
    def test_when_execution_failed_not_exist_output_json(
        self,
        shared_datadir: pathlib.Path,
        output_base_dir_name,
        job_id,
        run_id,
    ):
        r = ait_core.Result(
            output_base_dir_path=shared_datadir / output_base_dir_name,
            job_id=job_id,
            run_id=run_id,
        )
        assert r.ait_output_json_dict == {}
        assert r.is_execution_succeeded is False
        assert r.execution_errors == {}

    def test_when_execution_failed_exist_output_json(
        self,
        shared_datadir: pathlib.Path,
    ):
        r = ait_core.Result(output_base_dir_path=shared_datadir / "output_dirs/output3")
        assert r.ait_output_json_dict["AIT"]["Name"] == "eval_mnist_acc_tf2.3"
        assert r.is_execution_succeeded is False
        assert r.execution_errors["Code"] == "E901"
        assert "Traceback (most recent call last):" in r.execution_errors["Detail"]


class TestAitExecutionError:
    def test___str__(self):
        e = ait_core.AitExecutionError("error messages")
        assert str(e) == (
            "AIT docker container running succeeded, "
            + "but AIT execution error occured. error messages"
        )

    def test_from_result(
        self,
        shared_datadir: pathlib.Path,
    ):
        r = ait_core.Result(output_base_dir_path=shared_datadir / "output_dirs/output3")
        e = ait_core.AitExecutionError.from_result(r)
        assert r.execution_errors["Code"] == "E901"
        assert "Traceback (most recent call last):" in r.execution_errors["Detail"]
        assert (
            "Error Code: E901, Error Detail: Traceback (most recent call last):"
            in e.message
        )


class TestRunner:
    def test__docker_run(
        self,
        shared_datadir: pathlib.Path,
        caplog: pytest.LogCaptureFixture,
    ):
        caplog.set_level(logging.INFO)

        ait_core.Runner._docker_run(
            image_name="library/alpine:latest",
            command="cat /tmp/data/sample.txt",
            volumes={
                str(shared_datadir.resolve()): {
                    "bind": "/tmp/data",
                    "mode": "ro",
                },
            },
        )
        assert caplog.record_tuples[1] == (
            "qunomon_lite.ait_core",
            logging.INFO,
            "hello",
        )

        caplog.clear()

        logger = logging.getLogger("test")
        ait_core.Runner._docker_run(
            image_name="library/alpine:latest",
            entrypoint="/bin/cat",
            command="/tmp/data/sample.txt",
            volumes={
                str(shared_datadir.resolve()): {
                    "bind": "/tmp/data",
                    "mode": "ro",
                },
            },
            custom_logger=logger,
        )
        assert caplog.record_tuples[1] == ("test", logging.INFO, "hello")

    def test__docker_run_error(
        self,
        tmp_path: pathlib.Path,
    ):
        with pytest.raises(docker.errors.APIError):
            ait_core.Runner._docker_run(
                image_name="library/alpine:latest",
                command="command",
                volumes={
                    str(tmp_path.resolve()): {
                        "bind": "/tmp/data",
                        "mode": "---Illegal option---",
                    },
                },
            )

    def test__get_logger_for_each_run(
        self,
        caplog: pytest.LogCaptureFixture,
        tmp_path: pathlib.Path,
    ):
        a = ait_core.Runner(ait_core.Ait("name", "repo", "version"))
        logger = a._get_logger_for_each_run(tmp_path)

        caplog.set_level(logging.ERROR)
        other_logger = logging.getLogger("test")

        assert logger.name == str(tmp_path)
        assert logger.propagate is False
        assert logger.level == logging.INFO

        logger.debug("test debug log at each run logger")
        logger.info("test info log at each run logger")
        logger.error("test error log at each run logger")

        other_logger.info("test info log at ather logger")
        other_logger.error("test error log at ather logger")

        assert caplog.record_tuples == [
            ("test", logging.ERROR, "test error log at ather logger"),
        ]
        with open(str(tmp_path / "ait_run.log"), "r") as f:
            assert "test info log at each run logger" in f.readline()
            assert "test error log at each run logger" in f.readline()
            assert f.readline() == ""

    def test__build_ait_input_json(self):
        a = ait_core.Runner(ait_core.Ait("name", "repo", "version"))
        d = a._build_ait_input_json()
        assert d == {
            "testbed_mount_volume_path": "/usr/local/qai/mnt",
            "job_id": "-",
            "run_id": "-",
            "Inventories": [],
            "MethodParams": [],
        }

        a.inventories = {
            "i1": "iii1",
            "i2": "/iii2",
            "i3": "iii/iii3",
            "i4": "/iii/iii4",
            "i5": "/iii/iii5/",
            "i6": "/iii/iii6.txt",
        }
        a.params = {"p1": "ppp1", "p2": "ppp2"}
        d = a._build_ait_input_json(job_id="jobid", run_id="runid")
        assert d == {
            "testbed_mount_volume_path": "/usr/local/qai/mnt",
            "job_id": "jobid",
            "run_id": "runid",
            "Inventories": [
                {"Name": "i1", "Value": "/usr/local/qai/inventory/iii1"},
                {"Name": "i2", "Value": "/usr/local/qai/inventory/iii2"},
                {"Name": "i3", "Value": "/usr/local/qai/inventory/iii3"},
                {"Name": "i4", "Value": "/usr/local/qai/inventory/iii4"},
                {"Name": "i5", "Value": "/usr/local/qai/inventory/iii5"},
                {"Name": "i6", "Value": "/usr/local/qai/inventory/iii6.txt"},
            ],
            "MethodParams": [
                {"Name": "p1", "Value": "ppp1"},
                {"Name": "p2", "Value": "ppp2"},
            ],
        }

    def test__build_volumes_config(self):
        pwd = pathlib.Path(os.getcwd())
        a = ait_core.Runner(ait_core.Ait("name", "repo", "version"))
        d = a._build_volumes_config(
            ait_input_json=pathlib.Path("my_ait_input_json"),
            output_base_dir=pathlib.Path("my_output_base_dir"),
        )
        assert d == {
            str(pwd / "my_ait_input_json"): {
                "bind": "/usr/local/qai/ait.input.json",
                "mode": "ro",
            },
            str(pwd / "my_output_base_dir"): {
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            },
        }
        d = a._build_volumes_config(
            ait_input_json=pathlib.Path("/aaa/bbb/my_ait_input_json"),
            output_base_dir=pathlib.Path("/ccc/ddd/my_output_base_dir/"),
        )
        assert d == {
            str("/aaa/bbb/my_ait_input_json"): {
                "bind": "/usr/local/qai/ait.input.json",
                "mode": "ro",
            },
            str("/ccc/ddd/my_output_base_dir"): {
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            },
        }

        a.inventories = {
            "i1": "iii1",
            "i2": "/iii2",
            "i3": "iii/iii3",
            "i4": "/iii/iii4",
            "i5": "/iii/iii5/",
            "i6": "/iii/iii6.txt",
        }
        d = a._build_volumes_config(
            ait_input_json=pathlib.Path("aaa/bbb/my_ait_input_json"),
            output_base_dir=pathlib.Path("ccc/ddd/my_output_base_dir"),
        )
        assert d == {
            str(pwd / "aaa/bbb/my_ait_input_json"): {
                "bind": "/usr/local/qai/ait.input.json",
                "mode": "ro",
            },
            str(pwd / "iii1"): {
                "bind": "/usr/local/qai/inventory/iii1",
                "mode": "ro",
            },
            str("/iii2"): {
                "bind": "/usr/local/qai/inventory/iii2",
                "mode": "ro",
            },
            str(pwd / "iii/iii3"): {
                "bind": "/usr/local/qai/inventory/iii3",
                "mode": "ro",
            },
            str("/iii/iii4"): {
                "bind": "/usr/local/qai/inventory/iii4",
                "mode": "ro",
            },
            str("/iii/iii5"): {
                "bind": "/usr/local/qai/inventory/iii5",
                "mode": "ro",
            },
            str("/iii/iii6.txt"): {
                "bind": "/usr/local/qai/inventory/iii6.txt",
                "mode": "ro",
            },
            str(pwd / "ccc/ddd/my_output_base_dir"): {
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            },
        }

    def test_run(
        self,
        tmp_path: pathlib.Path,
        ait_stub: str,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name(ait_stub),
        )
        r = runner.run(output_base_dir_path=tmp_path)
        assert r.output_base_dir_path == tmp_path
        assert r.job_id == "-"
        assert r.run_id == "-"
        assert r.ait_output_json_dict["__Args__"] == "/usr/local/qai"

    def test_run_with_inventories_and_params(
        self,
        tmp_path: pathlib.Path,
        shared_datadir: pathlib.Path,
        ait_stub: str,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name(ait_stub),
            inventories={
                "inventory_sample": str(shared_datadir.resolve() / "sample.txt")
            },
            params={"p1": "ppp1"},
        )
        r = runner.run(output_base_dir_path=tmp_path)
        assert r.output_base_dir_path == tmp_path
        assert r.job_id == "-"
        assert r.run_id == "-"
        assert r.ait_output_json_dict["__Args__"] == "/usr/local/qai"
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
        assert r.ait_output_json_dict["__ait.input.json__"] == ait_input_json_expected
        assert (
            ait_core._load_json_file(tmp_path / "ait.input.json")
            == ait_input_json_expected
        )
        assert r.ait_output_json_dict["__inventory_sample__"] == "hello"

    def test_run_with_full_option(
        self,
        tmp_path: pathlib.Path,
        mocker: MockerFixture,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name("repo/name:ver"),
            inventories={"i1": "iii1"},
            params={"p1": "ppp1"},
        )
        m = mocker.patch.object(ait_core.Runner, "_docker_run")
        mocker.patch.object(
            ait_core.Result, "_is_execution_succeeded", return_value=True
        )
        r = runner.run(output_base_dir_path=tmp_path, job_id="job-id", run_id="run-id")

        ait_input_json_expected = {
            "testbed_mount_volume_path": "/usr/local/qai/mnt",
            "job_id": "job-id",
            "run_id": "run-id",
            "Inventories": [
                {"Name": "i1", "Value": "/usr/local/qai/inventory/iii1"},
            ],
            "MethodParams": [
                {"Name": "p1", "Value": "ppp1"},
            ],
        }
        assert (
            ait_core._load_json_file(tmp_path / "ait.input.json")
            == ait_input_json_expected
        )

        kwargs = m.call_args_list[0][1]
        assert kwargs["image_name"] == "repo/name:ver"
        assert kwargs["command"] == "/usr/local/qai"
        assert kwargs["volumes"] == {
            str(tmp_path / "ait.input.json"): {
                "bind": "/usr/local/qai/ait.input.json",
                "mode": "ro",
            },
            str(pathlib.Path(os.getcwd()) / "iii1"): {
                "bind": "/usr/local/qai/inventory/iii1",
                "mode": "ro",
            },
            str(tmp_path): {
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            },
        }

        kwargs = m.call_args_list[1][1]
        assert kwargs["entrypoint"] == ""
        assert kwargs["command"] == (
            "chown -R %s:%s /usr/local/qai/mnt/ip/job_result"
            % (os.getuid(), os.getgid())
        )
        assert r.output_base_dir_path == tmp_path
        assert r.job_id == "job-id"
        assert r.run_id == "run-id"

    def test_run_not_linux(
        self,
        tmp_path: pathlib.Path,
        mocker: MockerFixture,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name("repo/name:ver"),
        )
        m = mocker.patch.object(ait_core.Runner, "_docker_run")
        mocker.patch.object(
            ait_core.Result, "_is_execution_succeeded", return_value=True
        )
        mocker.patch.object(os, "name", "nt")
        runner.run(output_base_dir_path=tmp_path)

        assert m.call_count == 1

    def test_run_execution_error(
        self,
        tmp_path: pathlib.Path,
        ait_stub_for_err: str,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name(ait_stub_for_err),
        )
        with pytest.raises(ait_core.AitExecutionError) as e:
            runner.run(output_base_dir_path=tmp_path)

        assert (
            "AIT docker container running succeeded, "
            + "but AIT execution error occured. "
            + "Error Code: E901, Error Detail: Traceback (most recent call last):"
            in str(e.value)
        )

    def test_run_docker_error(
        self,
        tmp_path: pathlib.Path,
        mocker: MockerFixture,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name("repo/name:ver"),
        )
        mocker.patch.object(
            ait_core.Runner,
            "_docker_run",
            side_effect=docker.errors.APIError("dummy docker api error"),
        )
        with pytest.raises(docker.errors.APIError):
            runner.run(output_base_dir_path=tmp_path)
