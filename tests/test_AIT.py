import qunomon_lite.AIT
import json


def test_run():
    assert qunomon_lite.AIT.run() == "Hello, func1"


class TestRunResult:
    def test_str(self, shared_datadir):
        ait_output = json.loads(
            (shared_datadir / "output1/ait.output.json").read_text()
        )
        run_result = qunomon_lite.AIT.RunResult(**ait_output)
        actual = str(run_result)
        assert "{'AIT': {'Name': 'eval_mnist_acc_tf2.3', 'Version': '0.1'}" in actual
        assert "'ExecuteInfo': {'StartDateTime': '2021-05-10T17:38:14+0900'," in actual
        assert (
            "'MachineInfo': {'cpu_brand': 'Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz',"
            in actual
        )
        assert (
            "'Result': {'Measures': [{'Name': 'Accuracy', 'Value': '0.81652'},"
            in actual
        )

    def test_show(self, shared_datadir, capfd):
        ait_output = json.loads(
            (shared_datadir / "output1/ait.output.json").read_text()
        )
        run_result = qunomon_lite.AIT.RunResult(**ait_output)
        run_result.show()
        out, err = capfd.readouterr()
        assert "" == err
        assert "{'AIT': {'Name': 'eval_mnist_acc_tf2.3', 'Version': '0.1'}" in out
        assert "'ExecuteInfo': {'StartDateTime': '2021-05-10T17:38:14+0900'," in out
        assert (
            "'MachineInfo': {'cpu_brand': 'Intel(R) Core(TM) i7-8565U CPU @ 1.80GHz',"
            in out
        )
        assert (
            "'Result': {'Measures': [{'Name': 'Accuracy', 'Value': '0.81652'}," in out
        )
