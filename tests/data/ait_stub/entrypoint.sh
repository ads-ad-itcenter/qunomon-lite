#!/bin/sh

ait_input_json=$(cat /usr/local/qai/ait.input.json)
inventory_sample=$(cat usr/local/qai/inventory/sample.txt)

json=$(cat <<EOS
{
  "AIT": {
      "Name": "ait-stub",
      "Version": "latest"
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
