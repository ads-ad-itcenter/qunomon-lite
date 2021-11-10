import datetime
import json
import os
import pathlib
import pprint
import secrets
from logging import FileHandler, Formatter, getLogger
from typing import Dict

import docker
from docker.models.containers import Container
from rich.console import Console

from qunomon_lite.result import Result

docker_client = docker.from_env()


def result(
    run_id: str,
) -> Result:
    return Result(pathlib.Path("qunomon_lite_outputs") / run_id / "ait_output")


def run(
    ait: str,
    *,
    inventories: Dict[str, str] = {},
    params: Dict[str, str] = {},
) -> Result:

    console = Console()
    console.print("AIT: %s" % ait)
    console.print("inventories: ", inventories)
    console.print("params: ", params)

    output_root_dir_path = pathlib.Path("qunomon_lite_outputs")

    # ex) '20210709-090432-981577_81b4fb44ed'
    job_id = "%s_%s" % (
        datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f"),
        secrets.token_hex(5),
    )

    output_dir_path = output_root_dir_path / job_id
    output_dir_path.mkdir(parents=True, exist_ok=True)
    console.print("Output directory: ", output_dir_path)

    custom_file_logger = getLogger("qunomon_lite.custom_log_output")
    custom_file_log_handler = FileHandler(output_dir_path / "qunomon_lite.log")
    custom_file_log_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d: %(message)s")
    )
    custom_file_logger.addHandler(custom_file_log_handler)
    custom_file_logger.setLevel("INFO")
    # custom_file_logger.setLevel("DEBUG")  # for DEBUG # TODO: verboseオプションが欲しい

    run_id = "ait_output"
    ait_output_dir_path = output_dir_path / run_id

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
    custom_file_logger.debug(ait_input_json_file_path)
    with open(str(ait_input_json_file_path), mode="wt", encoding="utf-8") as f:
        json.dump(ait_input_json_dict, f, ensure_ascii=False)

    pwd_docker_host = pathlib.Path(os.getcwd())  # TODO:基底パスの指定

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
    custom_file_logger.debug("volumes: %s" % pprint.pformat(volumes))

    # raise Exception  # TODO: for DEBUG

    container: Container = None

    with console.status("[bold green]Working on AIT running..."):
        try:
            console.print("Running docker container (image: %s) ..." % ait)
            custom_file_logger.info("Running docker container (image: %s) ..." % ait)
            # TODO: コンテナイメージ名だけでなく、イメージIDも出力したい
            container = docker_client.containers.run(
                ait,
                command="/usr/local/qai",
                volumes=volumes,
                detach=True,
            )
            console.print("... Started %s" % container.id)
            custom_file_logger.info("... Started %s" % container.id)

            for line in container.logs(stream=True):
                custom_file_logger.info(line.strip().decode())

            console.print("... Stopped %s" % container.id)
            custom_file_logger.info("... Stopped %s" % container.id)

        finally:
            if container:
                container.remove()
                console.print("Removed docker container %s" % container.id)
                custom_file_logger.info("Removed docker container %s" % container.id)

    # Linuxの場合、出力ディレクトリ・ファイルのパーミッション変更
    # docker run の-idオプションによる指定の場合、AIT実行でパーミッションエラーが起こるため、
    # AIT実行後、同コンテナイメージを用いて、Python実行uid/gidにパーミッション変更を実施
    if os.name == "posix":
        try:
            custom_file_logger.info(
                "Adjustment for output file permission (on Linux only), Running docker container (image: %s) ..."
                % ait
            )
            container = docker_client.containers.run(
                ait,
                entrypoint="",
                command="chown -R %s:%s /usr/local/qai/mnt/ip/job_result"
                % (os.getuid(), os.getgid()),
                volumes=volumes,
                detach=True,
            )
            custom_file_logger.info("... Started %s" % container.id)

            for line in container.logs(stream=True):
                custom_file_logger.info(line.strip().decode())

            custom_file_logger.info("... Stopped %s" % container.id)

        finally:
            if container:
                container.remove()
                custom_file_logger.info("Removed docker container %s" % container.id)

    console.print("[bold]Finished!, run-id: [red]", job_id)
    console.print("See output directory for results: ", output_dir_path)
    return Result(ait_output_dir_path)
