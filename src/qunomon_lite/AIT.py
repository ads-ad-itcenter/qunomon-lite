import docker
from docker.models.containers import Container
import json
import pathlib
import pprint
import datetime
import secrets

docker_client = docker.from_env()


class RunResult:
    def __init__(self, **kwargs):
        self._run_result = kwargs

    def __str__(self) -> str:
        return pprint.pformat(self._run_result)

    def show(self) -> None:
        print(self)


def run(
    ait: str,
    *,
    inventories: dict[str, str] = {},
    params: dict[str, str] = {},
) -> RunResult:

    output_root_dir_path = pathlib.Path("qunomon_lite_outputs")

    # ex) '20210709-090432-981577_81b4fb44ed'
    job_id = "%s_%s" % (
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
        secrets.token_hex(5),
    )

    output_dir_path = output_root_dir_path / job_id
    output_dir_path.mkdir(parents=True, exist_ok=True)

    run_id = "ait_output"
    ait_output_dir_path = output_dir_path / run_id

    # TODO: for debug
    inventories = {
        "trained_model": "tests/data/input1/model_1.h5",
        "test_set_images": "tests/data/input1/t10k-images-idx3-ubyte.gz",
        "test_set_labels": "tests/data/input1/t10k-labels-idx1-ubyte.gz",
    }
    params = {
        "class_count": "10",
        "image_px_size": "28",
        "auc_average": "macro",
        "auc_multi_class": "raise",
    }
    ait_input_json_dict = {
        "testbed_mount_volume_path": "/usr/local/qai/mnt",
        "job_id": job_id,
        "run_id": run_id,
        "Inventories": [
            {"Name": k, "Value": "/usr/local/qai/inventory/%s" % pathlib.Path(v).name}
            for (k, v) in inventories.items()
        ],
        "MethodParams": [{"Name": k, "Value": v} for (k, v) in params.items()],
    }

    ait_input_json_file_path = output_dir_path / "ait.input.json"
    print(ait_input_json_file_path)
    with open(str(ait_input_json_file_path), mode="wt", encoding="utf-8") as f:
        json.dump(ait_input_json_dict, f, ensure_ascii=False)

    pwd_docker_host = pathlib.Path("/home/hayashima/work/qunomon-lite")  # TODO:基底パスの指定

    _volumes_ait_input_json = {
        str(pwd_docker_host / ait_input_json_file_path): {
            "bind": "/usr/local/qai/ait.input.json",
            "mode": "ro",
        }
    }
    _volumes_inventories = {
        str(pwd_docker_host / v): {
            "bind": "/usr/local/qai/inventory/%s" % pathlib.Path(v).name,
            "mode": "ro",
        }
        for (k, v) in inventories.items()
    }
    _volumes_result_dir = {
        str(pwd_docker_host / output_root_dir_path): {
            "bind": "/usr/local/qai/mnt/ip/job_result",
            "mode": "rw",
        }
    }
    volumes = dict(
        _volumes_ait_input_json, **_volumes_inventories, **_volumes_result_dir
    )
    print("volumes: ")
    pprint.pprint(volumes)

    #    raise Exception  # TODO: for DEBUG
    container: Container = None
    try:
        print("Running docker container (image: %s) ..." % ait)
        container = docker_client.containers.run(
            ait,
            command="/usr/local/qai",
            volumes=volumes,
            detach=True,
        )
        print("... Started %s" % container.id)

        for line in container.logs(stream=True):
            print(line.strip().decode())

        print("... Stopped %s" % container.id)

    finally:
        if container:
            container.remove()
            print("Removed docker container %s" % container.id)

    with open(str(ait_output_dir_path / "ait.output.json"), "r") as f:
        output_json = json.load(f)

    run_result = RunResult(**output_json)

    return run_result
