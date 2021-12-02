import pathlib

import docker
import pytest


@pytest.fixture(scope="session")
def build_image_for_ait_stub():
    docker_client = docker.from_env()
    docker_client.images.build(
        path=str(pathlib.Path(__file__).parent / "data/ait_stub"),
        tag="qunomon-lite/ait-stub:latest",
        rm=True,
        nocache=True,
    )
