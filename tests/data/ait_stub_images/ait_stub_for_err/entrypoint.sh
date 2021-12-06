#!/bin/sh

ait_input_json=$(cat /usr/local/qai/ait.input.json)
inventory_sample=$(cat usr/local/qai/inventory/sample.txt)

json=$(cat <<EOS
{
  "AIT": {
      "Name": "ait-stub",
      "Version": "latest"
  },
  "ExecuteInfo": {
      "StartDateTime": "2021-12-05T17:42:41+0900",
      "EndDateTime": "2021-12-05T17:42:41+0900",
      "MachineInfo": {
          "cpu_brand": "AMD EPYC 7571",
          "cpu_arch": "X86_64",
          "cpu_clocks": "2.1998 GHz",
          "cpu_cores": "4",
          "memory_capacity": "16385515520"
      },
      "Error": {
          "Code": "E901",
          "Detail": "Traceback (most recent call last):\n  File \"/usr/local/lib/python3.6/site-packages/ait_sdk/develop/annotation.py\", line 80, in wrapper\n    ret = func(*args, **kwargs)\n  File \"/usr/local/qai/my_ait.py\", line 757, in main\n    X_test = mnist.load_image(ait_input.get_inventory_path('test_set_images'), image_px_size)\n  File \"/usr/local/lib/python3.6/site-packages/ait_sdk/utils/logging.py\", line 133, in wrapper\n    ret = func(*args, **kwargs)\n  File \"/usr/local/lib/python3.6/site-packages/ait_sdk/common/files/ait_input.py\", line 131, in get_inventory_path\n    return self._find_value('Inventories', name)\n  File \"/usr/local/lib/python3.6/site-packages/ait_sdk/utils/logging.py\", line 133, in wrapper\n    ret = func(*args, **kwargs)\n  File \"/usr/local/lib/python3.6/site-packages/ait_sdk/common/files/ait_input.py\", line 162, in _find_value\n    raise KeyError(f'{section_name}/{name} is not found.')\nKeyError: 'Inventories/test_set_images is not found.'\n"
      }
  },
  "__Args__": "$*",
  "__ait.input.json__": $ait_input_json,
  "__inventory_sample__": "$inventory_sample"
}
EOS
)

echo "$json"

mkdir -p /usr/local/qai/mnt/ip/job_result/-/-/
echo "$json" >> /usr/local/qai/mnt/ip/job_result/-/-/ait.output.json
