# P300 Add Pattern Prompt

Use this command to add a pattern from a historical grid file.

## Command Format
```text
P_300 Add Pattern Symbol=[SYMBOL] Start=[START] End=[END]
```

## Example
```text
P_300 Add Pattern Symbol=ATGE Start=123025 End=012326
```

## Rules
- `Symbol` is the ticker symbol.
- `Start` is the first date in the pattern span.
- `End` is the last date in the pattern span.
- Use the actual consolidation window from the grid file.
- Hold days are inferred from the attached grid file, so they do not need to be typed in the command.

## Notes
- Use `MMDDYY` date format.
- Keep the command short and machine-friendly.
- Use one command per pattern.
