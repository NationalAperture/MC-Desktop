import unittest

from mc_desktop.node_manager import NodeManager


class NodeManagerTestCase(unittest.TestCase):
    def test_add_and_get_values(self) -> None:
        manager = NodeManager()
        manager.add_node(1)

        self.assertEqual(manager.get_config("1"), {"SN": "N/A", "VN": "N/A"})

        sn, vn = manager.get_config_values("1")
        self.assertEqual(sn, "N/A")
        self.assertEqual(vn, "N/A")

        stage_values = manager.get_stage("1")
        self.assertEqual(stage_values["Stage"], "1")
        self.assertEqual(stage_values["Travel"], "1")

    def test_update_node_id_transfers_state(self) -> None:
        manager = NodeManager()
        manager.add_node(1)
        manager.current_node_id = "1"
        manager.set_high_speed("500")

        manager.update_node_id("42")

        self.assertNotIn("1", manager.config)
        self.assertEqual(manager.config["42"]["SN"], "N/A")
        self.assertEqual(manager.motion["42"]["jog"], "500")
        self.assertEqual(manager.motion["42"]["Jog"], "350")


if __name__ == "__main__":
    unittest.main()
