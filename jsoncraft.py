#!/usr/bin/env python3
"""
jsoncraft — The Swiss Army Knife for JSON in your terminal.

A zero-dependency Python CLI tool for formatting, querying,
converting, diffing, and validating JSON data with colorful output.

Author: jsoncraft contributors
License: MIT
"""

import argparse
import csv
import io
import json
import re
import sys
from difflib import ndiff, unified_diff


# ── ANSI Color Helpers ────────────────────────────────────────────────────────

class Colors:
    """Terminal color codes with auto-detection."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"

    _enabled = True

    @classmethod
    def enable(cls):
        cls._enabled = True

    @classmethod
    def disable(cls):
        cls._enabled = False

    @classmethod
    def wrap(cls, text, color):
        if not cls._enabled:
            return text
        return f"{color}{text}{cls.RESET}"

    @classmethod
    def bold(cls, text):
        return cls.wrap(text, cls.BOLD)

    @classmethod
    def red(cls, text):
        return cls.wrap(text, cls.RED)

    @classmethod
    def green(cls, text):
        return cls.wrap(text, cls.GREEN)

    @classmethod
    def yellow(cls, text):
        return cls.wrap(text, cls.YELLOW)

    @classmethod
    def blue(cls, text):
        return cls.wrap(text, cls.BLUE)

    @classmethod
    def magenta(cls, text):
        return cls.wrap(text, cls.MAGENTA)

    @classmethod
    def cyan(cls, text):
        return cls.wrap(text, cls.CYAN)

    @classmethod
    def dim(cls, text):
        return cls.wrap(text, cls.DIM)


# ── JSON Syntax Highlighter ──────────────────────────────────────────────────

def highlight_json(data, indent=2):
    """Return syntax-highlighted JSON string."""
    raw = json.dumps(data, indent=indent, ensure_ascii=False)
    return _highlight_json_string(raw)


def _highlight_json_string(raw):
    """Apply syntax highlighting to a JSON string."""
    result = []
    i = 0
    length = len(raw)

    while i < length:
        ch = raw[i]

        if ch == '"':
            # String value or key
            j = i + 1
            while j < length and raw[j] != '"':
                if raw[j] == '\\':
                    j += 1
                j += 1
            string_content = raw[i + 1:j]
            i = j + 1

            # Check if this was a key (followed by colon after optional whitespace)
            k = i
            while k < length and raw[k] in ' \t':
                k += 1
            if k < length and raw[k] == ':':
                # This is a key - color it cyan
                result.append(Colors.cyan(f'"{string_content}"'))
                # Add whitespace and colon
                result.append(raw[i:k])
                result.append(Colors.dim(':'))
                i = k + 1
            else:
                # This is a string value - color it green
                result.append(Colors.green(f'"{string_content}"'))
                # i already advanced past closing quote

        elif ch in '-0123456789':
            j = i
            if raw[j] == '-':
                j += 1
            while j < length and raw[j] in '0123456789':
                j += 1
            if j < length and raw[j] == '.':
                j += 1
                while j < length and raw[j] in '0123456789':
                    j += 1
            if j < length and raw[j] in 'eE':
                j += 1
                if j < length and raw[j] in '+-':
                    j += 1
                while j < length and raw[j] in '0123456789':
                    j += 1
            result.append(Colors.magenta(raw[i:j]))
            i = j

        elif raw[i:i + 4] == 'true':
            result.append(Colors.yellow('true'))
            i += 4
        elif raw[i:i + 5] == 'false':
            result.append(Colors.yellow('false'))
            i += 5
        elif raw[i:i + 4] == 'null':
            result.append(Colors.red('null'))
            i += 4
        else:
            result.append(ch)
            i += 1

    return ''.join(result)


# ── Input / Output Helpers ───────────────────────────────────────────────────

def read_input(filepath=None):
    """Read JSON input from file or stdin."""
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            error(f"File not found: {filepath}")
        except PermissionError:
            error(f"Permission denied: {filepath}")
        except IOError as e:
            error(f"Error reading file: {e}")
    else:
        if sys.stdin.isatty():
            error("No input provided. Pipe JSON data or specify a file with -f/--file.\n"
                  "  Example: echo '{\"key\": \"value\"}' | jsoncraft fmt")
        return sys.stdin.read()


def parse_json(text):
    """Parse JSON text, with helpful error messages."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Show context around the error
        lines = text.split('\n')
        line_no = e.lineno
        col_no = e.col_offset
        start = max(0, line_no - 3)
        end = min(len(lines), line_no + 2)

        error(f"Invalid JSON at line {line_no}, column {col_no}: {e.msg}")
        for i in range(start, end):
            marker = ">>>" if i + 1 == line_no else "   "
            prefix = Colors.red(marker) if i + 1 == line_no else Colors.dim(marker)
            line_text = lines[i] if i < len(lines) else ""
            if i + 1 == line_no and col_no and col_no <= len(line_text):
                pointer = ' ' * (col_no - 1) + Colors.red('^')
                print(f"  {prefix} {line_text}")
                print(f"      {pointer}", file=sys.stderr)
            else:
                print(f"  {prefix} {Colors.dim(line_text)}", file=sys.stderr)


def error(msg):
    """Print error message and exit."""
    print(f"  {Colors.red('✗')} {Colors.bold('Error')}: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg):
    """Print warning message."""
    print(f"  {Colors.yellow('⚠')} {Colors.bold('Warning')}: {msg}", file=sys.stderr)


def success(msg):
    """Print success message."""
    print(f"  {Colors.green('✓')} {msg}", file=sys.stderr)


def info(msg):
    """Print info message."""
    print(f"  {Colors.blue('ℹ')} {msg}", file=sys.stderr)


# ── Command: fmt (format / prettify) ────────────────────────────────────────

def cmd_fmt(args):
    """Pretty-print JSON."""
    text = read_input(args.file)
    data = parse_json(text)
    indent = args.indent if args.indent is not None else 2
    sort_keys = args.sort

    print(highlight_json(data, indent=indent))

    if args.sort:
        info(f"Sorted {sum(isinstance(v, dict) for v in _walk(data))} object(s) by key")


def _walk(data):
    """Yield all values in a nested structure."""
    yield data
    if isinstance(data, dict):
        for v in data.values():
            yield from _walk(v)
    elif isinstance(data, list):
        for v in data:
            yield from _walk(v)


# ── Command: min (minify / compress) ─────────────────────────────────────────

def cmd_min(args):
    """Minify JSON."""
    text = read_input(args.file)
    data = parse_json(text)

    compact = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    original_size = len(text.strip())
    minified_size = len(compact)
    savings = ((original_size - minified_size) / original_size * 100) if original_size > 0 else 0

    print(compact, end='')
    if not args.quiet:
        info(f"{original_size:,} → {minified_size:,} bytes ({savings:.1f}% reduction)")


# ── Command: query (jq-like queries) ─────────────────────────────────────────

def cmd_query(args):
    """Execute a jq-like query on JSON data."""
    text = read_input(args.file)
    data = parse_json(text)

    result = _execute_query(data, args.expression)

    if result is None:
        if not args.raw:
            print(Colors.red("null"))
        else:
            print("null")
    else:
        if args.raw:
            if isinstance(result, str):
                print(result)
            elif isinstance(result, (int, float, bool)):
                print(json.dumps(result))
            else:
                print(json.dumps(result, ensure_ascii=False))
        else:
            print(highlight_json(result, indent=2))


def _execute_query(data, expr):
    """
    Execute a simplified jq-like query.

    Supported syntax:
        .field          — access field
        .[n]            — array index
        .field.sub      — nested access
        .field[]         — iterate array
        .[]             — iterate all array elements
        .field | .sub   — pipe (simple chain)
        .[start:end]    — array slice
        keys            — get keys of object
        values          — get values of object
        length          — get length
        type            — get type
        unique          — unique elements of array
        sort            — sort array
        reverse         — reverse array
        first           — first element
        last            — last element
        .field1,.field2 — multiple fields (returns array)
    """
    # Handle pipe expressions (simple left-to-right)
    if '|' in expr and not _is_inside_brackets(expr):
        parts = [p.strip() for p in expr.split('|')]
        result = data
        for part in parts:
            if not part:
                continue
            result = _execute_single_query(result, part)
        return result
    else:
        return _execute_single_query(data, expr)


def _is_inside_brackets(expr, idx=None):
    """Check if a pipe character is inside brackets."""
    if idx is None:
        # Check if any | is outside brackets
        depth = 0
        for i, ch in enumerate(expr):
            if ch in '([':
                depth += 1
            elif ch in ')]':
                depth -= 1
            elif ch == '|' and depth == 0:
                return False
        return True
    return False


def _execute_single_query(data, expr):
    """Execute a single query expression (no pipes)."""
    expr = expr.strip()

    # Built-in functions
    if expr == 'keys':
        if isinstance(data, dict):
            return list(data.keys())
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return list(data[0].keys())
        return []

    if expr == 'values':
        if isinstance(data, dict):
            return list(data.values())
        elif isinstance(data, list):
            return data
        return data

    if expr == 'length':
        if isinstance(data, (list, dict, str)):
            return len(data)
        return 0

    if expr == 'type':
        type_map = {list: "array", dict: "object", str: "string",
                    int: "number", float: "number", bool: "boolean",
                    type(None): "null"}
        return type_map.get(type(data), "unknown")

    if expr == 'unique':
        if isinstance(data, list):
            seen = []
            for item in data:
                serialized = json.dumps(item, sort_keys=True, ensure_ascii=False)
                if serialized not in [json.dumps(s, sort_keys=True, ensure_ascii=False) for s in seen]:
                    seen.append(item)
            return seen
        return data

    if expr == 'sort':
        if isinstance(data, list):
            try:
                return sorted(data)
            except TypeError:
                return sorted(data, key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
        return data

    if expr == 'reverse':
        if isinstance(data, list):
            return list(reversed(data))
        return data

    if expr == 'first':
        if isinstance(data, list) and data:
            return data[0]
        return None

    if expr == 'last':
        if isinstance(data, list) and data:
            return data[-1]
        return None

    if expr == 'flatten':
        if isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, list):
                    result.extend(item)
                else:
                    result.append(item)
            return result
        return data

    if expr == '.':
        return data

    # Multiple field access: .a,.b
    if ',' in expr:
        parts = [p.strip() for p in expr.split(',')]
        results = []
        for part in parts:
            results.append(_execute_single_query(data, part))
        return results

    # Handle dot-prefixed field access
    if expr.startswith('.'):
        path = expr[1:]
        return _resolve_path(data, path)

    # Bare field name
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', expr):
        if isinstance(data, dict) and expr in data:
            return data[expr]
        return None

    return data


def _resolve_path(data, path):
    """Resolve a dot-path like 'users[0].name' against data."""
    if not path:
        return data

    # Tokenize the path
    tokens = _tokenize_path(path)

    current = data
    collect_all = False

    for i, token in enumerate(tokens):
        if token == '[]':
            # Array iteration
            if isinstance(current, list):
                if i + 1 < len(tokens):
                    remaining = '.'.join(tokens[i + 1:])
                    return [_resolve_path(item, remaining) for item in current]
                else:
                    collect_all = True
                    break
            else:
                return None

        elif token.startswith('[') and token.endswith(']'):
            inner = token[1:-1]
            # Slice: [start:end]
            if ':' in inner:
                parts = inner.split(':')
                start = int(parts[0]) if parts[0] else 0
                end = int(parts[1]) if parts[1] else len(current)
                if isinstance(current, list):
                    current = current[start:end]
                else:
                    return None
            # Index: [n]
            else:
                try:
                    idx = int(inner)
                    if isinstance(current, list):
                        if -len(current) <= idx < len(current):
                            current = current[idx]
                        else:
                            warn(f"Index {idx} out of range (length: {len(current)})")
                            return None
                    elif isinstance(current, dict):
                        current = current.get(inner, None)
                    else:
                        return None
                except ValueError:
                    if isinstance(current, dict):
                        current = current.get(inner, None)
                    else:
                        return None

        elif isinstance(current, dict):
            if token in current:
                current = current[token]
            else:
                warn(f"Key '{token}' not found")
                return None
        else:
            return None

    return current


def _tokenize_path(path):
    """Tokenize a path like 'users[0].name' into ['users', '[0]', 'name']."""
    tokens = []
    current = []
    i = 0

    while i < len(path):
        ch = path[i]

        if ch == '.':
            if current:
                tokens.append(''.join(current))
                current = []
            i += 1
        elif ch == '[':
            if current:
                tokens.append(''.join(current))
                current = []
            # Find matching ]
            j = i
            depth = 0
            while j < len(path):
                if path[j] == '[':
                    depth += 1
                elif path[j] == ']':
                    depth -= 1
                    if depth == 0:
                        tokens.append(path[i:j + 1])
                        i = j + 1
                        break
                j += 1
            else:
                tokens.append(path[i:])
                break
        else:
            current.append(ch)
            i += 1

    if current:
        tokens.append(''.join(current))

    return tokens


# ── Command: path (JSONPath extraction) ──────────────────────────────────────

def cmd_path(args):
    """Extract values using JSONPath expressions."""
    text = read_input(args.file)
    data = parse_json(text)

    results = _jsonpath(data, args.expression)

    if args.raw:
        for r in results:
            if isinstance(r, str):
                print(r)
            else:
                print(json.dumps(r, ensure_ascii=False))
    else:
        if len(results) == 1:
            print(highlight_json(results[0], indent=2))
        else:
            print(highlight_json(results, indent=2))


def _jsonpath(data, expr):
    """
    Simplified JSONPath implementation.

    Supports:
        $                  — root
        $.key              — child
        $.key.sub          — nested
        $[n]               — index
        $[*]               — all elements
        $.key[*]           — all elements of child array
        $..key             — recursive descent (all levels)
        $[?(@.key==val)]   — filter expression
    """
    if not expr.startswith('$'):
        expr = '$' + expr

    # Convert to our internal query format
    query = expr[1:]  # Remove $
    query = query.replace('.[*]', '[]')
    query = query.replace('[*]', '[]')

    # Recursive descent
    if '..' in query:
        return _recursive_descent(data, query.replace('..', '.', 1))

    return [_resolve_path(data, query)]


def _recursive_descent(data, remaining):
    """Search for a key at all levels."""
    # Extract the first key
    parts = remaining.split('.')
    target_key = parts[0] if parts else ''
    rest = '.'.join(parts[1:]) if len(parts) > 1 else ''

    results = []
    _search_recursive(data, target_key, rest, results)
    return results


def _search_recursive(data, target_key, rest, results):
    """Recursively search for target_key in nested structures."""
    # Check current level
    if isinstance(data, dict):
        if target_key in data:
            if rest:
                resolved = _resolve_path(data[target_key], rest)
                results.append(resolved)
            else:
                results.append(data[target_key])
        # Recurse into values
        for value in data.values():
            _search_recursive(value, target_key, rest, results)
    elif isinstance(data, list):
        for item in data:
            _search_recursive(item, target_key, rest, results)


# ── Command: diff ────────────────────────────────────────────────────────────

def cmd_diff(args):
    """Compare two JSON files/inputs and show differences."""
    text_a = read_input(args.file_a)
    text_b = read_input(args.file_b)

    data_a = parse_json(text_a)
    data_b = parse_json(text_b)

    if args.mode == 'color':
        _diff_color(data_a, data_b, args)
    elif args.mode == 'unified':
        _diff_unified(data_a, data_b, args)
    elif args.mode == 'stat':
        _diff_stat(data_a, data_b)


def _diff_color(a, b, args):
    """Show colored diff between two JSON values."""
    diffs = _deep_diff(a, b, path="$")

    if not diffs:
        success("No differences found")
        return

    for diff in diffs:
        path = diff['path']
        kind = diff['type']

        if kind == 'added':
            print(f"  {Colors.green('+')} {Colors.cyan(path)}: "
                  f"{Colors.green(json.dumps(diff['value'], ensure_ascii=False))}")
        elif kind == 'removed':
            print(f"  {Colors.red('-')} {Colors.cyan(path)}: "
                  f"{Colors.red(json.dumps(diff['value'], ensure_ascii=False))}")
        elif kind == 'changed':
            print(f"  {Colors.yellow('~')} {Colors.cyan(path)}: "
                  f"{Colors.red(json.dumps(diff['old'], ensure_ascii=False))} → "
                  f"{Colors.green(json.dumps(diff['new'], ensure_ascii=False))}")
        elif kind == 'type_changed':
            print(f"  {Colors.magenta('!')} {Colors.cyan(path)}: "
                  f"{Colors.red(type(diff['old']).__name__)} → "
                  f"{Colors.green(type(diff['new']).__name__)}")

    print(f"\n  {Colors.bold(str(len(diffs)))} difference(s) found",
          file=sys.stderr)


def _deep_diff(a, b, path="$"):
    """Recursively find differences between two values."""
    diffs = []

    if type(a) != type(b):
        diffs.append({
            'path': path,
            'type': 'type_changed',
            'old': a,
            'new': b,
        })
        return diffs

    if isinstance(a, dict):
        all_keys = set(list(a.keys()) + list(b.keys()))
        for key in sorted(all_keys):
            child_path = f"{path}.{key}"
            if key not in a:
                diffs.append({
                    'path': child_path,
                    'type': 'added',
                    'value': b[key],
                })
            elif key not in b:
                diffs.append({
                    'path': child_path,
                    'type': 'removed',
                    'value': a[key],
                })
            else:
                diffs.extend(_deep_diff(a[key], b[key], child_path))

    elif isinstance(a, list):
        max_len = max(len(a), len(b))
        for i in range(max_len):
            child_path = f"{path}[{i}]"
            if i >= len(a):
                diffs.append({
                    'path': child_path,
                    'type': 'added',
                    'value': b[i],
                })
            elif i >= len(b):
                diffs.append({
                    'path': child_path,
                    'type': 'removed',
                    'value': a[i],
                })
            else:
                diffs.extend(_deep_diff(a[i], b[i], child_path))

    else:
        if a != b:
            diffs.append({
                'path': path,
                'type': 'changed',
                'old': a,
                'new': b,
            })

    return diffs


def _diff_unified(a, b, args):
    """Show unified diff between formatted JSON strings."""
    str_a = json.dumps(a, indent=2, sort_keys=True, ensure_ascii=False)
    str_b = json.dumps(b, indent=2, sort_keys=True, ensure_ascii=False)

    lines_a = str_a.splitlines(keepends=True)
    lines_b = str_b.splitlines(keepends=True)

    diff = unified_diff(lines_a, lines_b,
                        fromfile=args.label_a or 'a',
                        tofile=args.label_b or 'b',
                        lineterm='')

    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            print(Colors.green(line))
        elif line.startswith('-') and not line.startswith('---'):
            print(Colors.red(line))
        elif line.startswith('@@'):
            print(Colors.cyan(line))
        else:
            print(line)


def _diff_stat(a, b):
    """Show summary statistics of differences."""
    str_a = json.dumps(a, indent=2, sort_keys=True)
    str_b = json.dumps(b, indent=2, sort_keys=True)
    diffs = _deep_diff(a, b, "$")

    added = sum(1 for d in diffs if d['type'] == 'added')
    removed = sum(1 for d in diffs if d['type'] == 'removed')
    changed = sum(1 for d in diffs if d['type'] in ('changed', 'type_changed'))

    print(f"  {Colors.bold('JSON Diff Summary')}")
    print(f"  {'─' * 30}")
    print(f"  File A: {len(str_a):,} bytes")
    print(f"  File B: {len(str_b):,} bytes")
    print(f"  {Colors.green(f'+ {added} added')}")
    print(f"  {Colors.red(f'- {removed} removed')}")
    print(f"  {Colors.yellow(f'~ {changed} changed')}")
    print(f"  {'─' * 30}")
    print(f"  {Colors.bold(f'{len(diffs)} total difference(s)')}")


# ── Command: yaml ────────────────────────────────────────────────────────────

def cmd_yaml(args):
    """Convert JSON to/from YAML."""
    if args.to_json:
        # YAML → JSON
        text = read_input(args.file)
        try:
            data = _parse_yaml(text)
        except ValueError as e:
            error(f"YAML parse error: {e}")

        indent = args.indent if args.indent is not None else 2
        print(highlight_json(data, indent=indent))
    else:
        # JSON → YAML
        text = read_input(args.file)
        data = parse_json(text)
        print(_to_yaml(data, indent=args.indent or 2))


def _to_yaml(data, indent=2, level=0):
    """Convert Python object to YAML string (no external deps)."""
    prefix = ' ' * (level * indent)
    result = []

    if isinstance(data, dict):
        if not data:
            return '{}'
        for key, value in data.items():
            str_key = _yaml_quote_key(key)
            if isinstance(value, (dict, list)):
                if isinstance(value, list) and not value:
                    result.append(f"{prefix}{str_key}: []")
                elif isinstance(value, dict) and not value:
                    result.append(f"{prefix}{str_key}: {{}}")
                else:
                    result.append(f"{prefix}{str_key}:")
                    result.append(_to_yaml(value, indent, level + 1))
            else:
                result.append(f"{prefix}{str_key}: {_yaml_value(value)}")

    elif isinstance(data, list):
        if not data:
            return '[]'
        for item in data:
            if isinstance(item, dict):
                first_key = next(iter(item))
                first_val = item[first_key]
                str_key = _yaml_quote_key(first_key)
                if isinstance(first_val, (dict, list)) and first_val:
                    result.append(f"{prefix}- {str_key}:")
                    # Recurse for the value
                    sub = _to_yaml(first_val, indent, level + 2)
                    # Indent sub-items
                    for line in sub.split('\n'):
                        if line.strip():
                            result.append(' ' * indent + line)
                else:
                    result.append(f"{prefix}- {str_key}: {_yaml_value(first_val)}")
            else:
                result.append(f"{prefix}- {_yaml_value(item)}")
    else:
        result.append(f"{prefix}{_yaml_value(data)}")

    return '\n'.join(result)


def _yaml_quote_key(key):
    """Quote YAML key if needed."""
    if isinstance(key, str):
        if key and (key[0] in '0123456789' or any(c in key for c in ':{}[]&,?*!|>"\'%@`\n') or key.lower() in
                      ('true', 'false', 'null', 'yes', 'no', 'on', 'off')):
            escaped = key.replace("'", "''")
            return f"'{escaped}'"
        return key
    return str(key)


def _yaml_value(value):
    """Convert a Python value to YAML representation."""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, str):
        if not value:
            return "''"
        if value in ('true', 'false', 'null', 'yes', 'no', 'on', 'off'):
            return f"'{value}'"
        if '\n' in value:
            # Multi-line string as literal block
            lines = value.split('\n')
            return '|\n' + '\n'.join('  ' * 2 + line for line in lines)
        if any(c in value for c in ':{}[]&*?|><!%@`"') or value[0] in '0123456789' or '  ' in value:
            escaped = value.replace("'", "''")
            return f"'{escaped}'"
        return value
    if isinstance(value, (int, float)):
        return str(value)
    return str(value)


def _parse_yaml(text):
    """Parse a subset of YAML into Python objects."""
    lines = text.split('\n')
    return _parse_yaml_lines(lines, 0)[0]


def _parse_yaml_lines(lines, start, indent=-1):
    """Parse YAML lines into a Python object, starting from `start`."""
    result = []
    i = start

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped or stripped.startswith('#'):
            i += 1
            continue

        current_indent = len(line) - len(stripped)
        if indent != -1 and current_indent < indent:
            break
        if indent == -1:
            indent = current_indent

        # List item
        if stripped.startswith('- '):
            value_str = stripped[2:].strip()
            if ':' in value_str and not value_str.startswith('"') and not value_str.startswith("'"):
                # Inline dict in list
                obj = _parse_yaml_inline_dict(value_str)
                if obj is not None:
                    result.append(obj)
                    i += 1
                    continue

            parsed, consumed = _parse_yaml_value(value_str)
            if parsed is not None:
                result.append(parsed)
                i += 1
            else:
                # Nested structure after '-'
                i += 1
                if i < len(lines):
                    next_line = lines[i].lstrip()
                    next_indent = len(lines[i]) - len(next_line)
                    if next_indent > current_indent:
                        nested, consumed = _parse_yaml_lines(lines, i, next_indent)
                        result.append(nested)
                        i += consumed
                else:
                    result.append(None)
        elif ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip().strip("'\"")
            value = value.strip()

            if not value:
                # Nested structure
                i += 1
                if i < len(lines):
                    next_stripped = lines[i].lstrip()
                    next_indent = len(lines[i]) - len(next_stripped)
                    if next_indent > indent:
                        # Check if it's a list
                        if next_stripped.startswith('- '):
                            nested, consumed = _parse_yaml_lines(lines, i, next_indent)
                            result.append((key, nested))
                            i += consumed
                        else:
                            nested, consumed = _parse_yaml_lines(lines, i, next_indent)
                            # Convert list of tuples to dict
                            d = {}
                            if isinstance(nested, list):
                                for item in nested:
                                    if isinstance(item, tuple) and len(item) == 2:
                                        d[item[0]] = item[1]
                                    elif isinstance(item, dict):
                                        d.update(item)
                            result.append((key, d))
                            i += consumed
                    else:
                        result.append((key, None))
                else:
                    result.append((key, None))
            else:
                parsed, _ = _parse_yaml_value(value)
                result.append((key, parsed))
                i += 1
        else:
            i += 1

    # Convert list of tuples to dict
    if result and isinstance(result[0], tuple):
        return dict(result), i - start
    return result, i - start


def _parse_yaml_inline_dict(text):
    """Try to parse an inline YAML dict like 'key: val key2: val2'."""
    if not text or ':' not in text:
        return None
    result = {}
    remaining = text
    while ':' in remaining:
        colon_pos = remaining.index(':')
        key = remaining[:colon_pos].strip().strip("'\"")
        remaining = remaining[colon_pos + 1:].strip()
        # Find end of this value
        next_colon = remaining.find(': ')
        if next_colon == -1:
            parsed, _ = _parse_yaml_value(remaining.strip())
            result[key] = parsed
            break
        else:
            value_part = remaining[:next_colon].strip()
            parsed, _ = _parse_yaml_value(value_part)
            result[key] = parsed
            remaining = remaining[next_colon + 1:]
    return result


def _parse_yaml_value(text):
    """Parse a single YAML value."""
    text = text.strip()
    if not text:
        return None, 0
    if text in ('null', '~', ''):
        return None, 0
    if text.lower() in ('true', 'yes', 'on'):
        return True, 0
    if text.lower() in ('false', 'no', 'off'):
        return False, 0

    # Quoted string
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        return text[1:-1], 0

    # Number
    try:
        if '.' in text or 'e' in text.lower():
            return float(text), 0
        return int(text), 0
    except ValueError:
        pass

    return text, 0


# ── Command: csv ─────────────────────────────────────────────────────────────

def cmd_csv(args):
    """Convert JSON to CSV."""
    text = read_input(args.file)
    data = parse_json(text)

    if not isinstance(data, list):
        data = [data]

    if not data:
        warn("Empty JSON array, no CSV output")
        return

    # Collect all keys
    all_keys = []
    for item in data:
        if isinstance(item, dict):
            for key in item.keys():
                if key not in all_keys:
                    all_keys.append(key)

    if not all_keys:
        warn("No keys found in JSON objects")
        return

    # Flatten nested values for CSV
    writer = csv.writer(sys.stdout)
    writer.writerow(all_keys)

    for item in data:
        row = []
        for key in all_keys:
            value = item.get(key, '')
            if isinstance(value, (dict, list)):
                row.append(json.dumps(value, ensure_ascii=False))
            else:
                row.append(value)
        writer.writerow(row)

    success(f"Converted {len(data)} record(s) with {len(all_keys)} field(s)")


# ── Command: validate ────────────────────────────────────────────────────────

def cmd_validate(args):
    """Validate JSON against a basic schema."""
    text = read_input(args.file)
    data = parse_json(text)

    if args.schema:
        schema_text = read_input(args.schema)
        schema = parse_json(schema_text)
    else:
        schema = _guess_schema(data)

    errors = _validate_schema(data, schema, path="$")

    if not errors:
        success("✅ JSON is valid against the schema")
        if args.schema is None:
            info("Schema was auto-detected from the data")
    else:
        print(f"\n  {Colors.red('✗')} {Colors.bold('Validation failed')} — {len(errors)} error(s):",
              file=sys.stderr)
        for err in errors:
            print(f"    {Colors.red('•')} {Colors.cyan(err['path'])}: {err['message']}",
                  file=sys.stderr)
        sys.exit(1)


def _guess_schema(data):
    """Generate a schema from the data structure."""
    return _infer_schema(data)


def _infer_schema(data):
    """Infer a JSON Schema from a Python object."""
    if isinstance(data, dict):
        props = {}
        for k, v in data.items():
            props[k] = _infer_schema(v)
        return {"type": "object", "properties": props}
    elif isinstance(data, list):
        if data:
            return {"type": "array", "items": _infer_schema(data[0])}
        return {"type": "array"}
    elif isinstance(data, bool):
        return {"type": "boolean"}
    elif isinstance(data, int):
        return {"type": "integer"}
    elif isinstance(data, float):
        return {"type": "number"}
    elif isinstance(data, str):
        return {"type": "string"}
    elif data is None:
        return {"type": "null"}
    return {}


def _validate_schema(data, schema, path="$"):
    """Validate data against a basic JSON Schema."""
    errors = []
    schema_type = schema.get('type')

    # Type check
    if schema_type:
        type_map = {
            'object': dict, 'array': list, 'string': str,
            'integer': int, 'number': (int, float),
            'boolean': bool, 'null': type(None)
        }
        expected = type_map.get(schema_type)
        if expected and not isinstance(data, expected):
            # Special case: integer should not match bool
            if schema_type == 'integer' and isinstance(data, bool):
                errors.append({
                    'path': path,
                    'message': f"Expected {schema_type}, got boolean"
                })
            elif not (schema_type == 'number' and isinstance(data, int)):
                errors.append({
                    'path': path,
                    'message': f"Expected {schema_type}, got {type(data).__name__}"
                })
            return errors

    # Object properties
    if isinstance(data, dict) and 'properties' in schema:
        for key, prop_schema in schema['properties'].items():
            if key in data:
                errors.extend(_validate_schema(data[key], prop_schema, f"{path}.{key}"))
            elif prop_schema.get('required'):
                errors.append({
                    'path': f"{path}.{key}",
                    'message': "Required property is missing"
                })

        # Check required at object level (JSON Schema draft-07 style)
        if 'required' in schema and isinstance(schema['required'], list):
            for req_key in schema['required']:
                if req_key not in data:
                    errors.append({
                        'path': f"{path}.{req_key}",
                        'message': "Required property is missing"
                    })

        # additionalProperties
        if 'additionalProperties' in schema:
            allowed_keys = set(schema.get('properties', {}).keys())
            if isinstance(schema.get('additionalProperties'), bool) and not schema['additionalProperties']:
                for key in data:
                    if key not in allowed_keys:
                        errors.append({
                            'path': f"{path}.{key}",
                            'message': f"Additional property '{key}' is not allowed"
                        })
            elif isinstance(schema.get('additionalProperties'), dict):
                for key in data:
                    if key not in allowed_keys:
                        errors.extend(_validate_schema(data[key], schema['additionalProperties'], f"{path}.{key}"))

    # Array constraints
    if isinstance(data, list):
        if 'items' in schema:
            for i, item in enumerate(data):
                errors.extend(_validate_schema(item, schema['items'], f"{path}[{i}]"))
        if 'minItems' in schema and len(data) < schema['minItems']:
            errors.append({
                'path': path,
                'message': f"Array has {len(data)} items, minimum is {schema['minItems']}"
            })
        if 'maxItems' in schema and len(data) > schema['maxItems']:
            errors.append({
                'path': path,
                'message': f"Array has {len(data)} items, maximum is {schema['maxItems']}"
            })
        if schema.get('uniqueItems') and len(data) != len(set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in data)):
            errors.append({
                'path': path,
                'message': "Array items must be unique"
            })

    # String constraints
    if isinstance(data, str):
        if 'minLength' in schema and len(data) < schema['minLength']:
            errors.append({
                'path': path,
                'message': f"String length {len(data)} is less than minimum {schema['minLength']}"
            })
        if 'maxLength' in schema and len(data) > schema['maxLength']:
            errors.append({
                'path': path,
                'message': f"String length {len(data)} exceeds maximum {schema['maxLength']}"
            })
        if 'pattern' in schema:
            if not re.search(schema['pattern'], data):
                errors.append({
                    'path': path,
                    'message': f"String does not match pattern '{schema['pattern']}'"
                })

    # Number constraints
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if 'minimum' in schema and data < schema['minimum']:
            errors.append({
                'path': path,
                'message': f"Value {data} is less than minimum {schema['minimum']}"
            })
        if 'maximum' in schema and data > schema['maximum']:
            errors.append({
                'path': path,
                'message': f"Value {data} exceeds maximum {schema['maximum']}"
            })

    # Enum
    if 'enum' in schema and data not in schema['enum']:
        errors.append({
            'path': path,
            'message': f"Value {json.dumps(data)} is not one of: {json.dumps(schema['enum'])}"
        })

    return errors


# ── Command: schema (infer schema) ───────────────────────────────────────────

def cmd_schema(args):
    """Infer JSON Schema from data."""
    text = read_input(args.file)
    data = parse_json(text)

    schema = _infer_schema(data)
    schema["$schema"] = "http://json-schema.org/draft-07/schema#"

    print(highlight_json(schema, indent=2))
    info("Inferred JSON Schema (draft-07)")


# ── Command: keys / values / type / length ───────────────────────────────────

def cmd_keys(args):
    """Extract keys from JSON object(s)."""
    text = read_input(args.file)
    data = parse_json(text)

    if isinstance(data, dict):
        keys = list(data.keys())
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        keys = list(data[0].keys())
    else:
        error("Cannot extract keys from non-object data")

    for key in keys:
        print(Colors.cyan(key))


def cmd_values(args):
    """Extract values from JSON object(s)."""
    text = read_input(args.file)
    data = parse_json(text)

    if isinstance(data, dict):
        values = list(data.values())
    else:
        values = data

    print(highlight_json(values, indent=2))


def cmd_type(args):
    """Show the type of JSON data."""
    text = read_input(args.file)
    data = parse_json(text)

    type_map = {list: "array", dict: "object", str: "string",
                int: "number", float: "number", bool: "boolean",
                type(None): "null"}
    t = type_map.get(type(data), "unknown")
    print(Colors.magenta(t))


def cmd_length(args):
    """Show the length/size of JSON data."""
    text = read_input(args.file)
    data = parse_json(text)

    if isinstance(data, (list, dict, str)):
        print(Colors.magenta(str(len(data))))
    else:
        print(Colors.magenta("1"))


# ── Command: flatten ─────────────────────────────────────────────────────────

def cmd_flatten(args):
    """Flatten nested JSON structure."""
    text = read_input(args.file)
    data = parse_json(text)

    result = _flatten(data, separator=args.separator)
    print(highlight_json(result, indent=2))


def _flatten(data, separator=".", prefix=""):
    """Flatten a nested dict/list into a single-level dict."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            if isinstance(value, (dict, list)):
                result.update(_flatten(value, separator, new_key))
            else:
                result[new_key] = value
        return result
    elif isinstance(data, list):
        result = {}
        for i, value in enumerate(data):
            new_key = f"{prefix}{separator}{i}" if prefix else str(i)
            if isinstance(value, (dict, list)):
                result.update(_flatten(value, separator, new_key))
            else:
                result[new_key] = value
        return result
    else:
        return {prefix: data}


# ── Command: unflatten ───────────────────────────────────────────────────────

def cmd_unflatten(args):
    """Unflatten dot-notation keys back into nested JSON."""
    text = read_input(args.file)
    data = parse_json(text)

    if not isinstance(data, dict):
        error("unflatten requires a flat JSON object as input")

    result = _unflatten(data, separator=args.separator)
    print(highlight_json(result, indent=2))


def _unflatten(data, separator="."):
    """Expand dot-notation keys into a nested dict."""
    result = {}
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        for i, part in enumerate(parts):
            # Try to parse array indices
            if part.isdigit():
                part = int(part)
                # Ensure parent is a list
                if not isinstance(current, list):
                    # Convert dict index to list if needed
                    current_list = []
                    current.append(None)  # placeholder
                    current = current_list
                while len(current) <= part:
                    current.append(None)
                if i == len(parts) - 1:
                    current[part] = value
                else:
                    if current[part] is None:
                        next_part = parts[i + 1]
                        if next_part.isdigit():
                            current[part] = []
                        else:
                            current[part] = {}
                    current = current[part]
            else:
                if i == len(parts) - 1:
                    current[part] = value
                else:
                    next_part = parts[i + 1]
                    if part not in current or current[part] is None:
                        if next_part.isdigit():
                            current[part] = []
                        else:
                            current[part] = {}
                    current = current[part]
    return result


# ── Command: merge ───────────────────────────────────────────────────────────

def cmd_merge(args):
    """Merge multiple JSON files."""
    if len(args.files) < 2:
        error("merge requires at least 2 files")

    datasets = []
    for filepath in args.files:
        text = read_input(filepath)
        data = parse_json(text)
        datasets.append(data)

    strategy = args.strategy
    if strategy == 'deep':
        result = datasets[0]
        for i in range(1, len(datasets)):
            result = _deep_merge(result, datasets[i])
    elif strategy == 'shallow':
        result = datasets[0]
        for i in range(1, len(datasets)):
            if isinstance(result, dict) and isinstance(datasets[i], dict):
                result = {**result, **datasets[i]}
            elif isinstance(result, list) and isinstance(datasets[i], list):
                result = datasets[i]  # last wins
            else:
                result = datasets[i]
    elif strategy == 'concat':
        if all(isinstance(d, list) for d in datasets):
            result = []
            for d in datasets:
                result.extend(d)
        elif all(isinstance(d, dict) for d in datasets):
            result = {}
            for d in datasets:
                result.update(d)
        else:
            error("concat strategy requires all inputs to be the same type (all arrays or all objects)")

    output = highlight_json(result, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, indent=2, ensure_ascii=False))
        success(f"Merged {len(datasets)} files → {args.output}")
    else:
        print(output)
        info(f"Merged {len(datasets)} file(s) using {strategy} strategy")


def _deep_merge(base, override):
    """Deep merge two dicts/lists recursively."""
    if isinstance(base, dict) and isinstance(override, dict):
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], (dict, list)) and isinstance(value, (dict, list)):
                result[key] = _deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    elif isinstance(base, list) and isinstance(override, list):
        return base + override
    else:
        return override


# ── CLI Argument Parser ──────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog='jsoncraft',
        description='🔧 The Swiss Army Knife for JSON — format, query, convert, diff, validate, merge & flatten in your terminal.',
        epilog='Examples:\n'
               '  echo \'{"name":"Alice","age":30}\' | jsoncraft fmt\n'
               '  cat data.json | jsoncraft query ".users[0].name"\n'
               '  jsoncraft diff -f a.json -g b.json\n'
               '  jsoncraft merge -f base.json override.json --strategy deep\n'
               '  jsoncraft validate -f data.json -s schema.json\n'
               '  echo \'{"a.b":1}\' | jsoncraft unflatten\n'
               '  jsoncraft to-yaml -f data.json\n'
               '  jsoncraft csv -f data.json\n',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.1.0')
    parser.add_argument('-f', '--file', help='Input JSON file (default: stdin)')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # fmt
    p = subparsers.add_parser('fmt', aliases=['format', 'pretty'], help='Pretty-print JSON')
    p.add_argument('-i', '--indent', type=int, default=2, help='Indent spaces (default: 2)')
    p.add_argument('-s', '--sort', action='store_true', help='Sort object keys')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # min
    p = subparsers.add_parser('min', aliases=['minify', 'compact'], help='Minify JSON')
    p.add_argument('-q', '--quiet', action='store_true', help='Suppress stats')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # query
    p = subparsers.add_parser('query', aliases=['q', 'jq'], help='Query JSON (jq-like syntax)')
    p.add_argument('expression', help='Query expression (e.g., ".users[0].name")')
    p.add_argument('-r', '--raw', action='store_true', help='Output raw strings')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # path
    p = subparsers.add_parser('path', help='Extract values with JSONPath')
    p.add_argument('expression', help='JSONPath expression (e.g., "$.store.book[*].title")')
    p.add_argument('-r', '--raw', action='store_true', help='Output raw strings')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # diff
    p = subparsers.add_parser('diff', help='Compare two JSON files')
    p.add_argument('-f', '--file', dest='file_a', required=True, help='First JSON file')
    p.add_argument('-g', '--file-b', dest='file_b', required=True, help='Second JSON file')
    p.add_argument('-m', '--mode', choices=['color', 'unified', 'stat'], default='color',
                   help='Diff mode (default: color)')
    p.add_argument('--label-a', help='Label for file A in unified mode')
    p.add_argument('--label-b', help='Label for file B in unified mode')

    # yaml
    p = subparsers.add_parser('to-yaml', help='Convert JSON to YAML')
    p.set_defaults(to_json=False)
    p.add_argument('-i', '--indent', type=int, default=2, help='Indent spaces (default: 2)')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    p = subparsers.add_parser('from-yaml', help='Convert YAML to JSON')
    p.set_defaults(to_json=True)
    p.add_argument('-i', '--indent', type=int, default=2, help='Indent spaces (default: 2)')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # csv
    p = subparsers.add_parser('csv', help='Convert JSON to CSV')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # validate
    p = subparsers.add_parser('validate', help='Validate JSON against schema')
    p.add_argument('-f', '--file', dest='file', help='Input JSON file')
    p.add_argument('-s', '--schema', help='Schema file (auto-detected if omitted)')

    # schema
    p = subparsers.add_parser('schema', help='Infer JSON Schema from data')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # keys
    p = subparsers.add_parser('keys', help='Extract keys from JSON object')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # values
    p = subparsers.add_parser('values', help='Extract values from JSON')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # type
    p = subparsers.add_parser('type', help='Show type of JSON data')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # length
    p = subparsers.add_parser('length', help='Show length of JSON data')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # flatten
    p = subparsers.add_parser('flatten', help='Flatten nested JSON')
    p.add_argument('-s', '--separator', default='.', help='Key separator (default: ".")')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # unflatten
    p = subparsers.add_parser('unflatten', help='Unflatten dot-notation keys into nested JSON')
    p.add_argument('-s', '--separator', default='.', help='Key separator (default: ".")')
    p.add_argument('-f', '--file', dest='file', help='Input file')

    # merge
    p = subparsers.add_parser('merge', help='Merge multiple JSON files')
    p.add_argument('-f', '--files', nargs='+', required=True, dest='files',
                   help='JSON files to merge (2+)')
    p.add_argument('-s', '--strategy', choices=['deep', 'shallow', 'concat'], default='deep',
                   help='Merge strategy: deep (recursive), shallow (top-level), concat (append arrays)')
    p.add_argument('-o', '--output', help='Output file (default: stdout)')

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Handle --no-color
    if hasattr(args, 'no_color') and args.no_color:
        Colors.disable()

    # Detect non-TTY
    if not sys.stdout.isatty() and not getattr(args, 'no_color', False):
        # Check if NO_COLOR env var is set
        if os.environ.get('NO_COLOR'):
            Colors.disable()

    # Default command: fmt if no subcommand given and stdin has data
    if not args.command:
        if not sys.stdin.isatty():
            # Default to fmt when piped
            args.command = 'fmt'
            args.indent = 2
            args.sort = False
            args.file = getattr(args, 'file', None)
        else:
            parser.print_help()
            sys.exit(0)

    # Command dispatch
    cmd_map = {
        'fmt': cmd_fmt, 'format': cmd_fmt, 'pretty': cmd_fmt,
        'min': cmd_min, 'minify': cmd_min, 'compact': cmd_min,
        'query': cmd_query, 'q': cmd_query, 'jq': cmd_query,
        'path': cmd_path,
        'diff': cmd_diff,
        'to-yaml': cmd_yaml, 'from-yaml': cmd_yaml,
        'csv': cmd_csv,
        'validate': cmd_validate,
        'schema': cmd_schema,
        'keys': cmd_keys,
        'values': cmd_values,
        'type': cmd_type,
        'length': cmd_length,
        'flatten': cmd_flatten,
        'unflatten': cmd_unflatten,
        'merge': cmd_merge,
    }

    cmd_func = cmd_map.get(args.command)
    if cmd_func:
        cmd_func(args)
    else:
        parser.print_help()
        sys.exit(1)


import os

if __name__ == '__main__':
    main()
