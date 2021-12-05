import logging
import os
import pathlib

import docker
import pytest
from pytest_mock import MockerFixture

from qunomon_lite import ait_core


def test__docker_run(
    shared_datadir: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level(logging.INFO)

    ait_core._docker_run(
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
    ait_core._docker_run(
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
    tmp_path: pathlib.Path,
):
    with pytest.raises(docker.errors.APIError):
        ait_core._docker_run(
            image_name="library/alpine:latest",
            command="command",
            volumes={
                str(tmp_path.resolve()): {
                    "bind": "/tmp/data",
                    "mode": "---Illegal option---",
                },
            },
        )


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
    def test_init(
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

    def test_ait_output_json_dict(
        self,
        shared_datadir: pathlib.Path,
    ):
        d = ait_core.Result(
            output_base_dir_path=shared_datadir / "output_dirs/output1"
        ).ait_output_json_dict()
        assert d["AIT"]["Name"] == "eval_mnist_acc_tf2.3"
        assert d["ExecuteInfo"]["EndDateTime"] == "2021-11-22T18:17:55+0900"
        assert d["Result"]["Measures"][1]["Name"] == "Precision"
        assert d["Result"]["Measures"][1]["Value"] == "0.06327692"

    @pytest.mark.parametrize(
        "output_base_dir_name, job_id, run_id",
        [
            ("output_dirs/dummy", "-", "-"),
            ("output_dirs/output1", "dummy", "-"),
            ("output_dirs/output1", "-", "dummy"),
            ("output_dirs/output2", "-", "-"),
        ],
    )
    def test_ait_output_json_dict_error(
        self,
        shared_datadir: pathlib.Path,
        output_base_dir_name,
        job_id,
        run_id,
    ):
        with pytest.raises(FileNotFoundError):
            ait_core.Result(
                output_base_dir_path=shared_datadir / output_base_dir_name,
                job_id=job_id,
                run_id=run_id,
            ).ait_output_json_dict()


class TestRunner:
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

    @pytest.mark.usefixtures("build_image_for_ait_stub")
    def test_run(
        self,
        tmp_path: pathlib.Path,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name("qunomon-lite/ait-stub:latest"),
        )
        r = runner.run(output_base_dir_path=tmp_path)
        assert r.output_base_dir_path == tmp_path
        assert r.job_id == "-"
        assert r.run_id == "-"
        assert r.ait_output_json_dict()["__Args__"] == "/usr/local/qai"

    @pytest.mark.usefixtures("build_image_for_ait_stub")
    def test_run_with_inventories_and_params(
        self,
        tmp_path: pathlib.Path,
        shared_datadir: pathlib.Path,
    ):
        runner = ait_core.Runner(
            ait=ait_core.Ait.from_image_name("qunomon-lite/ait-stub:latest"),
            inventories={
                "inventory_sample": str(shared_datadir.resolve() / "sample.txt")
            },
            params={"p1": "ppp1"},
        )
        r = runner.run(output_base_dir_path=tmp_path)
        assert r.output_base_dir_path == tmp_path
        assert r.job_id == "-"
        assert r.run_id == "-"
        assert r.ait_output_json_dict()["__Args__"] == "/usr/local/qai"
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
        assert r.ait_output_json_dict()["__ait.input.json__"] == ait_input_json_expected
        assert (
            ait_core._load_json_file(tmp_path / "ait.input.json")
            == ait_input_json_expected
        )
        assert r.ait_output_json_dict()["__inventory_sample__"] == "hello"

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
        m = mocker.patch.object(ait_core, "_docker_run")
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
        m = mocker.patch.object(ait_core, "_docker_run")
        mocker.patch.object(os, "name", "nt")
        runner.run(output_base_dir_path=tmp_path)

        assert m.call_count == 1
