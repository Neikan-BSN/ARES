#!/bin/bash

# MCP Server Installation Script for ARES
# Agent Reliability Enforcement System - Installs all MCP servers with Doppler integration

set -e

echo "🚀 MCP Server Installation for ARES"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Project configuration
PROJECT_DIR="/home/user01/projects/ARES"
PROJECT_NAME="ARES"

print_status "Installing MCP servers for $PROJECT_NAME..."
print_status "Using local scope configuration: ~/.claude.json [project: $PROJECT_DIR]"

# Get secrets from Doppler (with fallbacks)
if command -v doppler >/dev/null 2>&1; then
    print_status "Fetching secrets from Doppler..."
    GH_TOKEN=$(doppler secrets get GH_TOKEN --plain 2>/dev/null || echo "")
    OPENAI_API_KEY=$(doppler secrets get OPENAI_API_KEY --plain 2>/dev/null || echo "")
    ANTHROPIC_API_KEY=$(doppler secrets get ANTHROPIC_API_KEY --plain 2>/dev/null || echo "")
    POSTGRES_CONNECTION_STRING=$(doppler secrets get POSTGRES_CONNECTION_STRING --plain 2>/dev/null || echo "postgresql://localhost:5432/ares")
    REDIS_URL=$(doppler secrets get REDIS_URL --plain 2>/dev/null || echo "redis://localhost:6379")
else
    print_status "Doppler not available, using environment variables..."
    GH_TOKEN="${GH_TOKEN:-}"
    OPENAI_API_KEY="${OPENAI_API_KEY:-}"
    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"
    POSTGRES_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-postgresql://localhost:5432/ares}"
    REDIS_URL="${REDIS_URL:-redis://localhost:6379}"
fi

cd "$PROJECT_DIR"

# Generate ~/.claude.json configuration
cat > ~/.claude.json << EOF
{
  "mcpServers": {
    "project:$PROJECT_DIR": {
      "context7": {
        "command": "npx",
        "args": ["-y", "@context7/mcp-server"]
      },
      "eslint": {
        "command": "npx",
        "args": ["-y", "@eslint/mcp@latest"]
      },
      "fetch": {
        "command": "npx",
        "args": ["-y", "@tokenizin/mcp-npx-fetch"]
      },
      "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "$PROJECT_DIR"]
      },
      "git": {
        "command": "npx",
        "args": ["-y", "@cyanheads/git-mcp-server"]
      },
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_PERSONAL_ACCESS_TOKEN": "$GH_TOKEN"
        }
      },
      "memory": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"]
      },
      "playwright": {
        "command": "npx",
        "args": ["-y", "@executeautomation/playwright-mcp-server"]
      },
      "sequentialthinking": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
      },
      "sqlite": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sqlite", "$PROJECT_DIR/data"]
      },
      "postgresql": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "env": {
          "POSTGRES_CONNECTION_STRING": "$POSTGRES_CONNECTION_STRING"
        }
      },
      "redis": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-redis"],
        "env": {
          "REDIS_URL": "$REDIS_URL"
        }
      },
      "ripgrep": {
        "command": "npx",
        "args": ["-y", "mcp-ripgrep@latest"]
      },
      "code-checker": {
        "command": "uv",
        "args": ["run", "python", "-m", "mcp_code_checker", "--project-dir", "$PROJECT_DIR"]
      },
      "docker": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-docker"]
      },
      "typescript": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-typescript"]
      },
      "obsidian": {
        "command": "npx",
        "args": ["-y", "@cyanheads/obsidian-mcp-server", "$PROJECT_DIR/docs"]
      },
      "clip-to-wsl": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-clipboard"]
      }
    }
  }
}
EOF

print_success "✅ MCP configuration generated at ~/.claude.json"
print_success "✅ All MCP servers configured for ARES"

echo ""
print_status "Next steps:"
echo "1. Restart Claude Code or start a new session"
echo "2. Navigate to $PROJECT_DIR"
echo "3. Run 'claude mcp list' to verify servers are loaded"
echo "4. Servers will be available with local scope for this project"

echo ""
print_status "Configured MCP servers:"
echo "  • context7 (AI documentation)"
echo "  • eslint (code quality)"
echo "  • fetch (web scraping)"
echo "  • filesystem (file operations)"
echo "  • git (version control)"
echo "  • github (GitHub integration)"
echo "  • memory (knowledge graphs)"
echo "  • playwright (browser automation)"
echo "  • sequentialthinking (reasoning)"
echo "  • sqlite (local database)"
echo "  • postgresql (main database)"
echo "  • redis (caching)"
echo "  • ripgrep (code search)"
echo "  • code-checker (quality analysis)"
echo "  • docker (containers)"
echo "  • typescript (TypeScript support)"
echo "  • obsidian (documentation)"
echo "  • clip-to-wsl (clipboard)"

print_success "🎉 ARES MCP setup completed!"
