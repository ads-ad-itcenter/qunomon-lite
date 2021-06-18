# [READMEドラフト] qunomon-lite: Lightweight tool for using Qunomon, AIT

***:construction::construction::construction: 現時点では未実装。Readmeのみ先行して記載してます。 :construction::construction::construction:***

[Qunomon](https://aistairc.github.io/qunomon/)およびAIT(AI system Test package)の簡易利用ツール

![](https://dummyimage.com/320x160&text=demo-image)

## :pushpin: Description

[Qunomon](https://aistairc.github.io/qunomon/)が提供する一部の機能を簡易的に利用できる、コマンドライン・Pythonツールです。
Qunomonを起動することなくAIT(AI system Test package)を実行したり、、、できます。
ML開発者がPoCや開発時に利用したり、ML開発パイプライン上で利用されることを想定してます。

* Note: 当ツールはQunomonを置き換えるものではありません。ユースケースによって、Qunomonの利用を検討ください。

### Concept, Motivation

AIシステムの品質評価支援のOSSツールとしてQunomonがあります。
利用するにはローカルもしくは別サーバでQunomonを起動しておく必要があること、ユーザーインターフェースはWeb UI/APIであることなど、ユースケースによってはハードルが高いと感じました。
* ML開発者が、自身の開発環境で、QunomonのAIシステム評価パッケージ（AIT: AI system Test package）をお試しで使ってみたい
* ML開発者が、Qunomonの品質レポートを基に、MLモデルの改善対応を行っていて、AITをワンタイムで実行して改善具合を見たい
* MLトレーニングパイプラインにて、AITを実行し、品質指標として活用したい

このようなユースケースにおいて、簡易にQunomonの機能を利用できるようにすることが、当ツールの目的です。
そのため、Qunomonの全て機能を実現するのではなく、AITの実行といった一部の機能にフォーカスしています。
Qunomonの代替・再実装ではありません。

また、当ツールの開発における気づきを通して、Qunomonに、ひいてはML開発エコシステムに貢献したいと考えています。

## :white_check_mark: Features

:+1: : 実装優先度

### AITの実行

* [x] ローカル環境（Docker）でAIT実行 (:+1::+1:)
* [x] パブリックAITの利用 (:+1::+1:)
* [ ] プライベートAITの利用

### AITの実行結果ビュー

* [ ] AITローカル実行結果の一覧 (:+1:)
* [x] AITローカル実行結果の閲覧 (:+1::+1:)
* [ ] AITローカル実行結果の比較 (:+1:)

### 品質評価レポートの出力

* [ ] 複数AITの実行構成と結果判定ルール構成（≒Qunomonの「テストディスクリプション」）
* [ ] 品質評価レポートの出力

### AITのカタログ・検索

* [ ] AITの一覧・閲覧
* [ ] AITの検索

---

## :floppy_disk: Install

### Requirements

* docker
* python, pip


### Step

PyPIからインストールできます

1. Install
    * CUI
      ```shell
      $ pip install qunomon-lite
      ```
    * Jupyter
      ```ipynb
      !pip install qunomon-lite
      ```

1. 各種設定（任意）
    `.qunomon-lite/config.json` を作成
    ```json
    # default
    {
      "ait.result.dir": "ait_results",  # AIT実行結果ディレクトリ
    }
    ```

## :rocket: Usage

### AITの実行（ローカル環境、パブリックAIT）

#### AITを探す、実行準備 （ツール外の作業）

1. 実行したいAITを探し、`ait.manifest.json`を参照する
    * 探す場所: QunomonのGitHubリポジトリから
      例: https://github.com/aistairc/qunomon/blob/main/ait_repository/ait/eval_mnist_acc_tf2.3_0.1/deploy/container/repository/ait.manifest.json

1. `ait.manifest.json` から必要な情報を確認・用意する
    * AITの名称とバージョンを確認
      * 例:
        ```
        name: eval_mnist_acc_tf2.3
        version: 0.1
        ```
        * `ait.manifest.json`例
          ```json
          {
            "name": "eval_mnist_acc_tf2.3",
            ...
            "version": "0.1",
            ...
          }
          ```
    * `inventories` を参考に、必要なファイルを準備
      * 例:
        ```
        ./models/
          sample.h5
        ./data/
          test_set_images.gz
          test_set_labels.gz
        ```
        * `ait.manifest.json`例
          ```json
          {
            ...
            "inventories": [
              {
                "name": "trained_model",
                "type": "model",
                "description": "Tensorflow 2.3で学習したモデル",
                "format": [
                  "h5"
                ],
                "schema": "https://support.hdfgroup.org/HDF5/doc/"
              },
              {
                "name": "test_set_images",
                "type": "dataset",
                "description": "テスト画像セット（MNISTフォーマット）",
                "format": [
                  "gz"
                ],
                "schema": "http://yann.lecun.com/exdb/mnist/"
              },
              {
                "name": "test_set_labels",
                "type": "dataset",
                "description": "テスト画像ラベル（MNISTフォーマット）",
                "format": [
                  "gz"
                ],
                "schema": "http://yann.lecun.com/exdb/mnist/"
              }
            ],
            ...
          }
          ```
    * `parameters` を参考に、必要なパラメータを確認
      * 例:
        ```
        class_count: 10 (default)
        image_px_size: 28 (default)
        auc_average: macro (default)
        auc_multi_class: raise (default)
        ```

        * `ait.manifest.json`例
          ```json
          {
            ...
            "parameters": [
              {
                "name": "class_count",
                "type": "int",
                "description": "multiple classification class number",
                "default_val": "10",
                "min": "10",
                "max": "10"
              },
              {
                "name": "image_px_size",
                "type": "int",
                "description": "prediction image pixel size",
                "default_val": "28",
                "min": "28",
                "max": "28"
              },
              {
                "name": "auc_average",
                "type": "string",
                "description": "{‘micro’, ‘macro’, ‘samples’, ‘weighted’}\r\nref:\r\nhttps://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html",
                "default_val": "macro"
              },
              {
                "name": "auc_multi_class",
                "type": "string",
                "description": "{‘raise’, ‘ovr’, ‘ovo’}\nref:\nhttps://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html",
                "default_val": "raise"
              }
            ],
            ...
          }
          ```


#### AITの実行

##### CUI:

```shell
$ qunomon-lite ait run <ait-name>:<ait-version>|<ait-manifest-path> \
    --inventories \
      <inventory-name>=<path> \
      <inventory-name>=<path> \
    --params \
      <param-name>=<value> \
      <param-name>=<value>
```
* コマンドオプション:
  * `<ait-name>:<ait-version>|<ait-manifest-path>` (必須): AIT名・バージョン or ait.manifest.jsonを指定
    * `<ait-name>:<ait-version>`: 指定されたAIT名・バージョンの`ait.manifest.json`を、QunomonのGitHubリポジトリ( `https://github.com/aistairc/qunomon/blob/main/ait_repository/ait/<ait-name>_<ait-version>/deploy/container/repository/ait.manifest.json` )からダウンロードして利用します
    * `<ait-manifest-path>`: 指定されたait.manifest.jsonを利用します（ファイルパス or URL）
  * `--inventories <inventory-name>=<path>` (基本的に必須のはず): AITに渡すインベントリを指定します
  * `--params <param-name>=<value>`: AITに渡すパラメータを指定します
* 実行結果: `<ait.result.dir>/<ait-name>_<ait-version>/<timestamp-with-hash>/`に出力
  * `ait-output/`: (QunomonでのAIT実行時と同じ出力)
    * `downloads/`
    * `resources/`
    * `ait.output.json`
  * `qunomon-lite/`: qunomon-lite独自の出力
    * `ait.input.json`: AIT実行設定（qunomon-liteにより実行時に自動生成、フォーマットはQunomonと同様）
    * `ait.manifest.json`: AIT実行時に利用したait.manifest.json（qunomon-liteにより実行時にコピー）
    * `qunomon-lite_ait-run.log`: qunomon-liteの実行ログ（qunomon-lite独自）
    * `qunomon-lite_ait-run.json`: AIT実行時の各種情報（qunomon-lite独自）
      ```json
      {
        "inventories": {
          "trained_model": {
            "hash": "0B8E...B755"
          },
          ...
        },
        "dockerimage": {
          "repository": "qunomon/eval_mnist_acc_tf2.3",
          "tag": "0.1",
          "id": "0B8E...B755"
        },
        ...
      }
      ```
      * インベントリ（ファイル）のハッシュ文字列
        * 利用したファイルが同一かどうかのチェックに利用することを想定
      * DockerイメージID
        * 利用したDockerイメージの特定に利用することを想定
      * ...
* Note:
  * 実行時に、AITのDockerイメージをダウンロードして利用します。
    ait.manifest.json から得られるAIT名・バージョンから、Docker Hubの`qunomon`ユーザーによる配布イメージ( https://hub.docker.com/u/qunomon )を利用します。
    * docker pullコマンド例: 'docker pull qunomon/eval_mnist_acc_tf2.3:0.1'

* コマンド例:
  ```shell
  # minimum option
  $ qunomon-lite ait run eval_mnist_acc_tf2.3:0.1 \
      --inventories \
        trained_model=models/trained_model.h5 \
        test_set_images=data/test_set_images.gz \
        test_set_labels=data/test_set_labels.gz
  ```
  ```shell
  # other option example
  $ qunomon-lite ait run downloaded-ait-manifest/eval_mnist_acc_tf2.3_0.1/ait.manifest.json \
      --inventories \
        trained_model=models/trained_model.h5 \
        test_set_images=data/test_set_images.gz \
        test_set_labels=data/test_set_labels.gz \
      --params \
        class_count=20 \
        auc_average=macro
  ```

* 実行結果表示: 後述「AIT実行結果の閲覧」と同様

##### Python:

* コード例:
  ```python
  # minimum option
  import qunomon_lite

  qunomon_lite.AIT.run(
      'eval_mnist_acc_tf2.3:0.1',
      inventories={
          'trained_model': 'models/trained_model.h5',
          'test_set_images': 'data/test_set_images.gz',
          'test_set_labels': 'data/test_set_labels.gz',
      },
  )
  ```
  ```python
  # other option example
  ait_run_result = qunomon_lite.AIT.run(
      'ait-manifests/eval_mnist_acc_tf2.3_0.1/ait.manifest.json',
      inventories={
          'trained_model': 'models/trained_model.h5',
          'test_set_images': 'data/test_set_images.gz',
          'test_set_labels': 'data/test_set_labels.gz',
      },
      params={
          'class_count': 20,
          'auc_average': 'macro',
      },
  )
  ```
  > ...
  > Output: `<ait.result.dir>/<ait-name>_<ait-version>/<timestamp-with-hash>/`
  > Finished

* 実行結果表示: 後述「AIT実行結果の閲覧」と同様

### AITの実行結果ビュー（ローカル環境）

* 🤔どんなビューができるか？？→要フィージビリティ確認
  * CUIベースなビュー？
  * 簡易なHTMLを出力してブラウザ表示？
  * Jupyterノートブック上でイイ感じに見たい...
    * Jupyter拡張機能は避けたい。利用者環境を汚したくないので。

#### AIT実行結果の一覧表示

##### CUI:

```shell
$ qunomon-lite ait result-ls
# or
$ qunomon-lite ait result-ls <ait-name>
# or
$ qunomon-lite ait result-ls <ait-name>:<ait-version>
```
→ 見せ方は要検討

##### Python:

```python
import qunomon_lite

qunomon_lite.AIT.results().ls()
# or
qunomon_lite.AIT.results('<ait-name>').ls()
# or
ait_run_results = qunomon_lite.AIT.results('<ait-name>:<ait-version>')
ait_run_results.ls()
```
→ 見せ方は要検討

#### AIT実行結果の閲覧

##### CUI:

```shell
$ qunomon-lite ait result-show <run-id>
```
→ 見せ方は要検討

##### Python:

```python
ait_run_results.show('<run-id>')
# or
ait_run_result = ait_run_results['<run-id>']
ait_run_result.show()
```
→ 見せ方は要検討


#### AIT実行結果の比較

##### CUI:

```shell
$ qunomon-lite ait result-diff <run-id1> <run-id2>
```
→ 見せ方は要検討

##### Python:

```python
ait_run_results.diff('<run-id1>', '<run-id2>')
# or
ait_run_result.diff('<run-id2>')
# or
ait_run_result.diff(ait_run_result2)
```
→ 見せ方は要検討



## :information_source: Anything else

### （メモ）機能候補・アイデア

#### AITの検索、把握

どんなAITがあるか見つける、使い方を調べる、など

* 🤔Qunomon本体で実装・提供されそう？べき？で、そちらで事足りるか、、
* 🤔手元で見れる簡易ビューアー機能は、qunomon-liteとして、あってもいいのかも、、

#### Qunomonのリモート操作

既設のQunomonサーバをリモートで操作

* 手元で作成したML成果物（モデルなど）を既設Qunomonのテスト対象に登録
  * 🤔ファイルアップロードは、現状のQunomonの機能に無いため、実現不可能
  * 🤔プロジェクトのストレージに配置する作業は別途やる前提で、テスト対象に登録する操作ができるだけでも有益か？

* 手元で作成したML成果物（モデルなど）を既設Qunomonでテスト実行、レポート出力
  * 🤔この段階まで来ていたら、Web UI操作で事足りているか

#### Dockerを用いないAIT実行

Dockerが必須という点が、利用の障壁になりえる
クラウドサービスのJupyterやCI環境で、Dockerが利用できない環境も多そう

* Pythonの仮想環境（venv, toxなど）でAITを実行
  * 🤔ポータビリティを考慮してのDockerのはず、厳しそう


## :pencil: Author

***...TBD...***

## :clipboard: LICENCE

***...TBD...***
