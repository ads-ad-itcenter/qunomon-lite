***:construction::construction::construction: 当書について: :construction::construction::construction:***
* 現時点の方向性・機能イメージを共有するものです。
* Readmeの体裁で作成していますが、開発前の段階です。
* 開発が進むにつれブラッシュアップしていきますが、特に下記についてお気づきの点があればご指摘・ご意見頂きたいです
  1. 当ツールの目的・方向性
  1. 機能の過不足、開発の優先度


# [READMEドラフト] qunomon-lite: Lightweight tool for using Qunomon, AIT

[Qunomon](https://aistairc.github.io/qunomon/)およびAIT(AI system Test package)の簡易利用ツール

## :pushpin: Description

[Qunomon](https://aistairc.github.io/qunomon/)が提供する一部の機能を簡易的に利用できる、コマンドライン・Pythonツールです。
Qunomonを起動することなくAIT(AI system Test package)を実行したり、、、できます。
ML開発者がPoCや開発時にコマンドラインやPythonプログラム・Jupyterノートブックから利用したり、ML開発パイプライン上で利用されることを想定してます。

* Note: 当ツールはQunomonを置き換えるものではありません。ユースケースによって、Qunomonの利用を検討ください。

### Concept, Motivation

AIシステムの品質評価支援のOSSツールとしてQunomonがありますが、下記に挙げるような一部のユースケースにおいて、利用しにくい場合があると感じました。
* ML開発者が、自身の開発環境で、QunomonのAIシステム評価パッケージ（AIT: AI system Test package）をお試しで使ってみたい
* ML開発者が、Qunomonの品質レポートを基に、MLモデルの改善対応を行っていて、AITをワンタイムで実行して改善具合を見たい
* MLトレーニングパイプラインにて、AITを実行し、品質指標として活用したい

このようなユースケースにおいて、簡易にQunomonの機能を利用できるようにすることが、当ツールの目的です。
そのため、Qunomonの全て機能を実現するのではなく、AITの実行といった一部の機能にフォーカスしています。
Qunomonの代替・再実装ではありません。

また、当ツールの開発における気づきを通して、Qunomonに、ひいてはML開発エコシステムに貢献したいと考えています。

## :white_check_mark: Features

:+1: : 実装優先度

### 機能a. AITの実行

* [x] :+1:ローカル環境（Docker）でAIT実行
* [x] :+1:パブリックAITの利用
* [ ] プライベートAITの利用

### 機能b. AITの実行結果ビュー

* [ ] AITローカル実行結果の一覧
* [x] :+1:AITローカル実行結果の閲覧
* [ ] AITローカル実行結果の比較


---

## :floppy_disk: Install

### Requirements

* docker
* python, pip


### Step

PyPIからインストールできます

1. Install
    ```shell
    pip install qunomon-lite
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

### 機能a. AITの実行

1. 実行したいAITを探し、AIT毎に提供されている`ait.manifest.json`を参照して、実行に必要となるファイルやパラメータを用意しておく
    * 探す場所: QunomonのGitHubリポジトリから
      例: https://github.com/aistairc/qunomon/blob/main/ait_repository/ait/eval_mnist_acc_tf2.3_0.1/deploy/container/repository/ait.manifest.json

1. AITを実行

    :construction:特に未確定な内容です:construction:

    * CUI:
      ```shell
      qunomon-lite ait run {<ait-name>:<ait-version> | <ait-manifest-path>}
        [--inventories <inventory-name>=<path> ... ]
        [--params <param-name>=<value> ... ]
      ```

    * Python:
      ```python
      import qunomon_lite

      ait_run_result = qunomon_lite.AIT.run(
          '<ait-name>:<ait-version> or <ait-manifest-path>',
          inventories={'<inventory-name>': '<path>', ...},
          params={'<param-name>': '<value>', ...},
      )
      ```

### 機能b. AITの実行結果ビュー

1. AIT実行結果の一覧表示

    :construction:特に未確定な内容です:construction:

    * CUI:
      ```shell
      qunomon-lite ait result-ls [<ait-name> | <ait-name>:<ait-version>]
      ```
      → 見せ方は要検討

    * Python:
      ```python
      import qunomon_lite

      ait_run_results = qunomon_lite.AIT.results('未指定 or <ait-name>:<ait-version> or <ait-manifest-path>').ls()
      ```
      → 見せ方は要検討

1. AIT実行結果の閲覧

    :construction:特に未確定な内容です:construction:

    * CUI:
      ```shell
      qunomon-lite ait result-show <run-id>
      ```
      → 見せ方は要検討

    * Python:
      ```python
      ait_run_result = ait_run_results['<run-id>']
      ait_run_result.show()
      ```
      ```python
      ait_run_result.show_m('未指定 or <measure-name>', ...)
      ```
      ```python
      ait_run_result.show_r('未指定 or <resource-name>', ...)
      ```
      ```python
      ait_run_result.show_d('未指定 or <download-name>', ...)
      ```
      → 見せ方は要検討

1. AIT実行結果の比較(同一AIT間のみ)

    :construction:特に未確定な内容です:construction:

    * CUI:
      ```shell
      qunomon-lite ait result-diff <run-id1> <run-id2>
      ```
      → 見せ方は要検討

    * Python:
      ```python
      ait_run_result.diff(ait_run_result2)
      ```
      ```python
      ait_run_result.diff_m(ait_run_result2, '未指定 or <measure-name>', ...)
      ```
      ```python
      ait_run_result.diff_r(ait_run_result2, '未指定 or <resource-name>', ...)
      ```
      ```python
      ait_run_result.diff_d(ait_run_result2, '未指定 or <download-name>', ...)
      ```
      → 見せ方は要検討

## :information_source: Anything else

***...TBD...***

## :pencil: Author

***...TBD...***

## :clipboard: LICENCE

***...TBD...***
