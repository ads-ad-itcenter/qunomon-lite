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
  {'class_count': '10', 'image_px_size': '28', 'auc_average': 'macro', 'auc_multi_class': 'raise'}
  Output directory:  qunomon_lite_outputs/20211122-181707-836943_d56d581c93
  Running docker container (image: qunomon/eval_mnist_acc_tf2.3:0.1) ...
  ... Started 8c9fb36b3add328803262925a1585314f871fea48b3fc44bddfa5899b66c828e
  ... Stopped 8c9fb36b3add328803262925a1585314f871fea48b3fc44bddfa5899b66c828e
  Removed docker container 8c9fb36b3add328803262925a1585314f871fea48b3fc44bddfa5899b66c828e
  Finished!, run-id:  20211122-181707-836943_d56d581c93
  See output directory for results:  qunomon_lite_outputs/20211122-181707-836943_d56d581c93
  ```

```sh
qunomon_lite result-show 20211122-181707-836943_d56d581c93
```

* Output
  ```
  qunomon_lite_outputs/20211122-181707-836943_d56d581c93/ait_output/ait.output.json
  ├── AIT
  │   ├── Name: eval_mnist_acc_tf2.3
  │   └── Version: 0.1
  ├── ExecuteInfo
  │   ├── StartDateTime: 2021-11-22T18:17:12+0900
  │   ├── EndDateTime: 2021-11-22T18:17:55+0900
  │   └── MachineInfo
  │       ├── cpu_brand: AMD EPYC 7571
  │       ├── cpu_arch: X86_64
  │       ├── cpu_clocks: 2.2000 GHz
  │       ├── cpu_cores: 4
  │       └── memory_capacity: 16385515520
  └── Result
      ├── Measures
      │          Name         Value
      │   ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
      │        Accuracy       0.81652
      │       Precision       0.06327693
      │         Recall        0.087357976
      │       F−measure       0.073392555
      │    AccuracyByClass    0.7739,0.8399,0.8602,0.8373,0.7884,0.695,0.8142,0.8256,0.8726,0.8581
      │    PrecisionByClass   0.00616808,0.0701107,0.06635071,0.18869829,0.012048192,0.14224137,0.071428575,0.0479798,0.025316456,0.00
      │                       24271845
      │     RecallByClass     0.008163265,0.033480175,0.027131783,0.18514852,0.014256619,0.4809417,0.0782881,0.03696498,0.008213553,0.
      │                       0009910803
      │    F−measureByClass   0.007026741,0.045318976,0.038514405,0.1869065,0.0130596515,0.2195496,0.074701145,0.04175819,0.012403064,
      │                       0.0014074184
      │          AUC          0.4826190252735609
      ├── Resources
      │             Name            Path
      │   ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
      │    ConfusionMatrixHeatmap   /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/ConfusionM
      │                             atrixHeatmap/confusion_matrix.png
      │          ROC-curve          /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/ROC-curve/
      │                             roc_curve.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_0.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_1.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_2.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_3.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_4.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_5.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_6.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_7.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_8.png
      │       NGPredictImages       /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/resources/NGPredictI
      │                             mages/ng_predict_actual_class_9.png
      └── Downloads
                  Name          Path
          ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
          ConfusionMatrixCSV   /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/downloads/ConfusionMatri
                                xCSV/confusion_matrix.csv
            PredictionResult    /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/downloads/PredictionResu
                                lt/prediction.csv
                  Log           /usr/local/qai/mnt/ip/job_result/20211122-181707-836943_d56d581c93/ait_output/downloads/Log/ait.log
  ```
