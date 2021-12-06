import json
import logging
import os
import pathlib
import pprint
import re
import typing

import docker


def _load_json_file(
    path: pathlib.Path,
) -> typing.Dict[str, dict]:
    return json.loads(path.read_bytes())


def _save_json_file(
    data: typing.Dict[str, dict],
    path: pathlib.Path,
) -> None:
    with open(str(path), mode="wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


class Ait:
    def __init__(
        self,
        name: str,
        repo: str,
        version: str,
        manifest: typing.Dict[str, typing.Union[str, dict]] = None,
    ) -> None:
        self.name = name
        self.version = version
        self.repo = repo
        self.manifest = manifest
        self.image_name = self._make_image_name()

    def _make_image_name(self) -> str:
        return "%s/%s:%s" % (self.repo, self.name, self.version)

    @classmethod
    def from_image_name(
        cls,
        image_name: str,
    ):
        splited = re.split("(.*)/(.*):(.*)", image_name)
        return Ait(repo=splited[1], name=splited[2], version=splited[3])

    @classmethod
    def from_manifest_url(
        cls,
        manifest_url: str,
    ):
        raise NotImplementedError  # TODO

    @classmethod
    def from_manifest_path(
        cls,
        manifest_path: str,
    ):
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
        self.ait_output_json_dict = self._load_ait_output_json_dict()
        self.execution_errors = self._load_execution_errors()
        self.is_execution_succeeded = self._is_execution_succeeded()

    def _load_ait_output_json_dict(self) -> typing.Dict[str, dict]:
        if not self.ait_output_json_path.exists():
            return {}
        return _load_json_file(self.ait_output_json_path)

    def _load_execution_errors(self) -> typing.Dict[str, str]:
        return self.ait_output_json_dict.get("ExecuteInfo", {}).get("Error", {})

    def _is_execution_succeeded(self) -> bool:
        if not self.ait_output_json_dict:
            return False
        if self.execution_errors:
            return False
        return True


class AitExecutionError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return (
            "AIT docker container running succeeded, "
            + "but AIT execution error occured. %s"
        ) % self.message

    @classmethod
    def from_result(cls, result: Result):
        return cls(
            "Error Code: %s, Error Detail: %s"
            % (
                result.execution_errors.get("Code"),
                result.execution_errors.get("Detail"),
            )
        )


class Runner:
    def __init__(
        self,
        ait: Ait,
        inventories: typing.Dict[str, str] = {},
        params: typing.Dict[str, str] = {},
    ) -> None:
        self.ait = ait
        self.inventories = inventories
        self.params = params

    @staticmethod
    def _docker_run(
        *,
        image_name: str,
        command: str,
        volumes: dict,
        entrypoint: str = None,
        custom_logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:

        docker_client = docker.from_env()
        container: docker.models.containers.Container = None

        try:
            container = docker_client.containers.run(
                image_name,
                entrypoint=entrypoint,
                command=command,
                volumes=volumes,
                detach=True,
            )
            print("... Started %s" % container.id)
            custom_logger.info("... Started %s" % container.id)

            for line in container.logs(stream=True):
                custom_logger.info(line.strip().decode())

            print("... Stopped %s" % container.id)
            custom_logger.info("... Stopped %s" % container.id)

        finally:
            if container:
                container.remove()
                print("Removed docker container %s" % container.id)
                custom_logger.info("Removed docker container %s" % container.id)

    def _get_logger_for_each_run(
        self,
        output_base_dir_path: pathlib.Path,
    ) -> logging.Logger:
        logger = logging.getLogger(
            str(output_base_dir_path)
        )  # Run毎にユニークなロガー名として、出力ディレクトリ名を採用
        logger.propagate = False  # 親ロガーに伝播しない（念のため）
        handler = logging.FileHandler(output_base_dir_path / "ait_run.log")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)1.1s %(module)s:%(lineno)d: %(message)s"
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # TODO: verboseオプションが欲しい

        return logger

    def _build_ait_input_json(
        self,
        *,
        job_id: str = "-",
        run_id: str = "-",
    ) -> dict:

        return {
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

    def _build_volumes_config(
        self,
        *,
        ait_input_json: pathlib.Path,
        output_base_dir: pathlib.Path,
    ) -> dict:
        _volumes_ait_input_json = {
            str(ait_input_json.resolve()): {  # 絶対パス
                "bind": "/usr/local/qai/ait.input.json",
                "mode": "ro",
            }
        }
        _volumes_inventories = {
            str(pathlib.Path(v).resolve()): {  # 絶対パス
                "bind": "/usr/local/qai/inventory/%s" % pathlib.Path(v).name,
                "mode": "ro",
            }
            for (k, v) in self.inventories.items()
        }
        _volumes_result_dir = {
            str(output_base_dir.resolve()): {  # 絶対パス
                "bind": "/usr/local/qai/mnt/ip/job_result",
                "mode": "rw",
            }
        }
        return {
            **_volumes_ait_input_json,
            **_volumes_inventories,
            **_volumes_result_dir,
        }

    def run(
        self,
        output_base_dir_path: pathlib.Path,
        *,
        job_id: str = "-",
        run_id: str = "-",
    ) -> Result:

        output_base_dir_path.mkdir(parents=True, exist_ok=True)

        custom_logger = self._get_logger_for_each_run(output_base_dir_path)

        # ait.input.json
        ait_input_json_path = output_base_dir_path / "ait.input.json"
        custom_logger.debug(ait_input_json_path)
        _save_json_file(
            data=self._build_ait_input_json(job_id=job_id, run_id=run_id),
            path=ait_input_json_path,
        )

        # volumes設定
        volumes = self._build_volumes_config(
            ait_input_json=ait_input_json_path,
            output_base_dir=output_base_dir_path,
        )
        custom_logger.debug("volumes: %s" % pprint.pformat(volumes))

        # docker run
        print("Running docker container (image: %s) ..." % self.ait.image_name)
        custom_logger.info(
            "Running docker container (image: %s) ..." % self.ait.image_name
        )
        # TODO: コンテナイメージ名だけでなく、イメージIDも出力したい
        self._docker_run(
            custom_logger=custom_logger,
            image_name=self.ait.image_name,
            command="/usr/local/qai",
            volumes=volumes,
        )

        # Linuxの場合、出力ディレクトリ・ファイルのパーミッション変更
        # docker run の-idオプションによる指定の場合、AIT実行でパーミッションエラーが起こるため、
        # AIT実行後、同コンテナイメージを用いて、Python実行uid/gidにパーミッション変更を実施
        if os.name == "posix":
            print(
                "Adjustment for output file permission (on Linux only)"
                + ", Running docker container (image: %s) ..." % self.ait.image_name
            )
            custom_logger.info(
                "Adjustment for output file permission (on Linux only)"
                + ", Running docker container (image: %s) ..." % self.ait.image_name
            )
            self._docker_run(
                custom_logger=custom_logger,
                image_name=self.ait.image_name,
                entrypoint="",
                command="chown -R %s:%s /usr/local/qai/mnt/ip/job_result"
                % (os.getuid(), os.getgid()),
                volumes=volumes,
            )

        result = Result(
            output_base_dir_path=output_base_dir_path,
            job_id=job_id,
            run_id=run_id,
        )

        if not result.is_execution_succeeded:
            error = AitExecutionError.from_result(result)
            custom_logger.error(str(error))
            raise error

        return result
