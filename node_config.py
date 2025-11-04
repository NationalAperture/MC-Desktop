class NodeManager:
    def __init__(self):
        self.current_node_id = None
        self.velocity = "250"
        self.low_speed_velocity = "250"
        self.high_speed_velocity = "500"
        self.max_velocity = "999"
        self.travel_unit = "counts"

        self.config = {}
        self.stage = {}
        self.pid = {}
        self.motion = {}
        self.advanced = {}

    def get_config(self, node_id):
        return self.config.get(node_id)

    def get_config_values(self, node_id):
        sn = self.get_config(node_id).get("SN")
        vn = self.get_config(node_id).get("VN")
        return sn, vn

    def get_stage(self, node_id):
        return self.stage.get(node_id)

    def get_stage_values(self, node_id):
        values = self.stage.get(node_id).values()
        values_str = ""
        for value in values:
            values_str += str(value) + ","
        return  values_str

    def get_pid(self, node_id):
        return self.pid.get(node_id)

    def get_pid_values(self, node_id):
        values = self.pid.get(node_id).values()
        values_str = ""
        for value in values:
            values_str += str(value) + ","
        return values_str

    def get_motion(self, node_id):
        return self.motion.get(node_id)

    def get_motion_values(self, node_id):
        values = list(self.motion.get(node_id).values())
        values = values[:-3]
        values_str = ""
        for value in values:
            values_str += str(value) + ","
        return values_str

    def get_advanced(self, node_id):
        return self.advanced.get(node_id)

    def get_advanced_values(self, node_id):
        values = self.advanced.get(node_id).values()
        values_str = ""
        for value in values:
            values_str += str(value) + ","

        return values_str

    def activate_high_speed(self):
        self.velocity = self.high_speed_velocity

    def activate_low_speed(self):
        self.velocity = self.low_speed_velocity

    def set_high_speed(self, high_speed):
        self.high_speed_velocity = high_speed
        self.motion[self.current_node_id].update({"jog": self.high_speed_velocity})

    def set_low_speed(self, low_speed):
        self.low_speed_velocity = low_speed

    def set_max_speed(self, max_speed):
        self.max_velocity = max_speed

    def add_node(self, node_id):
        try:
            node_id = str(node_id)
            self.config.update({node_id: {"SN": "N/A", "VN": "N/A", }})
            self.stage.update({node_id: {"Stage": "1", "Travel": "1", "GH": "N/A", "TPI": "N/A", "CPR": "N/A"}})
            self.pid.update({node_id: {"KP": "N/A", "KI": "N/A", "KD": "N/A", "Int": "N/A", "Rate": "N/A"}})
            self.motion.update({node_id: {"Accel": "N/A", "Velo": "N/A", "Decel": "N/A", "Error": "N/A", "JogValue": "350", "HSValue": "850", "Jog": "350"}})
            self.advanced.update({node_id: {"Lower": "N/A", "Upper": "N/A", "Tolerance": "N/A"}})
        except TypeError:  
            print(TypeError)

    def update_node_id(self, new_node_id):
        try:
            old_node_id = self.current_node_id
            self.current_node_id = new_node_id

            self.config[new_node_id] = self.config[old_node_id]
            self.stage[new_node_id] = self.stage[old_node_id]
            self.pid[new_node_id] = self.pid[old_node_id]
            self.motion[new_node_id] = self.motion[old_node_id]
            self.advanced[new_node_id] = self.advanced[old_node_id]

            del self.config[old_node_id]
            del self.stage[old_node_id]
            del self.pid[old_node_id]
            del self.motion[old_node_id]
            del self.advanced[old_node_id]
        except KeyError:
            print(KeyError)
        except Exception as e:
            print(e)

    def remove_node(self, index):
        keys_list = list(self.config.keys())
        key_to_delete = keys_list[index]
        del self.config[str(key_to_delete)]
        del self.stage[str(key_to_delete)]
        del self.pid[str(key_to_delete)]
        del self.motion[str(key_to_delete)]
        del self.advanced[str(key_to_delete)]