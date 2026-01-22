# MC-6 Serial Command Protocol

This document describes the serial command protocol used to communicate with National Aperture, Inc. MC-6 series motion controllers.

## Software Implementation

All command strings are centralized in `mc_desktop/commands.py` as constants:

```python
from mc_desktop.commands import (
    CMD_MOVE_ABSOLUTE,    # "mva"
    CMD_MOVE_RELATIVE,    # "mvr"
    CMD_JOG,              # "jog"
    CMD_POSITION,         # "pos"
    CMD_STATUS,           # "sts"
    # ... etc.
)
```

This ensures consistent command usage throughout the codebase and provides a single source of truth for the protocol implementation.

## Connection Parameters

| Parameter | Value |
|-----------|-------|
| Default Baud Rate | Configurable (9600, 19200, 38400, 57600, 115200) |
| Data Bits | 8 |
| Parity | None |
| Stop Bits | 1 |
| Line Terminator | `\r\n` (CRLF) |

## Command Format

Commands are sent as ASCII strings in the following format:

```
<node_id> <command> [parameter]\r\n
```

- **node_id**: Integer identifying the target controller node (e.g., `0`, `1`, `2`)
- **command**: Three-letter command code
- **parameter**: Optional value (integer or float depending on command)

### Example Commands
```
0 jog 350       # Jog node 0 at speed 350
0 mva 1000      # Move node 0 to absolute position 1000
0 sts           # Query status of node 0
```

## Command Reference

### Motion Commands

| Command | Parameters | Description | Example |
|---------|------------|-------------|---------|
| `jog` | speed (int) | Jog continuously at specified speed. Positive = forward, negative = backward | `0 jog 350` |
| `mov` | - | Execute loaded motion profile | `0 mov` |
| `mva` | position (int) | Move to absolute position | `0 mva 1000` |
| `mvr` | distance (int) | Move relative distance from current position | `0 mvr 500` |
| `lpa` | position (int) | Load absolute position (prepare move without executing) | `0 lpa 2000` |
| `lpr` | distance (int) | Load relative position (prepare move without executing) | `0 lpr -100` |
| `abm` | - | Abort motion (emergency stop) | `0 abm` |
| `hom` | position (int) | Set home position | `0 hom 0` |

### Status & Query Commands

| Command | Parameters | Description | Response |
|---------|------------|-------------|----------|
| `pos` | - | Query current position | Position value (int) |
| `sts` | - | Query status byte | Single ASCII character (see Status Byte) |
| `srn` | - | Query serial number | Serial number string |
| `vrn` | - | Query firmware version | Version string |

### Configuration Query Commands

| Command | Parameters | Description | Response Format |
|---------|------------|-------------|-----------------|
| `stg` | - | Get stage configuration | `type,travel_unit,gh,tpi,cpr` |
| `pid` | - | Get PID tuning values | `kp,ki,kd,integrator_limit,sample_rate` |
| `prf` | - | Get motion profile | `accel,velocity,decel,error_limit` |
| `swl` | - | Get software limits | `lower_limit,upper_limit` |
| `glm` | - | Get limit switch behavior | Behavior index (1-4) |
| `gut` | - | Get unit of travel | Travel unit string |

### Configuration Set Commands

#### Stage Configuration

| Command | Parameters | Description |
|---------|------------|-------------|
| `sst` | index (1-n) | Set stage type |
| `sut` | index (1-n) | Set unit of travel |
| `ghr` | value (int) | Set gear head ratio (GH) |
| `tpi` | value (int) | Set threads per inch (TPI) |
| `cpr` | value (int) | Set counts per revolution (CPR) |

#### PID Tuning

| Command | Parameters | Description |
|---------|------------|-------------|
| `kp` | value (float) | Set proportional gain |
| `ki` | value (float) | Set integral gain |
| `kd` | value (float) | Set derivative gain |
| `ilm` | value (int) | Set integrator limit |
| `spl` | value (int) | Set sample rate |

#### Motion Profile

| Command | Parameters | Description |
|---------|------------|-------------|
| `acc` | value (int) | Set acceleration |
| `vel` | value (int) | Set velocity |
| `dec` | value (int) | Set deceleration |
| `erl` | value (int) | Set error limit |

#### Limits & Tolerances

| Command | Parameters | Description |
|---------|------------|-------------|
| `sll` | value (int) | Set lower software limit |
| `slu` | value (int) | Set upper software limit |
| `tol` | value (int) | Set position tolerance |
| `slm` | index (1-4) | Set limit switch behavior |

### System Commands

| Command | Parameters | Description |
|---------|------------|-------------|
| `ena` | 0 or 1 | Enable (1) or disable (0) drive |
| `adr` | node_id (int) | Change controller node address |
| `sbr` | index (1-5) | Set baud rate (1=9600, 2=19200, 3=38400, 4=57600, 5=115200) |
| `scf` | slot (1-16) | Save configuration to slot |
| `lcf` | slot (1-16) | Load configuration from slot |
| `ecf` | - | Erase all saved configurations |

## Status Byte

The `sts` command returns a single ASCII character. The numeric value (ASCII code) contains bit flags:

| Bit | Mask | Description |
|-----|------|-------------|
| 0 | 0x01 | In Motion (1 = moving, 0 = stationary) |
| 1 | 0x02 | Reserved |
| 2 | 0x04 | Reserved |
| 3 | 0x08 | Reserved |
| 4 | 0x10 | Reserved |
| 5 | 0x20 | Reserved |
| 6 | 0x40 | Reserved |
| 7 | 0x80 | Reserved |

### Status Byte Example

```python
status = ord(response[0])  # Convert ASCII char to integer
in_motion = bool(status & 0x01)
```

## Response Format

Most query commands return comma-separated values (CSV):

```
# Stage configuration response
Linear,encoder_counts,0,20,4000

# PID values response
1.5,0.01,0.5,1000,100

# Motion profile response
500,1000,500,50
```

## Timing Considerations

- Allow at least 50ms between commands for processing
- After motion commands, poll `sts` to detect motion completion
- The `pos` command can be polled during motion to track position

## Error Handling

- Invalid commands are typically ignored without response
- If no response is received within timeout (default 500ms), the command may have failed
- Check `sts` after motion commands to verify successful execution

## Example Session

```
# Connect at 115200 baud
# Initialize node 0

> 0 srn
< SN12345

> 0 vrn
< 2.1.0

> 0 stg
< Linear,encoder_counts,1,20,4000

> 0 ena 1
< OK

> 0 mva 1000
< OK

> 0 sts
< A          # ASCII 65 = 0x41, bit 0 set = in motion

> 0 pos
< 523

> 0 sts
< @          # ASCII 64 = 0x40, bit 0 clear = stationary

> 0 pos
< 1000

> 0 ena 0
< OK
```
