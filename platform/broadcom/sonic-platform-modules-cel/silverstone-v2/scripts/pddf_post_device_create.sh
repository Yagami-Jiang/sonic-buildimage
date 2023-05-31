#!/bin/bash
# Set STA_LED(OS) to Green, assuming everything came up fine.
ipmitool raw 0x3a 0x42 0x02 0x00
ipmitool raw 0x3a 0x39 0x02 0x00 01
ipmitool raw 0x3a 0x42 0x02 0x01

# install custom fpga device
sleep 3

modprobe pddf_custom_fpga_extend
