# figma-ppt-plugin — Claude Code Marketplace

Custom Claude Code plugin marketplace containing the **figma-ppt** skill.

## Install

```bash
claude plugin marketplace add daehyeonxyz/figma-ppt-plugin
claude plugin install figma-ppt@daehyeonxyz-figma-ppt-plugin
```

## Available Plugins

### figma-ppt

Generate Figma presentation slides by building a real 1920×1080 HTML/CSS website
and capturing it into editable Figma frames via Claude Code + Figma Dev Mode MCP.

**No API key needed. No Figma plugin to install. Just Claude Code.**

→ See [plugins/figma-ppt/README.md](plugins/figma-ppt/README.md) for full documentation.

## Prerequisites

- Figma desktop app
- Dev Mode MCP enabled: Figma → Preferences → Dev Mode MCP Server ON
- `claude mcp add --transport sse figma-dev-mode-mcp-server http://127.0.0.1:3845/sse`
- Python 3.8+
