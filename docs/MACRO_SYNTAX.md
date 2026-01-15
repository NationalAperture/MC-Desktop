# Macro Syntax Guide

Macros allow you to automate sequences of motion commands in NAI-Mover. This guide covers the macro syntax and available features.

## Quick Start

1. Open NAI-Mover and connect to your controller
2. Navigate to the **Motion** page
3. Enter commands in the macro text area
4. Click **Run Macro** to execute

## Basic Syntax

Each line in a macro represents one command:

```
<node_id> <command> [parameter]
```

- **node_id**: The target controller node (e.g., `0`, `1`, `2`)
- **command**: Motion command code (see Command Reference below)
- **parameter**: Optional value (position, speed, etc.)

### Example

```
0 mva 1000
0 mva 0
```

This macro moves node 0 to position 1000, then back to position 0.

## Command Reference

### Motion Commands

| Command | Parameter | Description |
|---------|-----------|-------------|
| `mva` | position | Move to absolute position |
| `mvr` | distance | Move relative distance |
| `jog` | speed | Jog at specified speed |
| `mov` | - | Execute loaded motion |
| `abm` | - | Abort motion (stop) |
| `hom` | position | Set home position |

### Wait Commands

| Command | Parameter | Description |
|---------|-----------|-------------|
| `wait` | seconds | Pause execution for specified time |
| `sleep` | seconds | Alias for wait |

### Example with Wait

```
0 mva 500
wait 2
0 mva 1000
wait 1
0 mva 0
```

This moves to 500, waits 2 seconds, moves to 1000, waits 1 second, then returns to 0.

## Loop Constructs

Loops allow you to repeat a sequence of commands multiple times.

### Basic Loop

```
loop <count>
    <commands>
end
```

### Example

```
loop 3
0 mvr 100
0 mvr -100
end
```

This moves forward 100 units and back 3 times.

### Nested Loops

Loops can be nested for complex patterns:

```
loop 2
    0 mva 0
    loop 3
        0 mvr 50
    end
    0 mva 0
end
```

Execution sequence:
1. Move to 0
2. Move relative +50 (three times: 50 → 100 → 150)
3. Move to 0
4. Repeat entire sequence once more

## Execution Modes

### Run Once (Default)

Executes the macro a single time from start to finish.

### Run N Times

1. Select the **Variable** radio button
2. Enter the number of runs in the text field
3. Click **Run Macro**

The run count is displayed as "Run Count: X/N" during execution.

### Run Forever

Select the **Forever** radio button to loop the macro continuously until stopped.

## Control Flow

### Automatic Completion Waiting

The macro runner automatically waits for each motion command to complete before proceeding to the next step. You don't need to add explicit waits between motion commands.

```
0 mva 1000    # Runner waits for motion to complete
0 mva 2000    # Then executes this command
```

### Manual Timing with Wait

Use `wait` when you need explicit delays (e.g., for settling time, sensor readings, or synchronization):

```
0 mva 1000
wait 0.5       # Wait 500ms for settling
0 mva 2000
```

## Multi-Node Operations

Control multiple nodes by specifying different node IDs:

```
0 mva 1000
1 mva 500
2 mva 250
```

**Note**: Commands execute sequentially, waiting for each to complete.

## Step-Through Mode

Use the **Step** button to execute one command at a time:

1. Enter your macro
2. Click **Step** to execute the first command
3. The executed command is removed from the display
4. Click **Step** again for the next command
5. Continue until all commands are executed

This is useful for debugging or careful manual control.

## Saving and Loading Macros

### Save Macro

1. Enter your macro commands
2. Click **Save Macro**
3. Choose a location and filename (`.txt` extension added automatically)

### Load Macro

1. Click **Load Macro**
2. Select a previously saved `.txt` file
3. The commands are appended to any existing text

**Tip**: Clear the macro text area before loading if you want to replace rather than append.

## Complete Examples

### Back-and-Forth Pattern

```
loop 5
0 mva 1000
0 mva 0
end
```

Moves to 1000 and back to 0, five times.

### Scanning Pattern with Dwell

```
0 mva 0
loop 10
0 mvr 100
wait 0.5
end
0 mva 0
```

Steps through 10 positions, 100 units apart, pausing 0.5 seconds at each.

### Multi-Axis Synchronized Motion

```
loop 3
0 mva 500
1 mva 500
0 mva 0
1 mva 0
end
```

Moves both axes to 500, then back to 0, three times.

### Complex Nested Pattern

```
0 mva 0
loop 3
    loop 4
        0 mvr 25
    end
    0 mva 0
end
```

Moves in 25-unit steps (4 times), returns to 0, repeats 3 times.

## Error Handling

### Invalid Commands

- Commands with incorrect syntax are logged and skipped
- The macro continues with the next valid command

### Incomplete Commands

Commands must have at least a node ID and command:
```
0 mva        # ERROR: Missing position parameter
0            # ERROR: Missing command
mva 1000     # ERROR: Missing node ID
```

### Unmatched Loop/End

- `end` without matching `loop` is ignored
- `loop` without `end` logs a warning and skips the loop

## Best Practices

1. **Test with Step mode first**: Use step-through to verify your macro before running it fully

2. **Start and end at known positions**: Begin and end macros at position 0 or a home position for repeatability

3. **Use comments in external editor**: When editing macros in a text editor, you can add notes (they'll be executed as invalid commands and skipped)

4. **Save working macros**: Once you have a working sequence, save it for reuse

5. **Use relative moves for patterns**: `mvr` is often cleaner than calculating absolute positions

6. **Add waits for external synchronization**: If you need to synchronize with external equipment, use explicit wait commands

## Troubleshooting

### Macro Doesn't Run

- Verify serial connection is established
- Check that a node is selected
- Ensure macro text is not empty

### Motion Seems Stuck

- The runner waits for motion completion; long moves may appear stuck
- Check the position display to verify motion is occurring
- Use **Stop** button if needed

### Unexpected Behavior

- Check node IDs match your hardware configuration
- Verify parameter values are within valid ranges
- Use Step mode to identify the problematic command
