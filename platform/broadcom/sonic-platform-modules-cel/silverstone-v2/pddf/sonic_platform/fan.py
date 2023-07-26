#!/usr/bin/env python
# @Company ：Celestica
# @Time    : 2023/5/26 16:36
# @Mail    : yajiang@celestica.com
# @Author  : jiang tao
try:
    from sonic_platform_pddf_base.pddf_fan import PddfFan
    from . import helper
    import re
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Fan(PddfFan):
    """PDDF Platform-Specific Fan class"""

    def __init__(self, tray_idx, fan_idx=0, pddf_data=None, pddf_plugin_data=None, is_psu_fan=False, psu_index=0):
        # idx is 0-based 
        PddfFan.__init__(self, tray_idx, fan_idx, pddf_data, pddf_plugin_data, is_psu_fan, psu_index)
        self.helper = helper.APIHelper()

    def get_presence(self):
        """
          Retrieves the presence of fan
        """
        return super().get_presence() and self.get_status()

    def get_direction(self):
        """
          Retrieves the direction of fan
 
          Returns:
               A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
               depending on fan direction
               Or N/A if fan removed or abnormal
        """
        if not self.get_status():
            return 'N/A'
        return super().get_direction()

    def get_speed(self):
        """
        Obtain the fan speed ratio (rpm/max rpm) according to the fan maximum rpm in the pd-plugin.json file
        (cause of the conversion, it needs to * 150)

        returns: if the value > 100, return the value of rpm. else return Speed/percentage of maximum speed.
        """
        fan_name = self.get_name()
        speed_rpm = self.get_speed_rpm()
        if "PSU" in fan_name:
            max_psu_fan_rpm = eval(self.plugin_data['PSU']['PSU_FAN_MAX_SPEED'])
            psu_speed_percentage = round(speed_rpm / max_psu_fan_rpm * 100)
            return speed_rpm if psu_speed_percentage > 100 else psu_speed_percentage
        # if use 'get_direction' to get the fan direction, it will make python maximum recursion depth exceeded.
        idx = (self.fantray_index - 1) * self.platform['num_fans_pertray'] + self.fan_index
        attr = "fan" + str(idx) + "_direction"
        output = self.pddf_obj.get_attr_name_output("FAN-CTRL", attr)
        if not output:
            return 0
        val = output['status'].rstrip()
        f_r_fan = "Front" if fan_name.endswith("1") else "Rear"
        max_fan_rpm = eval(self.plugin_data['FAN']['FAN_MAX_RPM_SPEED'][val][f_r_fan])
        speed_percentage = round(speed_rpm / max_fan_rpm * 100)
        return 100 if speed_percentage > 100 else speed_percentage
