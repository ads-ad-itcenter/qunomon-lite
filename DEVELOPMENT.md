# Development Guide

***...TBD...***

* 参考
  * https://future-architect.github.io/articles/20200820/#%E3%83%86%E3%82%B9%E3%83%88%E7%92%B0%E5%A2%83%E8%87%AA%E4%BD%93%E3%81%AE%E6%95%B4%E7%90%86%EF%BC%9Atox
    * venv
    * setup.{cfg,py}, requirements.txt
    * pytest + tox
    * black + tox
    * flake8 + tox
    * mypy + tox
    * アレンジ:
      * VSCode + Dockerコンテナ を利用した開発環境。
        * 定常利用はOS（コンテナ）の直のPython環境。
        * venvはtox経由でのみ利用。
  * https://tox.readthedocs.io/en/latest/example/package.html#setuptools

## 開発の流れ（1例）

* 環境
  * docker
    ```
    docker run -it --rm --mount type=bind,src=${PWD},dst=/tmp/work --workdir /tmp/work library/python:3.9 bash
    (container) #

    ...

    (container) # exit
    ```
  * venv
    ```
    python -m venv .venv

    source .venv/bin/activate

    (.venv) $

    ...

    (.venv) $ deactivate
    ```

* 開発対象パッケージ + 依存パッケージのインストール
  ```
  $ pip install -Ur requirements.txt
  ```
  * requirements.txt, setup.cfg(options.install_requires) を参照

* テストなど
  ```
  $ pytest

  $ flake8

  $ black . --check
  $ black . --diff

  $ mypy .
  ```
  or
  ```
  $ tox
  ```


## pip installして使ってみる

* 環境
  * docker
    ```
    docker run -it --rm --mount type=bind,src=${PWD},dst=/tmp/work --workdir /tmp/work library/python:3.9 bash
    (container) #

    ...

    (container) # exit
    ```
  * docker(ローカルフォルダをマウントしない => リモート経由でのインストール)
    ```
    docker run -it --rm library/python:3.9 bash
    (container) #

    ...

    (container) # exit
    ```
  * venv
    ```
    python -m venv .venv-tmp

    source .venv-tmp/bin/activate

    (.venv-tmp) $

    ...

    (.venv-tmp) $ deactivate
    ```

* ローカル経由でインストール
  * ローカルのディレクトリをインストールして試用
    ```
    pip install ./

    pip list
        Package      Version
        ------------ -------
        ...
        qunomon-lite 0.1
        ...

    python -c "from qunomon_lite import sample; print(sample.func1())"
        Hello, func1

    qunomon_lite_sample
        Hello, func2

    qunomon_lite_docker_sample
        > running continer list
        059def448abc1c6cd598f48c9fb6de5608445870c3b100beac80ef624329e4ac
        ...
        > image list
        sha256:c3361abeacfd5e4b6c1d391c393789a7cbababbd2989a390f82a38e541dd36a1
        ...

        参考)
        docker ps
            CONTAINER ID   IMAGE                  COMMAND            CREATED          STATUS          PORTS     NAMES
            059def448abc   qunomon-lite_develop   "sleep infinity"   11 minutes ago   Up 11 minutes             qunomon-lite_develop_1
        docker image list
            REPOSITORY             TAG       IMAGE ID       CREATED             SIZE
            qunomon-lite_develop   latest    c3361abeacfd   About an hour ago   1.28GB
            ...
    ```

* リモート経由でインストール
  * GitHubリポジトリ経由
    ```
    pip install git+https://github.com/ads-ad-itcenter/qunomon-lite.git
    or
    pip install git+https://github.com/ads-ad-itcenter/qunomon-lite.git@<branch-name>

    pip list
        Package      Version
        ------------ -------
        ...
        qunomon-lite 0.1
        ...

    python -c "from qunomon_lite import sample; print(sample.func1())"
        Hello, func1

    qunomon_lite_sample
        Hello, func2

    qunomon_lite_docker_sample
        > running continer list
        059def448abc1c6cd598f48c9fb6de5608445870c3b100beac80ef624329e4ac
        ...
        > image list
        sha256:c3361abeacfd5e4b6c1d391c393789a7cbababbd2989a390f82a38e541dd36a1
        ...

        参考)
        docker ps
            CONTAINER ID   IMAGE                  COMMAND            CREATED          STATUS          PORTS     NAMES
            059def448abc   qunomon-lite_develop   "sleep infinity"   11 minutes ago   Up 11 minutes             qunomon-lite_develop_1
        docker image list
            REPOSITORY             TAG       IMAGE ID       CREATED             SIZE
            qunomon-lite_develop   latest    c3361abeacfd   About an hour ago   1.28GB
            ...
    ```

