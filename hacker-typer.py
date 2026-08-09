#!/usr/bin/env python3
"""
Hacker Typer - Cinematic Code Streaming Visualizer
A terminal-based tool that streams source code with syntax-aware colorization.

Features:
  - Real-time syntax highlighting (C++ keywords, special chars, digits)
  - Configurable streaming speed
  - Cinematic terminal effects (random pauses, color-coded output)
  - Keyboard interrupt handling
  - Support for any text-based source file

Usage:
  python hacker-typer.py <source_file> [chunk_size]

Author: amirizzuan
License: MIT
Repository: https://github.com/amirizzuan/hacker-typer
"""

import sys
import time
import random

# ==========
# ANSI Color Codes for Terminal Output
# ==========
# These escape sequences control text color in POSIX-compliant terminals.
# Format: \033[<code>m where code determines the color
# Note: Not all terminals support these codes; most modern terminals do.
GREEN = "\033[92m"      # Standard identifiers and regular text
CYAN = "\033[96m"       # Special characters (operators, brackets, etc)
AMBER = "\033[93m"      # Reserved keywords (language-specific)
MAGENTA = "\033[95m"    # Numeric literals
RED = "\033[91m"        # Error/termination messages
RESET = "\033[0m"       # Reset to default terminal color

# ==========
# Character Classifications
# ==========
# SPECIAL_CHARS: Symbols that require unique colorization
# These represent operators, delimiters, and punctuation in source code.
# Treat any char in this set as a token boundary + color it CYAN.
SPECIAL_CHARS = set("<>;()[]{}*&^%$#@!~`|\\/?.,:+-=")

# ==========
# C++ Reserved Keywords (Core Set - C++98 Compatible)
# ==========
# This set contains keywords available across all C++ standards from C++98
# through C++20. Keywords are language-reserved identifiers and cannot be
# used as variable/function names.
#
# Organized by category for readability:
#   - Storage class: control variable lifetime and linkage
#   - Type specifiers: define primitive data types
#   - Type modifiers: add compile-time constraints (const, volatile)
#   - Control flow: conditionals and loops
#   - OOP: class-based and encapsulation features
#   - Templates: generic programming support
#   - Exception handling: error management
#   - Namespaces: code organization and scope
#   - Other: utility keywords (sizeof, nullptr, etc)
#
# To extend this for other languages:
#   1. Create a new KEYWORDS_<LANGUAGE> set
#   2. Modify the colorization logic to accept language parameter
#   3. Add command-line flag: --lang cpp|python|java|etc
KEYWORDS = {
    # Storage class specifiers (memory and scope)
    "auto", "register", "static", "extern", "mutable",
    
    # Type specifiers (primitive types)
    "void", "char", "short", "int", "long", "float", "double",
    "signed", "unsigned", "bool",
    
    # Type modifiers (compile-time constraints)
    "const", "volatile",
    
    # Control flow (conditionals and loops)
    "if", "else", "switch", "case", "default",
    "for", "while", "do", "break", "continue", "goto", "return",
    
    # Object-oriented programming
    "class", "struct", "union", "enum",
    "public", "private", "protected",
    "virtual", "friend", "this", "operator",
    
    # Templates (generic programming)
    "template", "typename",
    
    # Exception handling
    "try", "catch", "throw",
    
    # Namespaces (code organization)
    "namespace", "using",
    
    # Other utility keywords
    "sizeof", "typeid", "inline", "asm",
    "nullptr", "true", "false"
}


class HackerTyper:
    """
    Main class for streaming and colorizing source code.
    
    This class handles:
      - File I/O (reading source files)
      - Tokenization (splitting code into meaningful units)
      - Syntax-aware colorization (keywords, operators, literals)
      - Streaming output (character-by-character with timing)
      - Terminal effects (random pauses for cinematic feel)
    
    Attributes:
        filepath (str): Path to the source file to stream
        chunk_size (int): Number of characters to process per iteration
        counter (int): Tracks loop iterations (for statistics/debugging)
        buffer (str): Accumulates alphanumeric chars until a token boundary
    """
    
    def __init__(self, filepath, chunk_size=3):
        """
        Initialize the HackerTyper instance.
        
        Args:
            filepath (str): Path to source file to stream
            chunk_size (int): Number of characters to read per batch.
                             Lower = finer control, Higher = faster streaming.
                             Default 3 provides ~cinematic~ pacing.
        """
        self.filepath = filepath
        self.chunk_size = chunk_size
        self.counter = 0          # Loop iteration counter (useful for benchmarking)
        self.buffer = ""          # Holds incomplete tokens (identifiers/keywords)

    def read_file(self):
        """
        Read source file with proper error handling.
        
        Returns:
            str: Complete file contents as a single string
            
        Raises:
            SystemExit: On FileNotFoundError or PermissionError
            
        Note:
            Uses UTF-8 encoding to support international characters and emojis.
            Modify encoding parameter if working with legacy ASCII/Latin-1 files.
        """
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {self.filepath}")
            sys.exit(1)
        except PermissionError:
            print(f"Error: Permission denied: {self.filepath}")
            sys.exit(1)

    def run(self):
        """
        Main execution loop: stream file contents with colorization.
        
        Algorithm:
            1. Read entire file into memory
            2. Loop forever (user breaks with Ctrl+C)
            3. For each character in file:
               a. If digit: flush buffer, color MAGENTA
               b. If alphanumeric/_: accumulate in buffer (building token)
               c. If special char/whitespace: flush buffer as keyword or identifier
               d. Color output based on character type
               e. Add small delay for cinematic effect
            4. After file completes: pause and restart loop
            5. Catch KeyboardInterrupt for graceful shutdown
        
        Colorization Rules:
            - Keyword (in KEYWORDS set)  → AMBER
            - Identifier (alphanumeric)  → GREEN
            - Operator/bracket           → CYAN
            - Digit                      → MAGENTA
            - Whitespace/other           → GREEN (default)
        
        Timing:
            - Base delay: 0.005s per character (200 chars/sec)
            - Chunk delay: 0.01s per chunk (cinematic breathing)
            - Random stutter: 1% chance of 1s pause (connection hiccup effect)
            - Loop restart: 0.5s pause between file cycles
            
        Extension Ideas:
            - Add --speed flag to adjust base delay
            - Implement file rotation (multiple files in sequence)
            - Add statistics (lines/sec, chars colored, etc)
            - Support stdin input (pipe from other commands)
            - Add logging to file for playback/review
        """
        code = self.read_file()

        # Print startup message with color
        print(f"\n{AMBER}[*] Streaming... Press Ctrl+C to quit{RESET}\n")

        try:
            # Infinite loop: restart file when complete (cinema mode)
            while True:
                # Process file in chunks (batch reading)
                for i in range(0, len(code), self.chunk_size):
                    chunk = code[i:i + self.chunk_size]

                    # Process each character in chunk
                    for char in chunk:
                        # --- DIGIT HANDLING (check FIRST) ---
                        # Digits must be checked before isalnum() because
                        # isalnum() returns True for digits, which would
                        # incorrectly route them into the buffer.
                        if char.isdigit():
                            # Flush any accumulated buffer first
                            if self.buffer:
                                if self.buffer in KEYWORDS:
                                    sys.stdout.write(f"{AMBER}{self.buffer}{RESET}")
                                else:
                                    sys.stdout.write(f"{GREEN}{self.buffer}{RESET}")
                                self.buffer = ""
                            # Color the digit MAGENTA
                            sys.stdout.write(f"{MAGENTA}{char}{RESET}")
                        
                        # --- TOKEN ACCUMULATION PHASE ---
                        # Build tokens from alphanumeric sequences
                        elif char.isalnum() or char == "_":
                            # Part of identifier or keyword → accumulate
                            self.buffer += char
                        
                        else:
                            # --- TOKEN FLUSH PHASE ---
                            # Hit a token boundary (non-alphanumeric)
                            # Flush accumulated buffer with appropriate color
                            
                            if self.buffer:
                                # Check if accumulated token is a keyword
                                if self.buffer in KEYWORDS:
                                    # Keyword found → color AMBER
                                    sys.stdout.write(f"{AMBER}{self.buffer}{RESET}")
                                else:
                                    # Regular identifier → color GREEN
                                    sys.stdout.write(f"{GREEN}{self.buffer}{RESET}")
                                self.buffer = ""  # Reset buffer for next token

                            # --- SPECIAL CHARACTER HANDLING ---
                            # Now process the boundary character itself
                            
                            if char in SPECIAL_CHARS:
                                # Operator or bracket → color CYAN
                                sys.stdout.write(f"{CYAN}{char}{RESET}")
                            else:
                                # Whitespace, newlines, comments → default GREEN
                                # This keeps code readable while preserving structure
                                sys.stdout.write(f"{GREEN}{char}{RESET}")

                        # Flush stdout immediately (don't buffer terminal output)
                        # Ensures smooth streaming appearance
                        sys.stdout.flush()
                        
                        # Cinematic pacing: small delay per character
                        # Lower values = faster/more intense
                        # Higher values = slower/more deliberate
                        # 0.005s ≈ 200 chars/sec (reasonable hacker speed)
                        time.sleep(0.005)

                    # Delay between chunks (cinematic breathing)
                    # Gives the impression of thinking/processing
                    time.sleep(0.01)

                    # Random stutter effect: 1-in-100 chance of longer pause
                    # Creates unpredictable "connection lag" feel
                    # Remove this if you want consistent pacing
                    if random.randint(1, 100) == 1:
                        time.sleep(1)

                    # Increment counter for optional statistics
                    self.counter += 1

                # --- END OF FILE ---
                # Add spacing and pause before restarting file
                sys.stdout.write(f"\n\n")
                sys.stdout.flush()
                time.sleep(0.5)

        # --- GRACEFUL SHUTDOWN ---
        # Catch Ctrl+C and display termination message
        except KeyboardInterrupt:
            print(f"\n\n{RED}[!] CONNECTION TERMINATED{RESET}\n")
            sys.exit(0)


def main():
    """
    Entry point: parse command-line arguments and start streaming.
    
    Arguments:
        <source_file>  : Path to source code file (required)
        [chunk_size]   : Characters per batch, default 3 (optional)
    
    Examples:
        python hacker-typer.py main.cpp
        python hacker-typer.py main.cpp 1      # Slower (per-char)
        python hacker-typer.py main.cpp 10     # Faster (larger chunks)
    
    Future Enhancement Ideas:
        - Add --lang flag for language-specific keywords
        - Add --speed flag to override timing globally
        - Add --no-loop flag (stream once, exit)
        - Add --stats flag (show performance metrics)
        - Add --output flag (save output to file)
        - Add --theme flag (preset color schemes)
        - Support reading from stdin (pipe support)
    """
    
    # --- ARGUMENT VALIDATION ---
    if len(sys.argv) < 2:
        print("Usage: python hacker-typer.py <source_file> [chunk_size]")
        print()
        print("Arguments:")
        print("  source_file : Path to source code file (required)")
        print("  chunk_size  : Characters per batch [1-10], default 3 (optional)")
        print()
        print("Examples:")
        print("  python hacker-typer.py source.cpp")
        print("  python hacker-typer.py source.cpp 1")
        print("  python hacker-typer.py source.cpp 5")
        print()
        print("Tips:")
        print("  - Lower chunk_size = slower, more controlled streaming")
        print("  - Higher chunk_size = faster, more intense streaming")
        print("  - Press Ctrl+C to stop streaming anytime")
        sys.exit(1)

    filepath = sys.argv[1]
    chunk_size = 3  # Default chunk size (cinematic default)

    # --- OPTIONAL ARGUMENT PARSING ---
    # Parse chunk_size if provided as second argument
    if len(sys.argv) > 2:
        try:
            chunk_size = int(sys.argv[2])
        except ValueError:
            # User provided non-integer chunk_size
            print("Error: chunk_size must be an integer.")
            sys.exit(1)

    # --- VALIDATION ---
    # Ensure chunk_size is positive (0 or negative would cause infinite loop)
    if chunk_size < 1:
        print("Error: chunk_size must be 1 or greater.")
        sys.exit(1)

    # --- EXECUTION ---
    # Create instance and begin streaming
    typer = HackerTyper(filepath, chunk_size)
    typer.run()


# ==========
# SCRIPT ENTRY POINT
# ==========
# Standard Python idiom: only run main() if this file is executed directly,
# not if imported as a module in another script.
if __name__ == "__main__":
    main()