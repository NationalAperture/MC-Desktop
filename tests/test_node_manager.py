import unittest

from mc_desktop.node_manager import NodeManager


class NodeManagerTestCase(unittest.TestCase):
    def test_add_node_initialises_defaults(self) -> None:
        manager = NodeManager()
        created = manager.add_node("1")

        self.assertTrue(created)
        config = manager.get_config("1")
        self.assertIsNotNone(config)
        self.assertEqual(config["SN"], "N/A")
        self.assertEqual(config["VN"], "N/A")

        stage = manager.get_stage("1")
        self.assertEqual(stage["Stage"], "1")
        self.assertEqual(stage["Travel"], "1")

        motion = manager.get_motion("1")
        self.assertEqual(motion["JogValue"], "350")
        self.assertEqual(motion["HSValue"], "850")

    def test_get_value_helpers_return_csv_strings(self) -> None:
        manager = NodeManager()
        manager.add_node("7")

        self.assertEqual(manager.get_stage_values("7"), "1,1,N/A,N/A,N/A")
        self.assertEqual(manager.get_pid_values("7"), "N/A,N/A,N/A,N/A,N/A")
        self.assertEqual(manager.get_motion_values("7"), "N/A,N/A,N/A,N/A")
        self.assertEqual(manager.get_advanced_values("7"), "N/A,N/A,N/A")

    def test_update_node_id_transfers_state(self) -> None:
        manager = NodeManager()
        manager.add_node("1")
        manager.current_node_id = "1"
        motion = manager.get_motion("1")
        motion["Jog"] = "123"

        updated = manager.update_node_id("42")

        self.assertTrue(updated)
        self.assertNotIn("1", manager.list_nodes())
        config = manager.get_config("42")
        self.assertEqual(config["SN"], "N/A")
        self.assertEqual(manager.get_motion("42")["Jog"], "123")

    def test_remove_node_by_id(self) -> None:
        manager = NodeManager()
        manager.add_node("1")
        manager.add_node("2")
        manager.current_node_id = "2"

        removed = manager.remove_node("1")

        self.assertTrue(removed)
        self.assertNotIn("1", manager.list_nodes())
        self.assertEqual(manager.current_node_id, "2")

    def test_remove_current_node_updates_pointer(self) -> None:
        manager = NodeManager()
        manager.add_node("1")
        manager.add_node("2")
        manager.current_node_id = "2"

        manager.remove_node("2")

        self.assertEqual(manager.current_node_id, "1")


if __name__ == "__main__":
    unittest.main()
