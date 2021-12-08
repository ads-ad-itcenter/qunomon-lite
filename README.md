# qunomon-lite: Lightweight tool for using Qunomon, AIT

[Qunomon](https://aistairc.github.io/qunomon/)およびAIT(AI system Test package)の簡易利用ツール

## 📌 Description

[Qunomon](https://aistairc.github.io/qunomon/)が提供する一部の機能を簡易的に利用できる、コマンドライン・Pythonツールです。
Qunomonを起動することなくAIT(AI system Test package)を実行することができます。
下記に挙げるようなユースケースにおいて、ML開発者がPoCや開発時にコマンドラインやPythonプログラム・Jupyterノートブックから利用したり、ML開発パイプライン上で利用されることを想定しています。
* ML開発者が、自身の開発環境で、QunomonのAIシステム評価パッケージ（AIT: AI system Test package）をお試しで使ってみたい
* ML開発者が、Qunomonの品質レポートを基に、MLモデルの改善対応を行っていて、AITをワンタイムで実行して改善具合を見たい
* ML開発パイプラインにて、AITを実行し、品質指標として活用したい

Note: 当ツールはQunomonを置き換えるものではありません。ユースケースによって、Qunomonの利用を検討ください。


## ✅ Features

「AITの実行」や「AITの実行結果表示」に関して、より柔軟な使い方を実現する機能を提供します。

### 機能a. AITの実行

* ✅ ローカル環境（Docker）でAIT実行
* ✅ パブリックAITの利用
* ⬛ プライベートAITの利用

### 機能b. AITの実行結果表示

* ✅ AITローカル実行結果の閲覧
* ⬛ AITローカル実行結果の測定値（Measures）の取得
* ⬛ AITローカル実行結果の一覧


---

## 💾 Install

### Requirements

* docker
  * sudo無しでdockerコマンドが実行できること
* python 3.x, pip


### Step


1. Install

    ```shell
    pip install qunomon-lite
    ```

    開発中の最新はGitHubリポジトリからインストールできます
    ```shell
    pip install -U git+https://github.com/ads-ad-itcenter/qunomon-lite.git
    ```


## 🚀 Usage

### 使用例:

* CUI: [examples/example-cli.md](https://github.com/ads-ad-itcenter/qunomon-lite/blob/main/examples/example-cli.md)
* Python: [examples/example-notebook.ipynb](https://github.com/ads-ad-itcenter/qunomon-lite/blob/main/examples/example-notebook.ipynb)

### AITの実行（パブリックAIT）

1. 実行したいAITを探し、AIT毎に提供されている`ait.manifest.json`を参照して、実行に必要となるファイルやパラメータを用意しておく
    * 探す場所: QunomonのGitHubリポジトリから
      例: https://github.com/aistairc/qunomon/blob/main/ait_repository/ait/eval_mnist_acc_tf2.3_0.1/deploy/container/repository/ait.manifest.json

1. AITを実行し、結果を表示

    * CUI:
      ```shell
      qunomon-lite ait run <ait-name>:<ait-version>
        [--inventories <inventory-name>=<path> ... ]
        [--params <param-name>=<value> ... ]

      qunomon-lite ait result-show
      ```

    * Python:
      ```python
      from qunomon_lite import ait

      result = ait.run(
          '<ait-name>:<ait-version>',
          inventories={'<inventory-name>': '<path>', ...},
          params={'<param-name>': '<value>', ...},
      )

      result.show()
      ```

### AITの実行結果表示

1. AIT実行結果の閲覧

    * CUI:
      ```shell
      qunomon-lite ait result-show {latest|<run-id>}
      ```

    * Python:
      ```python
      result = ait.result(未指定 or 'latest' or '<run-id>')   # 未指定 or 'latest': 最新の実行結果
      result.show()
      ```


## ℹ️ Anything else


### Troubleshooting

#### qunomon-liteコマンドが見つからない（command not found）

```shell
$ qunomon-lite --help
qunomon-lite: command not found
```

Debianパッケージのpipコマンド（python3-pip）は、一般ユーザで`pip install`すると、デフォルトで`~/.local` にインストールされるようです（`--user`オプションが自動で付与）。
そのため、Debian系のOS（Debian, Ubuntu,,,）で、各OSパッケージのpipを利用している場合（例. `sudo apt install python3-pip` ）は、`~/.local/bin`にPATHを通してみてください。

```shell
# for example...
$ export PATH="$HOME/.local/bin:$PATH"
```

#### AIT実行でPermissionErrorが発生（Permission denied）

```shell
$ qunomon-lite run qunomon/eval_mnist_acc_tf2.3:0.1 ...

...
Running docker container (image: qunomon/eval_mnist_acc_tf2.3:0.1) ...
Error while fetching server API version: ('Connection aborted.', PermissionError(13, 'Permission denied'))
```

当ツール・パッケージを利用するには、実行ユーザーが、sudoせずにdockerコマンドが利用できる必要があります。

```shell
# for example...
$ sudo usermod -aG docker $USER
```

## 📋 LICENCE

[Apache License 2.0](https://github.com/ads-ad-itcenter/qunomon-lite/blob/main/LICENSE)
