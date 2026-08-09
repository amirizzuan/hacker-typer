# hacker-typer

My interpretation of "hacker-typer" in multiple programming languages. Influenced by www.hackertyper.net

For my style, I'd rather have this running in the UNIX command line terminal.

## Current Implementation

**Python version** — fully functional, syntax-aware streaming for C++ code.

The [`distributed-signal-interceptor.cpp`](https://github.com/amirizzuan/hacker-typer/blob/main/distributed-signal-interceptor.cpp) file included is a dummy example (pure Hollywood hacker-ish aesthetics) designed to make people stop and stare at your terminal. The kind of code that makes people wonder if the CIA's about to burst through your window from a helicopter.

## Usage

```bash
python hacker-typer.py <source_file> [chunk_size]
```

Examples:
```bash
python hacker-typer.py distributed-signal-interceptor.cpp          # Default pacing
python hacker-typer.py distributed-signal-interceptor.cpp 1        # Slower (per-character)
python hacker-typer.py distributed-signal-interceptor.cpp 10       # Faster (chunked)
```

Press `Ctrl+C` to stop.

## Features

- Syntax-aware colorization (C++ keywords, operators, digits)
- Configurable streaming speed
- Cinematic terminal effects (random pauses, color-coded output)
- Works with any text-based source file

## Extending

To add language support:
1. Create a new `KEYWORDS_<LANGUAGE>` set in the script
2. Add a `--lang` flag to the CLI
3. Route colorization based on file extension or flag

See the source code comments for more extension ideas.

## License

MIT