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
