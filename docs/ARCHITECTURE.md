# Architecture Overview

This document describes the software architecture of MC-Desktop (NAI-Mover), a desktop application for controlling MC-6 series motion controllers.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              MC-Desktop                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        UI Layer (PySide6/Qt)                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │   │
│  │  │ MainWindow  │  │  Dialogs    │  │   Widgets               │   │   │
│  │  │             │  │ - Connection│  │ - MotorStats            │   │   │
│  │  │             │  │ - Update    │  │ - MacroEditor           │   │   │
│  │  │             │  │ - Record    │  │ - SettingsPanels        │   │   │
│  │  └──────┬──────┘  └─────────────┘  └─────────────────────────┘   │   │
│  └─────────┼────────────────────────────────────────────────────────┘   │
│            │                                                             │
│            │ signals/slots                                               │
│            ▼                                                             │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      Controller Layer                             │   │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐   │   │
│  │  │ MacroRunner     │  │ NodeSettings │  │ CommandDispatcher  │   │   │
│  │  │ - parse macros  │  │ Controller   │  │ - prompt dialogs   │   │   │
│  │  │ - loop handling │  │ - refresh    │  │ - execute commands │   │   │
│  │  │ - await motion  │  │ - set params │  │                    │   │   │
│  │  └────────┬────────┘  └──────┬───────┘  └─────────┬──────────┘   │   │
│  └───────────┼──────────────────┼───────────────────┼───────────────┘   │
│              │                  │                   │                    │
│              └──────────────────┼───────────────────┘                    │
│                                 ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Model Layer                                │   │
│  │  ┌─────────────────────────┐  ┌───────────────────────────────┐  │   │
│  │  │     NodeManager         │  │   CommunicationManager        │  │   │
│  │  │  - node state storage   │  │   - serial transport          │  │   │
│  │  │  - config/stage/pid/    │  │   - command queue             │  │   │
│  │  │    motion/advanced      │  │   - worker thread             │  │   │
│  │  │  - dataclass-based      │  │   - polling                   │  │   │
│  │  └─────────────────────────┘  └───────────────┬───────────────┘  │   │
│  └───────────────────────────────────────────────┼──────────────────┘   │
│                                                  │                       │
└──────────────────────────────────────────────────┼───────────────────────┘
                                                   │
                                                   │ Serial (RS-232/USB)
                                                   ▼
                                        ┌─────────────────────┐
                                        │   MC-6 Controller   │
                                        │   (Hardware)        │
                                        └─────────────────────┘
```

## Component Details

### UI Layer

The UI layer is built with PySide6 (Qt6) and handles all user interactions.

#### MainWindow (`main_window.py`)

The central UI component that:
- Creates and manages all widgets
- Routes user actions to controllers
- Displays serial communication logs
- Manages node selection via combobox

```
┌───────────────────────────────────────────────────────────┐
│ MainWindow                                                 │
├───────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────┐   │
│ │ MenuBar: [Connection] [Motion] [Settings]  [Node ▼] │   │
│ └─────────────────────────────────────────────────────┘   │
│ ┌───────────────────────┬─────────────────────────────┐   │
│ │                       │                             │   │
│ │    StackedWidget      │     System Monitor          │   │
│ │    ┌─────────────┐    │     ┌─────────────────┐     │   │
│ │    │ Motion Page │    │     │ MotorStats[0]   │     │   │
│ │    │ - Jog       │    │     │ Position: 1234  │     │   │
│ │    │ - Move      │    │     └─────────────────┘     │   │
│ │    │ - Macro     │    │     ┌─────────────────┐     │   │
│ │    └─────────────┘    │     │ MotorStats[1]   │     │   │
│ │    ┌─────────────┐    │     │ Position: 5678  │     │   │
│ │    │Settings Page│    │     └─────────────────┘     │   │
│ │    │ - Stage     │    │                             │   │
│ │    │ - PID       │    │                             │   │
│ │    │ - Motion    │    │                             │   │
│ │    │ - Advanced  │    │                             │   │
│ │    └─────────────┘    │                             │   │
│ └───────────────────────┴─────────────────────────────┘   │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Communication Log Table                              │   │
│ │ Device  │  Message              │  Timestamp         │   │
│ │ PC      │  0 mva 1000           │  2024-01-15 10:30 │   │
│ │ Node: 0 │  OK                   │  2024-01-15 10:30 │   │
│ └─────────────────────────────────────────────────────┘   │
│ StatusBar: [v0.1.9]                                       │
└───────────────────────────────────────────────────────────┘
```

#### Supporting Dialogs

| Dialog | File | Purpose |
|--------|------|---------|
| Connection | `main_window.py:Connection` | Serial port selection, node management |
| UpdateDialog | `update_dialog.py` | Update notifications and installation |
| RecordBus | `main_window.py:RecordBus` | Export communication log to CSV |

### Controller Layer

Controllers encapsulate business logic and coordinate between UI and model.

#### MacroRunner (`controllers.py`)

State machine for macro execution:

```
                    ┌─────────────────┐
                    │   parse_macro   │
                    │   _text()       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
         ┌─────────│   run_macro()   │
         │         └────────┬────────┘
         │                  │
         │                  ▼
         │         ┌─────────────────┐
         │         │ _prepare_run    │
         │         │ _state()        │
         │         └────────┬────────┘
         │                  │
         │                  ▼
         │     ┌────────────────────────┐
         │     │    manage_macro()      │◄────────┐
         │     └───────────┬────────────┘         │
         │                 │                      │
         │                 ▼                      │
         │     ┌────────────────────────┐         │
         │     │   _next_command()      │         │
         │     │   (state machine)      │         │
         │     └───────────┬────────────┘         │
         │                 │                      │
         │      ┌──────────┴──────────┐           │
         │      ▼                     ▼           │
         │   [loop/end]          [command]        │
         │      │                     │           │
         │      │                     ▼           │
         │      │          ┌─────────────────┐    │
         │      │          │_dispatch_command│    │
         │      │          │ await_completion│    │
         │      │          └────────┬────────┘    │
         │      │                   │             │
         │      │                   ▼             │
         │      │          ┌─────────────────┐    │
         │      │          │ [waiting for    │    │
         │      │          │  completion]    │    │
         │      │          └────────┬────────┘    │
         │      │                   │             │
         │      │                   │ command_complete
         │      │                   │ signal      │
         │      │                   ▼             │
         │      │          ┌─────────────────┐    │
         │      └─────────►│on_command_      │────┘
         │                 │complete()       │
         │                 └────────┬────────┘
         │                          │
         │                          ▼
         │                 ┌─────────────────┐
         └─────────────────│ [end of macro]  │
                           └─────────────────┘
```

#### NodeSettingsController (`controllers.py`)

Manages settings UI synchronization:
- Snapshot: Read current values from NodeManager
- Refresh: Queue serial commands to fetch from device
- Update: Parse device responses and update UI
- Set: Send new values to device

#### CommandDispatcher (`controllers.py`)

Declarative command execution with prompts:

```python
_PROMPTS = {
    "move_absolute": PromptConfig("mva", "Move Absolute", "Where would you like to move?"),
    "move_relative": PromptConfig("mvr", "Move Relative", "Where would you like to move?"),
    ...
}
```

### Model Layer

#### NodeManager (`node_manager.py`)

Dataclass-based state management:

```
┌─────────────────────────────────────────────────────┐
│ NodeManager                                          │
├─────────────────────────────────────────────────────┤
│ current_node_id: str                                │
│ _nodes: OrderedDict[str, NodeState]                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│   ┌───────────────────────────────────────────┐     │
│   │ NodeState (per node)                       │     │
│   ├───────────────────────────────────────────┤     │
│   │ ┌─────────────┐  ┌─────────────────────┐  │     │
│   │ │ NodeConfig  │  │ NodeStage           │  │     │
│   │ │ - sn        │  │ - stage             │  │     │
│   │ │ - vn        │  │ - travel            │  │     │
│   │ └─────────────┘  │ - gh, tpi, cpr      │  │     │
│   │                  └─────────────────────┘  │     │
│   │ ┌─────────────┐  ┌─────────────────────┐  │     │
│   │ │ NodePID     │  │ NodeMotion          │  │     │
│   │ │ - kp,ki,kd  │  │ - accel,velo,decel  │  │     │
│   │ │ - integrator│  │ - jog_value         │  │     │
│   │ │ - rate      │  │ - hs_value          │  │     │
│   │ └─────────────┘  └─────────────────────┘  │     │
│   │ ┌─────────────────────────────────────┐   │     │
│   │ │ NodeAdvanced                         │   │     │
│   │ │ - lower, upper (limits)              │   │     │
│   │ │ - tolerance, baud_rate               │   │     │
│   │ └─────────────────────────────────────┘   │     │
│   └───────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
```

#### CommunicationManager (`communication.py`)

Threaded serial communication:

```
┌─────────────────────────────────────────────────────────────┐
│ CommunicationManager                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Main Thread                     Worker Thread               │
│  ───────────                     ─────────────               │
│                                                              │
│  transmit_queue()                                            │
│       │                                                      │
│       │ put()                                                │
│       ▼                                                      │
│  ┌─────────────┐                 ┌─────────────────────┐    │
│  │   Queue     │────────────────►│    transmit()       │    │
│  │ - Serial    │    get()        │    (worker loop)    │    │
│  │   Command   │                 └──────────┬──────────┘    │
│  │ - Sleep     │                            │               │
│  │   Command   │                            ▼               │
│  └─────────────┘                 ┌─────────────────────┐    │
│                                  │  SerialTransport    │    │
│                                  │  - write()          │    │
│                                  │  - read_line()      │    │
│                                  └──────────┬──────────┘    │
│                                             │               │
│                                             │ Serial I/O    │
│                                             ▼               │
│                                  ┌─────────────────────┐    │
│                                  │   MC-6 Hardware     │    │
│                                  └─────────────────────┘    │
│                                                              │
│  Signals (Qt cross-thread communication):                   │
│  ─────────────────────────────────────────                  │
│                                                              │
│  ┌────────────────┐    ┌────────────────┐                   │
│  │ main_thread    │    │ poll           │                   │
│  │ (callback)     │    │ (position)     │                   │
│  └────────────────┘    └────────────────┘                   │
│  ┌────────────────┐    ┌────────────────┐                   │
│  │ log            │    │ command_       │                   │
│  │ (responses)    │    │ complete       │                   │
│  └────────────────┘    └────────────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Command Execution Flow

```
User clicks "Move Absolute"
         │
         ▼
┌─────────────────────────────────┐
│ CommandDispatcher.execute()     │
│ - Show prompt dialog            │
│ - User enters value             │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ MainWindow.send_command()       │
│ - Get current node_id           │
│ - Log to table                  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ CommunicationManager            │
│ .transmit_queue()               │
│ - Create SerialCommand          │
│ - Put in queue                  │
└────────────────┬────────────────┘
                 │
                 │ [Worker Thread]
                 ▼
┌─────────────────────────────────┐
│ transmit() loop                 │
│ - Dequeue command               │
│ - Write to serial               │
│ - Read response                 │
│ - Poll status until idle        │
└────────────────┬────────────────┘
                 │
                 │ emit signals
                 ▼
┌─────────────────────────────────┐
│ MainWindow receives signals     │
│ - log: display in table         │
│ - poll: update position display │
│ - command_complete: notify      │
└─────────────────────────────────┘
```

### Macro Execution Flow

```
User clicks "Run Macro"
         │
         ▼
┌─────────────────────────────────┐
│ MacroRunner.run_macro()         │
│ - Parse macro text              │
│ - Compute loop bounds           │
│ - Initialize state              │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐◄──────────────────────┐
│ manage_macro()                  │                       │
│ - Check if awaiting completion  │                       │
│ - Get next command              │                       │
└────────────────┬────────────────┘                       │
                 │                                        │
                 ▼                                        │
┌─────────────────────────────────┐                       │
│ _dispatch_command()             │                       │
│ - Set await_completion=True     │                       │
│ - Queue command with context    │                       │
└────────────────┬────────────────┘                       │
                 │                                        │
                 │ [Waiting...]                           │
                 │                                        │
                 ▼                                        │
┌─────────────────────────────────┐                       │
│ command_complete signal         │                       │
│ received from                   │                       │
│ CommunicationManager            │                       │
└────────────────┬────────────────┘                       │
                 │                                        │
                 ▼                                        │
┌─────────────────────────────────┐                       │
│ on_command_complete()           │                       │
│ - Clear awaiting flag           │                       │
│ - Call manage_macro()           │───────────────────────┘
└─────────────────────────────────┘
```

## Threading Model

```
┌─────────────────────────────────────────────────────────────┐
│                        Main Thread                           │
│                     (Qt Event Loop)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   UI Events  │  │   Signals    │  │  Timer Events    │   │
│  │   (clicks,   │  │   (slots)    │  │  (update check)  │   │
│  │   typing)    │  │              │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ Cross-thread signals
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                    QThreadPool                               │
├───────────────────────────┼─────────────────────────────────┤
│                           │                                  │
│  ┌────────────────────────▼────────────────────────────┐    │
│  │              Serial Worker Thread                    │    │
│  │                                                      │    │
│  │  while alive:                                        │    │
│  │      command = queue.get(timeout=0.5)               │    │
│  │      if command:                                     │    │
│  │          transport.write(command)                    │    │
│  │          response = transport.read()                 │    │
│  │          emit signals                                │    │
│  │      else:                                           │    │
│  │          poll_status()                               │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Design Patterns Used

| Pattern | Location | Purpose |
|---------|----------|---------|
| **MVC** | Overall architecture | Separation of concerns |
| **Observer** | Qt signals/slots | Event-driven communication |
| **Command** | SerialCommand dataclass | Encapsulate commands as objects |
| **State Machine** | MacroRunner._next_command | Loop/iteration tracking |
| **Facade** | NodeSectionView | Dict-like access to dataclasses |
| **Factory** | Worker class | Create runnable thread tasks |
| **Queue** | CommunicationManager | Serialize command processing |

## File Dependencies

```
app.py
    └── ui/MainWindow
            ├── communication.py (CommunicationManager)
            ├── node_manager.py (NodeManager)
            ├── updater.py (UpdateChecker)
            └── ui/controllers.py
                    ├── MacroRunner
                    ├── NodeSettingsController
                    └── CommandDispatcher
```
