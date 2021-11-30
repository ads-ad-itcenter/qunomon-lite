```sh
$ qunomon_lite run qunomon/eval_mnist_acc_tf2.3:0.1 \
  --inventories \
    trained_model=data/model_1.h5 \
    test_set_images=data/t10k-images-idx3-ubyte.gz \
    test_set_labels=data/t10k-labels-idx1-ubyte.gz \
  --params \
    class_count=10 \
    image_px_size=28 \
    auc_average=macro \
    auc_multi_class=raise
```

* Output
  ```
  AIT: qunomon/eval_mnist_acc_tf2.3:0.1
  inventories:
  {
      'trained_model': 'data/model_1.h5',
      'test_set_images': 'data/t10k-images-idx3-ubyte.gz',
      'test_set_labels': 'data/t10k-labels-idx1-ubyte.gz'
  }
  params:
  {
      'class_count': '10',
      'image_px_size': '28',
      'auc_average': 'macro',
      'auc_multi_class': 'raise'
  }
  Output directory:  qunomon_lite_outputs/20211201-011306-851862_7c7efdc45a
  Running docker container (image: qunomon/eval_mnist_acc_tf2.3:0.1) ...
  ... Started c9f1efe13b232b028dc3c431c8194f8f55c88ee08ee1b4550b3319cd655db0be
  ... Stopped c9f1efe13b232b028dc3c431c8194f8f55c88ee08ee1b4550b3319cd655db0be
  Removed docker container
  c9f1efe13b232b028dc3c431c8194f8f55c88ee08ee1b4550b3319cd655db0be
  Adjustment for output file permission (on Linux only), Running docker container
  (image: qunomon/eval_mnist_acc_tf2.3:0.1) ...
  ... Started cd806ff519e4c148f781b510141a7e18f3207461bc28f38d104af99d1397541c
  ... Stopped cd806ff519e4c148f781b510141a7e18f3207461bc28f38d104af99d1397541c
  Removed docker container
  cd806ff519e4c148f781b510141a7e18f3207461bc28f38d104af99d1397541c
  Finished! run-id:  20211201-011306-851862_7c7efdc45a
  See output directory for results:
  qunomon_lite_outputs/20211201-011306-851862_7c7efdc45a
  ```

```sh
qunomon_lite result-show 20211201-011306-851862_7c7efdc45a

or

qunomon_lite result-show latest
```

* Output
  ```
  qunomon_lite_outputs/20211201-011306-851862_7c7efdc45a/-/-/ait.output.json
  ├── AIT
  │   ├── Name: eval_mnist_acc_tf2.3
  │   └── Version: 0.1
  ├── ExecuteInfo
  │   ├── StartDateTime: 2021-12-01T01:13:11+0900
  │   ├── EndDateTime: 2021-12-01T01:13:52+0900
  │   └── MachineInfo
  │       ├── cpu_brand: AMD EPYC 7571
  │       ├── cpu_arch: X86_64
  │       ├── cpu_clocks: 2.1996 GHz
  │       ├── cpu_cores: 4
  │       └── memory_capacity: 16385523712
  └── Result
      ├── Measures
      │          Name         Value
      │   ─────────────────────────────────────────────────────────────────────────────
      │        Accuracy       0.81652
      │       Precision       0.06327693
      │         Recall        0.087357976
      │       F−measure       0.073392555
      │    AccuracyByClass    0.7739,0.8399,0.8602,0.8373,0.7884,0.695,0.8142,0.8256,0
      │                       .8726,0.8581
      │    PrecisionByClass   0.00616808,0.0701107,0.06635071,0.18869829,0.012048192,0
      │                       .14224137,0.071428575,0.0479798,0.025316456,0.0024271845
      │     RecallByClass     0.008163265,0.033480175,0.027131783,0.18514852,0.0142566
      │                       19,0.4809417,0.0782881,0.03696498,0.008213553,0.00099108
      │                       03
      │    F−measureByClass   0.007026741,0.045318976,0.038514405,0.1869065,0.01305965
      │                       15,0.2195496,0.074701145,0.04175819,0.012403064,0.001407
      │                       4184
      │          AUC          0.4826190252735609
      ├── Resources
      │             Name            Path
      │   ─────────────────────────────────────────────────────────────────────────────
      │    ConfusionMatrixHeatmap   /usr/local/qai/mnt/ip/job_result/-/-/resources/Con
      │                             fusionMatrixHeatmap/confusion_matrix.png
      │          ROC-curve          /usr/local/qai/mnt/ip/job_result/-/-/resources/ROC
      │                             -curve/roc_curve.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_0.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_1.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_2.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_3.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_4.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_5.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_6.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_7.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_8.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/-/-/resources/NGP
      │                             redictImages/ng_predict_actual_class_9.png
      └── Downloads
                  Name          Path
          ─────────────────────────────────────────────────────────────────────────────
          ConfusionMatrixCSV   /usr/local/qai/mnt/ip/job_result/-/-/downloads/Confusi
                                onMatrixCSV/confusion_matrix.csv
            PredictionResult    /usr/local/qai/mnt/ip/job_result/-/-/downloads/Predict
                                ionResult/prediction.csv
                  Log           /usr/local/qai/mnt/ip/job_result/-/-/downloads/Log/ait
                                .log
  ```
