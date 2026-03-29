<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Zero_Deps-✅-success?style=for-the-badge" alt="Zero Deps"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">🔧 jsoncraft</h1>

<p align="center">
  <strong>The Swiss Army knife for JSON — format, query, diff, convert & more in your terminal.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Install</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-license">License</a>
</p>

---

## ✨ Features

- 📋 **Format & Minify** — Pretty-print or compress JSON with indentation control
- 🔍 **Query** — Extract values using simple dot-notation paths
- 🔄 **Convert** — JSON ↔ CSV, JSON → YAML (no dependencies)
- 📊 **Diff** — Compare two JSON files and show differences
- 🌳 **Paths** — List all JSON paths in a structure
- 📈 **Stats** — Show JSON structure overview (keys, types, depth)
- 🎨 **Syntax Highlight** — Colorized terminal output
- 📥 **Stdin Support** — Pipe-friendly, works with any data source

## 📦 Installation

```bash
chmod +x jsoncraft.py
sudo cp jsoncraft.py /usr/local/bin/jsoncraft
```

Or use directly:
```bash
python3 jsoncraft.py <command> [args]
```

## 🚀 Usage

```bash
# Pretty-print JSON
cat data.json | jsoncraft format

# Minify JSON
jsoncraft minify data.json

# Query a specific path
echo '{"user":{"name":"Alice","age":30}}' | jsoncraft query .user.name

# JSON to CSV
jsoncraft to-csv data.json

# Diff two JSON files
jsoncraft diff old.json new.json

# Show structure stats
jsoncraft stats data.json

# List all paths
jsoncraft paths data.json
```

### Commands

| Command | Description |
|---------|-------------|
| `format` | Pretty-print JSON (default) |
| `minify` | Compress JSON to single line |
| `query <path>` | Extract value at dot-notation path |
| `to-csv` | Convert JSON array to CSV |
| `diff <file1> <file2>` | Compare two JSON files |
| `stats` | Show JSON statistics |
| `paths` | List all JSON paths |

## 🛠 Tech Details

- **Zero dependencies** — Pure Python standard library
- **Color output** — Auto-detects terminal color support
- **Large files** — Streams efficiently, handles big JSON
- **Error handling** — Clear error messages with line numbers

## 📁 Project Structure

```
jsoncraft/
├── jsoncraft.py    # Single-file CLI tool
├── README.md
└── LICENSE
```

## 📄 License

MIT — use it however you like.

---

<p align="center">
  Made with ⚡ by <a href="https://github.com/nadonghuang">nadonghuang</a>
  <br/>
  <sub>If you find this useful, give it a ⭐!</sub>
</p>
