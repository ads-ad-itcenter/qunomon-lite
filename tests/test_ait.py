import pathlib
import re
from typing import List

import pytest
from pytest_mock import MockerFixture

from qunomon_lite import ait, ait_core


class TestResult:
    def test_from_core(self):
        run_id = "run-id"
        output_base_dir_path = pathlib.Path("/tmp/dummy/") / run_id
        r = ait.Result.from_core(
            ait_core.Result(output_base_dir_path=output_base_dir_path)
        )

        assert r.run_id == run_id
        assert r.core.output_base_dir_path == output_base_dir_path

    def test_from_run_id(self):
        run_id = "run-id"
        r = ait.Result.from_run_id(run_id)

        output_base_dir_path = ait.OUTPUT_ROOT_DIR_PATH / run_id

        assert r.run_id == run_id
        assert r.core.output_base_dir_path == output_base_dir_path

    @pytest.mark.parametrize(
        "dirs, expected",
        [
            (
                [
                    "20211203-010203-123456_1f2f3f4f5f",
                    "20211203-010203-123458_1f2f3f4f5f",
                    "20211203-010203-123457_1f2f3f4f5f",
                ],
                "20211203-010203-123458_1f2f3f4f5f",
            ),
            (
                [
                    "20211203-010204-123456_1f2f3f4f5f",
                    "20211203-010203-123458_1f2f3f4f5f",
                    "20211203-010203-123457_1f2f3f4f5f",
                ],
                "20211203-010204-123456_1f2f3f4f5f",
            ),
            (
                [
                    "20211204-010203-123456_1f2f3f4f5f",
                    "20211203-010203-123458_1f2f3f4f5f",
                    "20211203-010203-123457_1f2f3f4f5f",
                ],
                "20211204-010203-123456_1f2f3f4f5f",
            ),
            (
                [
                    "20211203-010203-123456_1f2f3f4f5f",
                    "20211203-010203-123458_1f2f3f4f5f",
                    "3",
                    "20211203-010203-123457_1f2f3f4f5f",
                ],
                "3",
            ),
        ],
    )
    def test_latest_run(
        self,
        tmp_path: pathlib.Path,
        mocker: MockerFixture,
        dirs: List[str],
        expected: str,
    ):
        for d in dirs:
            (tmp_path / d).mkdir(parents=True, exist_ok=True)
        mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)
        assert ait.Result.from_latest_run().run_id == expected

    def test_show(self, shared_datadir: pathlib.Path):
        ait.Result.from_core(
            ait_core.Result(output_base_dir_path=shared_datadir / "output_dirs/output1")
        ).show()


def test_result(
    mocker: MockerFixture,
    shared_datadir: pathlib.Path,
):
    mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", shared_datadir / "output_dirs")

    r = ait.result()

    assert r.run_id == "output3"

    r = ait.result("output1")

    assert r.run_id == "output1"


def test__generate_run_id():
    assert re.match(r"^\d{8}-\d{6}-\d{6}_[0-9a-f]{10}$", ait._generate_run_id())


@pytest.mark.usefixtures("build_image_for_ait_stub")
def test_run(
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
):
    mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)

    r = ait.run("qunomon-lite/ait-stub:latest")

    assert re.match(r"^\d{8}-\d{6}-\d{6}_[0-9a-f]{10}$", r.run_id)
    assert r.core.output_base_dir_path == tmp_path / r.run_id
    assert r.core.output_dir_path == tmp_path / r.run_id / "-/-"
    assert r.core.ait_output_json_dict()["AIT"]["Name"] == "ait-stub"
    assert r.core.ait_output_json_dict()["AIT"]["Version"] == "latest"


@pytest.mark.usefixtures("build_image_for_ait_stub")
def test_run_full_option(
    mocker: MockerFixture,
    tmp_path: pathlib.Path,
    shared_datadir: pathlib.Path,
):
    mocker.patch.object(ait, "OUTPUT_ROOT_DIR_PATH", tmp_path)
    mocker.patch.object(ait, "_generate_run_id", return_value="run-id")

    r = ait.run(
        ait="qunomon-lite/ait-stub:latest",
        inventories={"inventory_sample": str(shared_datadir.resolve() / "sample.txt")},
        params={"p1": "ppp1"},
    )

    assert r.run_id == "run-id"
    assert r.core.output_base_dir_path == tmp_path / "run-id"
    assert r.core.output_dir_path == tmp_path / "run-id/-/-"
    assert r.core.ait_output_json_dict()["AIT"]["Name"] == "ait-stub"
    assert r.core.ait_output_json_dict()["AIT"]["Version"] == "latest"
    assert r.core.job_id == "-"
    assert r.core.run_id == "-"
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
