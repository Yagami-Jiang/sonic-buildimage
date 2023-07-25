#!/usr/bin/env python
# @Company ：Celestica
# @Time    : 2023/7/20  13:46
# @Mail    : yajiang@celestica.com
# @Author  : jiang tao
try:
    from sonic_platform_pddf_base.pddf_psu import PddfPsu
    import re
    import os
    from . import helper
    from . import bmc_present_config
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

BMC_EXIST = bmc_present_config.get_bmc_status()
PSU_STATUS_INFO_CMD = "i2cget -y -f 100 0x0d 0x60"


class Psu(PddfPsu):
    """PDDF Platform-Specific PSU class"""

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfPsu.__init__(self, index, pddf_data, pddf_plugin_data)
        self.helper = helper.APIHelper()
        if BMC_EXIST:
            from . import sensor_list_config
            if not os.path.exists(sensor_list_config.Sensor_List_Info):
                cmd = "ipmitool sensor list > %s" % sensor_list_config.Sensor_List_Info
                self.helper.run_command(cmd)

    @staticmethod
    def get_capacity():
        return 550

    @staticmethod
    def get_type():
        return 'AC'

    def get_status(self):
        """
        Get PSU1/2 power ok status by iic command
        return: True or False
        """
        if BMC_EXIST:
            return super().get_status()
        else:
            status, res = self.helper.run_command(PSU_STATUS_INFO_CMD)
            if not status:
                return False
            psu_status = (bin(int(res, 16)))[-2:]
            psu_power_ok_index = 0 if self.psu_index == 1 else 1
            psu_power_ok = self.plugin_data['PSU']['psu_power_good']["i2c"]['valmap'][psu_status[psu_power_ok_index]]
            return psu_power_ok

    def get_presence(self):
        """
        Get PSU1/2 present status by iic command
        return: True or False
        """
        if BMC_EXIST:
            return super().get_presence()
        else:
            status, res = self.helper.run_command(PSU_STATUS_INFO_CMD)
            if not status:
                return False
            psu_status = (bin(int(res, 16)))[-4:-2]
            psu_present_index = 0 if self.psu_index == 1 else 1
            psu_present = self.plugin_data['PSU']['psu_present']["i2c"]['valmap'][psu_status[psu_present_index]]
            return psu_present



