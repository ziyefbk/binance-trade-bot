# User-Level Claude Code Configuration Guide

## ~/.claude.json Setup

This file configures global MCP servers and preferences for Claude Code across all projects.

**File Location**:
- Windows: `C:\Users\[YourUsername]\.claude.json`
- Linux/macOS: `~/.claude.json`

---

## Recommended Configuration

Create or edit `~/.claude.json` with the following content:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "YOUR_GITHUB_TOKEN_HERE"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## MCP Server Details

### 1. GitHub MCP (Required)

**Purpose**: Automate Git operations, create PRs, manage issues

**Setup**:
1. Visit https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
   - `admin:org_hook` (if working with organization repos)
4. Generate token and copy it
5. Replace `YOUR_GITHUB_TOKEN_HERE` in the config above

**Usage**:
- "Create a PR for these changes"
- "List open issues"
- "View PR #123"
- "Merge PR #456"

---

### 2. Memory MCP (Recommended)

**Purpose**: Persist context and learnings across sessions

**Features**:
- Remember project-specific patterns
- Save architecture decisions
- Recall coding preferences
- Store frequently used commands

**No setup required** - works out of the box.

---

### 3. Sequential Thinking MCP (Recommended)

**Purpose**: Complex reasoning and debugging

**Use Cases**:
- Debugging intricate race conditions
- Architecture design trade-offs
- Performance optimization strategies
- Security vulnerability analysis

**No setup required** - works out of the box.

---

## Optional MCP Servers

### Context7 (Documentation Lookup)

```json
{
  "context7": {
    "command": "npx",
    "args": ["-y", "@context7/mcp-server"]
  }
}
```

**Use Cases**:
- Real-time Boost documentation lookup
- C++ standard library reference
- CMake documentation

---

### Filesystem MCP (Advanced)

```json
{
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "/path/to/your/projects"
    ]
  }
}
```

**Warning**: Only enable if you need cross-project file access. Can consume significant context.

---

## MCP Best Practices

### 1. Limit to Essential MCPs
- **Recommended**: 3-5 MCPs
- **Maximum**: 10 MCPs
- **Reason**: Each MCP consumes context window space

### 2. Disable Per-Project
In project-level `.claude.json`:
```json
{
  "disabledMcpServers": ["context7", "filesystem"]
}
```

### 3. Monitor Token Usage
- With 3 MCPs: ~180k tokens available
- With 10 MCPs: ~70k tokens available
- **Rule**: If context runs out, disable unused MCPs

---

## Global Rules (Optional)

Create `~/.claude/rules/` directory for global behavioral rules:

```bash
mkdir -p ~/.claude/rules
```

**Recommended rules to copy from everything-claude-code**:

```bash
# Copy from everything-claude-code repository
cp ../everything-claude-code/rules/security.md ~/.claude/rules/
cp ../everything-claude-code/rules/testing.md ~/.claude/rules/
cp ../everything-claude-code/rules/coding-style.md ~/.claude/rules/
cp ../everything-claude-code/rules/performance.md ~/.claude/rules/
```

---

## Verification

### Test GitHub MCP

```bash
# Start Claude Code
claude

# In chat, type:
"List my GitHub repositories"
```

If configured correctly, you'll see a list of your repos.

---

### Test Memory MCP

```bash
# In Claude Code:
"Remember that I prefer using Google Test for C++ testing"

# In a new session:
"What do I prefer for C++ testing?"
```

Should recall your preference.

---

## Troubleshooting

### MCP Not Working

1. **Check npx is installed**:
   ```bash
   npx --version
   ```

2. **Install Node.js** (if needed):
   - Windows: https://nodejs.org/
   - Linux: `sudo apt install nodejs npm`
   - macOS: `brew install node`

3. **Verify MCP package**:
   ```bash
   npx -y @modelcontextprotocol/server-github --help
   ```

4. **Check token permissions** (GitHub MCP):
   - Visit https://github.com/settings/tokens
   - Ensure token has `repo` scope

---

### Context Window Issues

**Symptom**: "Context limit exceeded" errors

**Solutions**:
1. Disable unused MCPs in project `.claude.json`:
   ```json
   { "disabledMcpServers": ["context7", "filesystem"] }
   ```

2. Reduce number of global MCPs in `~/.claude.json`

3. Use `/compact` command to compress context

---

## Complete Example Configuration

Here's a production-ready `~/.claude.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      },
      "disabled": false
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "disabled": false
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "disabled": false
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"],
      "disabled": true
    }
  },
  "globalPreferences": {
    "defaultModel": "claude-sonnet-4-5",
    "enableTelemetry": false
  }
}
```

---

## Next Steps

1. **Create `~/.claude.json`** with the recommended configuration
2. **Set up GitHub token** for GitHub MCP
3. **Test MCPs** to verify they work
4. **Copy global rules** to `~/.claude/rules/`
5. **Start using Claude Code** with enhanced capabilities!

---

## Resources

- [MCP Servers Registry](https://github.com/modelcontextprotocol/servers)
- [GitHub MCP Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Memory MCP Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
- [Everything Claude Code Repository](https://github.com/affaan-m/everything-claude-code)

---

## Support

If you encounter issues:
1. Check the [Claude Code documentation](https://docs.anthropic.com/claude-code)
2. Review [everything-claude-code](https://github.com/affaan-m/everything-claude-code) examples
3. Open an issue on the Binance Arbitrage Bot repository
