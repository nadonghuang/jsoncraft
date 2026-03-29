# 🔧 jsoncraft

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-orange)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

**The Swiss Army Knife for JSON in your terminal.**

A zero-dependency Python CLI for formatting, querying, converting, diffing,
validating, merging, and flattening JSON — with beautiful colored output.

---

## 🎬 ASCII Demo

```
$ echo '{"status":"ok","count":42,"active":true,"items":[{"id":1,"name":"alpha"},{"id":2,"name":"beta"}]}' \
  | python jsoncraft.py fmt

{                             ← keys in cyan
  "status": "ok",             ← strings in green
  "count": 42,                ← numbers in magenta
  "active": true,             ← booleans in yellow
  "items": [
    { "id": 1, "name": "alpha" },
    { "id": 2, "name": "beta" }
  ]
}
```

```
$ python jsoncraft.py diff -f v1.json -g v2.json

  ~ $.version: "1.0.0" → "1.1.0"         ← changed: yellow
  + $.features[2]: "dark-mode"            ← added:   green
  - $.deprecated: ["old-api"]             ← removed: red

  3 difference(s) found
```

```
$ python jsoncraft.py merge -f base.json override.json --strategy deep

{
  "host": "prod.example.com",   ← from override
  "port": 443,                  ← from override
  "debug": false                ← from base (not overridden)
}
```

---

## ✨ Features

| Category | What you get |
|----------|-------------|
| 🎨 **Format & Minify** | Pretty-print or compress JSON with syntax highlighting |
| 🔍 **jq-like Queries** | `.users[0].name`, `.items[]`, pipes, built-in functions |
| ⚡ **JSONPath** | Extract values with `$.store.book[*].author` syntax |
| 📊 **JSON Diff** | Color, unified, or stat modes for comparing two files |
| ✅ **Schema Validation** | Validate against JSON Schema (draft-07) or auto-infer |
| 🔀 **Merge** | Deep, shallow, or concat strategies for combining files |
| 🔧 **Flatten / Unflatten** | Dot-notation ↔ nested JSON, both directions |
| 🔄 **JSON ↔ YAML** | Bidirectional conversion, zero external libs |
| 📄 **JSON → CSV** | Convert JSON arrays to CSV in one command |
| 🌈 **Colored Output** | Syntax highlighting with auto TTY detection |
| 📦 **Zero Dependencies** | Pure Python stdlib — no pip install needed |

---

## 📦 Installation

```bash
# Clone and run
git clone https://github.com/nadonghuang/jsoncraft.git
cd jsoncraft
chmod +x jsoncraft.py

# Or download the single file
curl -O https://raw.githubusercontent.com/nadonghuang/jsoncraft/main/jsoncraft.py
chmod +x jsoncraft.py

# Optional: add to PATH
sudo ln -s "$(pwd)/jsoncraft.py" /usr/local/bin/jsoncraft
```

No `pip install` needed. One file. Zero dependencies.

---

## 🚀 Quick Start

```bash
# Pretty-print
echo '{"name":"Alice","age":30}' | python jsoncraft.py fmt

# Query
cat users.json | python jsoncraft.py query ".users[0].name"

# Diff
python jsoncraft.py diff -f old.json -g new.json

# Validate
python jsoncraft.py validate -f data.json -s schema.json

# Merge
python jsoncraft.py merge -f base.json local.json --strategy deep

# Flatten → modify → unflatten
echo '{"a":{"b":1}}' | python jsoncraft.py flatten
echo '{"a.b":1}' | python jsoncraft.py unflatten
```

---

## 🎯 Use Cases

### API Response Debugging
Quickly inspect, query, and compare API responses without leaving the terminal.

```bash
# Pretty-print an API response with syntax highlighting
curl -s https://api.example.com/users | python jsoncraft.py fmt

# Pluck a specific field
curl -s https://api.example.com/users | python jsoncraft.py query ".data[0].email" -r

# Compare two API snapshots
python jsoncraft.py diff -f response_v1.json -g response_v2.json --mode stat
```

### Configuration File Processing
Merge configs, flatten for editing, validate before deploy.

```bash
# Deep-merge a base config with environment overrides
python jsoncraft.py merge -f config/default.json config/production.json \
  --strategy deep -o config/final.json

# Validate config against a schema before shipping
python jsoncraft.py validate -f config/final.json -s schema/config.json

# Flatten config for grep-friendly inspection
python jsoncraft.py flatten -f config.json | grep "database"
```

### Data Migration
Transform JSON structures for migration pipelines.

```bash
# Convert legacy YAML config to JSON
python jsoncraft.py from-yaml -f legacy.yaml > new_config.json

# Extract CSV for database import
python jsoncraft.py csv -f users.json > users.csv

# Flatten nested data for flat-file processing
python jsoncraft.py flatten -f orders.json > orders_flat.json

# Reverse: unflatten flat keys back to nested
python jsoncraft.py unflatten -f orders_flat.json > orders_nested.json
```

---

## 🏆 Why Choose jsoncraft?

| | **jsoncraft** | **jq** | **python -m json.tool** |
|---|---|---|---|
| Install | Download one file | Package manager (brew/apt) | Built-in |
| Dependencies | **Zero** | C lib, ~3 MB | Python stdlib |
| Syntax highlighting | ✅ Always on | ❌ None | ❌ None |
| Diff two files | ✅ 3 modes | ❌ Manual | ❌ No |
| Schema validation | ✅ Built-in | ❌ Need `jaq`/external | ❌ No |
| Merge JSON | ✅ 3 strategies | ✅ `*` operator | ❌ No |
| Flatten / unflatten | ✅ Both | ❌ No | ❌ No |
| YAML conversion | ✅ Both ways | ❌ Need `yq` | ❌ No |
| jq-like queries | ✅ Simplified | ✅ Full Turing-complete | ❌ No |
| JSONPath | ✅ Built-in | ❌ Different syntax | ❌ No |
| Learning curve | **Low** — dot notation | High — own language | None |

**TL;DR**: `jq` is more powerful for complex transformations. `json.tool` is always available. `jsoncraft` sits in the sweet spot — more features than `json.tool`, easier to learn than `jq`, and zero dependencies.

---

## 📖 Command Reference

| Command | Alias | Description |
|---------|-------|-------------|
| `fmt` | `format`, `pretty` | Pretty-print JSON with colors |
| `min` | `minify`, `compact` | Minify JSON to single line |
| `query` | `q`, `jq` | Query with jq-like syntax |
| `path` | — | Extract with JSONPath |
| `diff` | — | Compare two JSON files |
| `merge` | — | Merge multiple JSON files |
| `flatten` | — | Flatten nested structure to dot-notation |
| `unflatten` | — | Expand dot-notation back to nested |
| `validate` | — | Validate against JSON Schema |
| `schema` | — | Infer JSON Schema from data |
| `to-yaml` | — | Convert JSON → YAML |
| `from-yaml` | — | Convert YAML → JSON |
| `csv` | — | Convert JSON array → CSV |
| `keys` | — | Extract object keys |
| `values` | — | Extract object values |
| `type` | — | Show data type |
| `length` | — | Show data length |

---

## 📖 Detailed Usage

### Pretty-print (`fmt`)

```bash
echo '{"name":"Alice","age":30}' | python jsoncraft.py fmt
echo '{"name":"Alice","age":30}' | python jsoncraft.py fmt --indent 4 --sort
```

### Query (`query`)

```bash
cat data.json | python jsoncraft.py query ".users[0].name"        # "Alice"
cat data.json | python jsoncraft.py query ".users[].email" -r     # raw strings
cat data.json | python jsoncraft.py query ".data | first"
cat data.json | python jsoncraft.py query "keys"
```

**Supported expressions:**

| Expression | Description |
|------------|-------------|
| `.field` | Access field |
| `.[n]` | Array index (negative supported) |
| `.[start:end]` | Array slice |
| `.[]` | Iterate all elements |
| `.field.sub` | Nested access |
| `keys` / `values` | Get keys or values |
| `length` / `type` | Get length or type |
| `unique` / `sort` / `reverse` | Array operations |
| `first` / `last` | First/last element |
| `.a \| .b` | Pipe expressions |

### Diff (`diff`)

```bash
python jsoncraft.py diff -f old.json -g new.json                  # color mode (default)
python jsoncraft.py diff -f old.json -g new.json --mode unified   # git-style patch
python jsoncraft.py diff -f old.json -g new.json --mode stat      # summary stats
```

### Validate (`validate`)

```bash
# Validate against an explicit schema
python jsoncraft.py validate -f data.json -s schema.json

# Auto-infer schema from the data itself
python jsoncraft.py validate -f data.json

# Infer and save a schema
python jsoncraft.py schema -f data.json > schema.json
```

Supports JSON Schema draft-07 keywords: `type`, `properties`, `required`, `additionalProperties`, `items`, `minItems`, `maxItems`, `uniqueItems`, `minLength`, `maxLength`, `pattern`, `minimum`, `maximum`, `enum`.

### Merge (`merge`)

```bash
# Deep merge (nested objects merged recursively, later files win)
python jsoncraft.py merge -f base.json override.json --strategy deep

# Shallow merge (top-level only, later values override)
python jsoncraft.py merge -f a.json b.json --strategy shallow

# Concat (arrays appended, objects updated)
python jsoncraft.py merge -f arr1.json arr2.json --strategy concat

# Output to file
python jsoncraft.py merge -f base.json prod.json -o final.json
```

### Flatten / Unflatten

```bash
# Flatten nested JSON → dot-notation keys
echo '{"user":{"name":"Alice","address":{"city":"NYC"}}}' | python jsoncraft.py flatten
# {"user.name": "Alice", "user.address.city": "NYC"}

# Unflatten → nested JSON
echo '{"user.name":"Alice","user.address.city":"NYC"}' | python jsoncraft.py unflatten
# {"user": {"name": "Alice", "address": {"city": "NYC"}}}

# Custom separator
echo '{"a":{"b":1}}' | python jsoncraft.py flatten --separator "/"
# {"a/b": 1}
```

### YAML Conversion

```bash
python jsoncraft.py to-yaml -f config.json > config.yaml
python jsoncraft.py from-yaml -f config.yaml > config.json
```

### CSV Export

```bash
python jsoncraft.py csv -f users.json > users.csv
```

---

## ❓ FAQ

**Q: Do I need to install anything?**
No. `jsoncraft` is a single Python file with zero external dependencies. Just download and run with Python 3.8+.

**Q: How is this different from `jq`?**
`jq` is a powerful Turing-complete language for JSON transformation. `jsoncraft` trades that power for ease of use — simple dot-notation queries, built-in diff/merge/validate, and colored output out of the box. No new language to learn.

**Q: Can I use it without cloning the repo?**
Yes. Download the single file:
```bash
curl -O https://raw.githubusercontent.com/nadonghuang/jsoncraft/main/jsoncraft.py
```

**Q: Does it work on Windows?**
Yes, as long as you have Python 3.8+. Colors work in Windows Terminal, PowerShell 7+, and cmd with ANSI support.

**Q: How do I disable colors?**
Use `--no-color` or set the `NO_COLOR` environment variable. Colors also auto-disable when piping output.

**Q: What JSON Schema features are supported?**
`type`, `properties`, `required`, `additionalProperties`, `items`, `minItems`/`maxItems`, `uniqueItems`, `minLength`/`maxLength`, `pattern`, `minimum`/`maximum`, and `enum`. This covers the most common validation scenarios.

**Q: Can I merge more than two files?**
Yes. Pass any number of files: `python jsoncraft.py merge -f a.json b.json c.json d.json`.

**Q: Is there a Python API I can import?**
Not yet — it's designed as a CLI tool. But the functions are modular; you can `import jsoncraft` and call individual functions if needed.

---

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
