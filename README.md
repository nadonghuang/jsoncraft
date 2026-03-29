# 🔧 jsoncraft

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-orange)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

**The Swiss Army Knife for JSON in your terminal.**

A zero-dependency Python CLI tool for formatting, querying, converting, diffing, and validating JSON data — with beautiful colored output.

## ✨ Features

- 🎨 **Format & Minify** — Pretty-print or compress JSON with syntax highlighting
- 🔍 **jq-like Queries** — Simplified query syntax (`.users[0].name`, `.items[]`, pipes)
- 🔄 **JSON ↔ YAML** — Bidirectional conversion, no external libs needed
- ⚡ **JSONPath** — Extract values with JSONPath expressions
- 📊 **JSON Diff** — Compare two JSON files with colored or unified diff
- ✅ **Schema Validation** — Validate against JSON Schema or auto-infer schema
- 📄 **JSON → CSV** — Convert JSON arrays to CSV format
- 🔧 **Flatten** — Flatten nested structures into dot-notation keys
- 🌈 **Colored Output** — Beautiful syntax highlighting out of the box
- 📦 **Zero Dependencies** — Pure Python standard library, pip install not even required

## 📦 Installation

```bash
# Clone and use directly
git clone https://github.com/nadonghuang/jsoncraft.git
cd jsoncraft
chmod +x jsoncraft.py

# Or download single file
curl -O https://raw.githubusercontent.com/nadonghuang/jsoncraft/main/jsoncraft.py
chmod +x jsoncraft.py

# Optional: add to PATH
sudo ln -s $(pwd)/jsoncraft.py /usr/local/bin/jsoncraft
```

No `pip install` needed — it's a single file with zero dependencies!

## 🚀 Usage Examples

### 1. Pretty-print JSON

```bash
echo '{"name":"Alice","age":30,"skills":["Python","JSON"]}' | python jsoncraft.py fmt
```

```
{
  "name": "Alice",
  "age": 30,
  "skills": [
    "Python",
    "JSON"
  ]
}
```

### 2. Query with jq-like Syntax

```bash
cat users.json | python jsoncraft.py query ".users[0].name"
# Output: "Alice"

cat users.json | python jsoncraft.py query ".users[].email" -r
# Output (raw strings):
# alice@example.com
# bob@example.com
```

### 3. Convert JSON to YAML

```bash
python jsoncraft.py to-yaml -f config.json > config.yaml
```

### 4. Compare Two JSON Files

```bash
python jsoncraft.py diff -f old.json -g new.json
```

```
  ~ $.version: "1.0.0" → "1.1.0"
  + $.features[2]: "dark-mode"
  - $.deprecated: ["old-api"]

  3 difference(s) found
```

### 5. Convert JSON Array to CSV

```bash
python jsoncraft.py csv -f users.json > users.csv
```

### 6. Validate JSON Schema

```bash
# Auto-infer schema from data
python jsoncraft.py validate -f data.json

# Validate against specific schema
python jsoncraft.py validate -f data.json -s schema.json
```

### 7. Extract Keys or Values

```bash
cat data.json | python jsoncraft.py keys
# name
# age
# email

cat data.json | python jsoncraft.py values
```

### 8. Flatten Nested JSON

```bash
echo '{"user":{"name":"Alice","address":{"city":"NYC"}}}' | python jsoncraft.py flatten
```

```json
{
  "user.name": "Alice",
  "user.address.city": "NYC"
}
```

## 🎨 ASCII Demo

```
$ echo '{"status":"ok","count":42,"items":[{"id":1,"name":"alpha"},{"id":2,"name":"beta"}]}' | python jsoncraft.py fmt

{
  "status": "ok",
  "count": 42,
  "items": [
    {
      "id": 1,
      "name": "alpha"
    },
    {
      "id": 2,
      "name": "beta"
    }
  ]
}
```

*Colors: keys in cyan, strings in green, numbers in magenta, booleans in yellow, null in red*

## 📖 Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `fmt` | `format`, `pretty` | Pretty-print JSON with colors |
| `min` | `minify`, `compact` | Minify JSON to single line |
| `query` | `q`, `jq` | Query with jq-like syntax |
| `path` | — | Extract with JSONPath |
| `diff` | — | Compare two JSON files |
| `to-yaml` | — | Convert JSON → YAML |
| `from-yaml` | — | Convert YAML → JSON |
| `csv` | — | Convert JSON array → CSV |
| `validate` | — | Validate against schema |
| `schema` | — | Infer JSON Schema from data |
| `keys` | — | Extract object keys |
| `values` | — | Extract object values |
| `type` | — | Show data type |
| `length` | — | Show data length |
| `flatten` | — | Flatten nested structure |

## 🔍 Query Syntax

Supports a simplified jq-like syntax:

| Expression | Description |
|------------|-------------|
| `.field` | Access field |
| `.[n]` | Array index (negative supported) |
| `.[start:end]` | Array slice |
| `.[]` | Iterate all elements |
| `.field.subfield` | Nested access |
| `keys` / `values` | Get keys or values |
| `length` / `type` | Get length or type |
| `unique` / `sort` / `reverse` | Array operations |
| `first` / `last` | First/last element |
| `.a \| .b` | Pipe expressions |

Examples:
```bash
jsoncraft query ".users[0].name"
jsoncraft query ".items[].price"
jsoncraft query ".data | .results | first"
jsoncraft query "keys"
jsoncraft query ".users[] | .email"
```

## 📁 Project Structure

```
jsoncraft/
├── jsoncraft.py      # Single-file CLI tool (all code here)
├── README.md         # This file
└── LICENSE           # MIT License
```

## 🤝 Contributing

Contributions welcome! This project is intentionally simple — single file, zero deps. Keep it that way.

1. Fork the repo
2. Make your changes to `jsoncraft.py`
3. Test thoroughly
4. Submit a PR

## 📜 License

MIT License — use it however you want.

---

<p align="center">
  <b>jsoncraft</b> — JSON, crafted for the terminal.<br>
  Made with ❤️ for developers who live in the CLI.
</p>
