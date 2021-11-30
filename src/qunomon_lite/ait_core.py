import json
import os
import pathlib
import pprint
import re
from logging import FileHandler, Formatter, getLogger
from typing import Dict, Union

import docker
from docker.models.containers import Container


class Ait:
    def __init__(
        self,
        name: str,
        repo: str,
        version: str,
        manifest: Dict[str, Union[str, dict]] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.repo = repo
        self.manifest = manifest

    def image_name(self) -> str:
        return "%s/%s:%s" % (self.repo, self.name, self.version)

    @classmethod
    def from_image_name(cls, image_name: str):
        splited = re.split("(.*)/(.*):(.*)", image_name)
        return Ait(repo=splited[1], name=splited[2], version=splited[3])

    @classmethod
    def from_manifest_url(cls, manifest_url: str):
        raise NotImplementedError  # TODO

    @classmethod
    def from_manifest_path(cls, manifest_path: str):
        raise NotImplementedError  # TODO


class Result:
    def __init__(
        self,
        output_base_dir_path: pathlib.Path,
        *,
        job_id: str = "-",
        run_id: str = "-",
    ) -> None:
        self.job_id = job_id
        self.run_id = run_id
        self.output_base_dir_path = output_base_dir_path
        self.output_dir_path = self.output_base_dir_path / job_id / run_id
        self.ait_output_json_path = self.output_dir_path / "ait.output.json"
        self.ait_output_json_dict: Dict[str, dict] = json.loads(
            self.ait_output_json_path.read_bytes()
        )


class Runner:
    def __init__(
        self,
        ait: Ait,
        inventories: Dict[str, str] = {},
        params: Dict[str, str] = {},
    ) -> None:
        self.ait = ait
        self.inventories = inventories
        self.params = params

    def run(
        self,
        output_base_dir_path: pathlib.Path,
        *,
        job_id: str = "-",
        run_id: str = "-",
    ) -> Result:

        output_base_dir_path.mkdir(parents=True, exist_ok=True)

        custom_file_logger = getLogger(__name__ + "_ait_run_log")
        custom_file_log_handler = FileHandler(output_base_dir_path / "ait_run.log")
        custom_file_log_handler.setFormatter(
            Formatter("%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d: %(message)s")
        )
        custom_file_logger.addHandler(custom_file_log_handler)
        custom_file_logger.setLevel("INFO")
        # custom_file_logger.setLevel("DEBUG")  # for DEBUG # TODO: verboseオプションが欲しい

        ait_input_json_dict = {
            "testbed_mount_volume_path": "/usr/local/qai/mnt",
            "job_id": job_id,
            "run_id": run_id,
            "Inventories": [
                {
                    "Name": k,
                    "Value": "/usr/local/qai/inventory/%s" % pathlib.Path(v).name,
                }
                for (k, v) in self.inventories.items()
            ],
            "MethodParams": [{"Name": k, "Value": v} for (k, v) in self.params.items()],
        }

        ait_input_json_file_path = output_base_dir_path / "ait.input.json"
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
            for (k, v) in self.inventories.items()
        }
        _volumes_result_dir = {
            str(pwd_docker_host / output_base_dir_path): {
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            }
        }
        volumes = dict(
            _volumes_ait_input_json, **_volumes_inventories, **_volumes_result_dir
        )
        custom_file_logger.debug("volumes: %s" % pprint.pformat(volumes))

        # raise Exception  # TODO: for DEBUG

        docker_client = docker.from_env()
        container: Container = None

        try:
            print("Running docker container (image: %s) ..." % self.ait.image_name())
            custom_file_logger.info(
                "Running docker container (image: %s) ..." % self.ait.image_name()
            )
            # TODO: コンテナイメージ名だけでなく、イメージIDも出力したい
            container = docker_client.containers.run(
                self.ait.image_name(),
                command="/usr/local/qai",
                volumes=volumes,
                detach=True,
            )
            print("... Started %s" % container.id)
            custom_file_logger.info("... Started %s" % container.id)

            for line in container.logs(stream=True):
                custom_file_logger.info(line.strip().decode())

            print("... Stopped %s" % container.id)
            custom_file_logger.info("... Stopped %s" % container.id)

        finally:
            if container:
                container.remove()
                print("Removed docker container %s" % container.id)
                custom_file_logger.info("Removed docker container %s" % container.id)

        # Linuxの場合、出力ディレクトリ・ファイルのパーミッション変更
        # docker run の-idオプションによる指定の場合、AIT実行でパーミッションエラーが起こるため、
        # AIT実行後、同コンテナイメージを用いて、Python実行uid/gidにパーミッション変更を実施
        if os.name == "posix":
            try:
                print(
                    "Adjustment for output file permission (on Linux only)"
                    + ", Running docker container (image: %s) ..."
                    % self.ait.image_name()
                )
                custom_file_logger.info(
                    "Adjustment for output file permission (on Linux only)"
                    + ", Running docker container (image: %s) ..."
                    % self.ait.image_name()
                )
                container = docker_client.containers.run(
                    self.ait.image_name(),
                    entrypoint="",
                    command="chown -R %s:%s /usr/local/qai/mnt/ip/job_result"
                    % (os.getuid(), os.getgid()),
                    volumes=volumes,
                    detach=True,
                )
                print("... Started %s" % container.id)
                custom_file_logger.info("... Started %s" % container.id)

                for line in container.logs(stream=True):
                    custom_file_logger.info(line.strip().decode())

                print("... Stopped %s" % container.id)
                custom_file_logger.info("... Stopped %s" % container.id)

            finally:
                if container:
                    container.remove()
                    print("Removed docker container %s" % container.id)
                    custom_file_logger.info(
                        "Removed docker container %s" % container.id
                    )

        return Result(
            output_base_dir_path=output_base_dir_path, job_id=job_id, run_id=run_id
        )
