# OrCAD Capture Reference Notes

**IMPORTANT**: This file is the ONLY source the coding assistant may use
for OrCAD Tcl commands. Never use a command not listed here.

## Day 0 Questions to Answer

These must be filled in before vision code is written:

1. **Capture version and edition**: ?
2. **Part/pin limits of this edition**: ?
3. **How Tcl is executed**: ?
   Options: headless CLI, sourcing via command window, pywinauto
4. **Commands verified from journal**: None yet
5. **Which property holds power symbol net name**: ?
6. **Pin end offsets for each rotation/mirror**: see orcad/symbols.json (must be verified)
7. **Does journaling capture wire as single cmd or click sequence**: ?
8. **Netlist dump**: via Tcl or menu only?

## Journaling Setup

1. In Capture command window:
   ```
   SetOptionBool Journaling TRUE
   SetOptionBool DisplayCommands TRUE
   ```
   Or: Options > Extended Preferences > Journaling.

2. Build hand-designs and copy the logged commands here.

## Reference Designs (to be hand-built Day 0)

| File | Content | Learns |
|------|---------|--------|
| ref_R.dsn | R1, 2 wires, GND, VCC | place part, wire, power symbol |
| ref_RC.dsn | R1, C1, one junction | junction representation |
| ref_label.dsn | two wires with same net alias | connect by name |
| ref_opamp.dsn | 5-pin op-amp, 3 wires | multi-pin placement |
| ref_rot.dsn | R rotated 90, mirrored | rotation and mirror commands |

## Verified Commands

_None yet. Add each command here after verifying in a live session._

## XML Dump

```
XMATIC_DSN2XML <dsn> <xml>
XMATIC_XML2DSN <xml> <dsn>
```
