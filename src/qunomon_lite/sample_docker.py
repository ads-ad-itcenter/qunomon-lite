import docker

client = docker.from_env()


def func1():
    print("> running continer list")
    for container in client.containers.list():
        print(container.id)
    print("> image list")
    for image in client.images.list():
        print(image.id)
