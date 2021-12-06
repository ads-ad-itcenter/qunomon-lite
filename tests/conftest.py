import pathlib

import docker
import pytest


@pytest.fixture(scope="session")
def ait_stub() -> str:
    print("aaaaa")
    tag = "qunomon-lite/ait-stub:latest"
    docker_client = docker.from_env()
    docker_client.images.build(
        path=str(pathlib.Path(__file__).parent / "data/ait_stub_images/ait_stub"),
        tag=tag,
        rm=True,
        nocache=True,
    )
    return tag


@pytest.fixture(scope="session")
def ait_stub_for_err() -> str:
    tag = "qunomon-lite/ait-stub-for-err:latest"
    docker_client = docker.from_env()
    docker_client.images.build(
        path=str(
            pathlib.Path(__file__).parent / "data/ait_stub_images/ait_stub_for_err"
        ),
        tag=tag,
        rm=True,
        nocache=True,
    )
    return tag
