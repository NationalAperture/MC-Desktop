from __future__ import annotations

from collections import OrderedDict
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, Optional


@dataclass
class NodeConfig:
    sn: str = "N/A"
    vn: str = "N/A"


@dataclass
class NodeStage:
    stage: str = "1"
    travel: str = "1"
    gh: str = "N/A"
    tpi: str = "N/A"
    cpr: str = "N/A"


@dataclass
class NodePID:
    kp: str = "N/A"
    ki: str = "N/A"
    kd: str = "N/A"
    integrator: str = "N/A"
    rate: str = "N/A"


@dataclass
class NodeMotion:
    accel: str = "N/A"
    velo: str = "N/A"
    decel: str = "N/A"
    error: str = "N/A"
    jog_value: str = "350"
    hs_value: str = "850"
    jog: str = "350"


@dataclass
class NodeAdvanced:
    lower: str = "N/A"
    upper: str = "N/A"
    tolerance: str = "N/A"


@dataclass
class NodeState:
    config: NodeConfig = field(default_factory=NodeConfig)
    stage: NodeStage = field(default_factory=NodeStage)
    pid: NodePID = field(default_factory=NodePID)
    motion: NodeMotion = field(default_factory=NodeMotion)
    advanced: NodeAdvanced = field(default_factory=NodeAdvanced)


class NodeSectionView(MutableMapping[str, Any]):
    """Mutable mapping facade over a dataclass so legacy dict updates still work."""

    def __init__(self, section_obj: Any, key_map: Dict[str, str]) -> None:
        self._section = section_obj
        self._key_map = key_map

    def __getitem__(self, key: str) -> Any:
        attr = self._key_map[key]
        return getattr(self._section, attr)

    def __setitem__(self, key: str, value: Any) -> None:
        attr = self._key_map[key]
        setattr(self._section, attr, str(value))

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError("Node sections do not support deleting keys.")

    def __iter__(self) -> Iterator[str]:
        return iter(self._key_map.keys())

    def __len__(self) -> int:
        return len(self._key_map)

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        items = ", ".join(f"{k}={self[k]!r}" for k in self._key_map)
        return f"{self.__class__.__name__}({items})"


class NodeManager:
    """Manage MC node metadata and provide mutable views for the UI."""

    _CONFIG_KEYS = {"SN": "sn", "VN": "vn"}
    _STAGE_KEYS = {"Stage": "stage", "Travel": "travel", "GH": "gh", "TPI": "tpi", "CPR": "cpr"}
    _PID_KEYS = {"KP": "kp", "KI": "ki", "KD": "kd", "Int": "integrator", "Rate": "rate"}
    _MOTION_KEYS = {
        "Accel": "accel",
        "Velo": "velo",
        "Decel": "decel",
        "Error": "error",
        "JogValue": "jog_value",
        "HSValue": "hs_value",
        "Jog": "jog",
    }
    _ADVANCED_KEYS = {"Lower": "lower", "Upper": "upper", "Tolerance": "tolerance"}

    def __init__(self) -> None:
        self.current_node_id: Optional[str] = None
        self.velocity: str = "250"
        self.low_speed_velocity: str = "250"
        self.high_speed_velocity: str = "500"
        self.max_velocity: str = "999"
        self.travel_unit: str = "counts"
        self._nodes: "OrderedDict[str, NodeState]" = OrderedDict()

    # Internal helpers -------------------------------------------------
    def _get_node(self, node_id: str) -> Optional[NodeState]:
        return self._nodes.get(str(node_id))

    def _get_section_view(self, node_id: str, key_map: Dict[str, str], accessor: str) -> Optional[NodeSectionView]:
        node = self._get_node(node_id)
        if not node:
            return None
        section = getattr(node, accessor)
        return NodeSectionView(section, key_map)

    # Accessors -------------------------------------------------------
    def get_config(self, node_id: str) -> Optional[NodeSectionView]:
        return self._get_section_view(node_id, self._CONFIG_KEYS, "config")

    def get_config_values(self, node_id: str) -> tuple[str, str]:
        view = self.get_config(node_id)
        if not view:
            return "", ""
        return view["SN"], view["VN"]

    def get_stage(self, node_id: str) -> Optional[NodeSectionView]:
        return self._get_section_view(node_id, self._STAGE_KEYS, "stage")

    def get_stage_values(self, node_id: str) -> str:
        node = self._get_node(node_id)
        if not node:
            return ""
        stage = node.stage
        return ",".join(str(value) for value in (stage.stage, stage.travel, stage.gh, stage.tpi, stage.cpr))

    def get_pid(self, node_id: str) -> Optional[NodeSectionView]:
        return self._get_section_view(node_id, self._PID_KEYS, "pid")

    def get_pid_values(self, node_id: str) -> str:
        node = self._get_node(node_id)
        if not node:
            return ""
        pid = node.pid
        return ",".join(str(value) for value in (pid.kp, pid.ki, pid.kd, pid.integrator, pid.rate))

    def get_motion(self, node_id: str) -> Optional[NodeSectionView]:
        return self._get_section_view(node_id, self._MOTION_KEYS, "motion")

    def get_motion_values(self, node_id: str) -> str:
        node = self._get_node(node_id)
        if not node:
            return ""
        motion = node.motion
        values = (motion.accel, motion.velo, motion.decel, motion.error)
        return ",".join(str(value) for value in values)

    def get_advanced(self, node_id: str) -> Optional[NodeSectionView]:
        return self._get_section_view(node_id, self._ADVANCED_KEYS, "advanced")

    def get_advanced_values(self, node_id: str) -> str:
        node = self._get_node(node_id)
        if not node:
            return ""
        advanced = node.advanced
        return ",".join(str(value) for value in (advanced.lower, advanced.upper, advanced.tolerance))

    # Velocity helpers ------------------------------------------------
    def activate_high_speed(self) -> None:
        self.velocity = self.high_speed_velocity

    def activate_low_speed(self) -> None:
        self.velocity = self.low_speed_velocity

    def set_high_speed(self, high_speed: Any) -> None:
        self.high_speed_velocity = str(high_speed)
        motion = self.get_motion(self.current_node_id) if self.current_node_id else None
        if motion:
            motion["HSValue"] = self.high_speed_velocity
            motion["Jog"] = self.high_speed_velocity

    def set_low_speed(self, low_speed: Any) -> None:
        self.low_speed_velocity = str(low_speed)

    def set_max_speed(self, max_speed: Any) -> None:
        self.max_velocity = str(max_speed)

    # Node lifecycle --------------------------------------------------
    def add_node(self, node_id: Any) -> bool:
        node_key = str(node_id)
        if node_key in self._nodes:
            return False
        self._nodes[node_key] = NodeState()
        self.current_node_id = node_key
        return True

    def update_node_id(self, new_node_id: Any) -> bool:
        if self.current_node_id is None:
            return False
        old_id = self.current_node_id
        if old_id not in self._nodes:
            return False
        node_key = str(new_node_id)
        if node_key in self._nodes and node_key != old_id:
            return False

        self._nodes[node_key] = self._nodes.pop(old_id)
        self.current_node_id = node_key
        return True

    def remove_node(self, node_id: Any) -> bool:
        node_key = str(node_id)
        removed = self._nodes.pop(node_key, None)
        if removed is None:
            return False

        if self.current_node_id == node_key:
            self.current_node_id = next(iter(self._nodes), None)
        return True

    # Introspection ---------------------------------------------------
    def list_nodes(self) -> Iterable[str]:
        return list(self._nodes.keys())
