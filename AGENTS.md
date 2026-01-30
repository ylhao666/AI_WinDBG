# AGENTS.md - AI Coding Agent Guidelines

Guidelines for agentic coding agents in AI_WinDBG repository.

## Build, Lint, and Test Commands

### Python Backend
```bash
pip install -r requirements.txt
black src/ && flake8 src/ && mypy src/
pytest tests/                           # All tests
pytest tests/test_windbg.py             # Single file
pytest tests/test_windbg.py::test_func  # Single function
pytest --cov=src tests/                # Coverage
python main.py --mode cli|web|both
```

### Frontend (TypeScript/React)
```bash
cd web-ui && npm install
npm run dev                # Dev with hot reload
npm run build              # Production build
npm run lint && npm test    # Lint & tests
npm run test:ui            # Vitest UI
```

## Code Style Guidelines

### Python Code

**Imports**: Absolute imports `from src.core.config import ConfigManager`. Group: stdlib → third-party → local.

**Formatting**: Black (line 88), PEP 8, 4 spaces, double quotes. Type hints required.

**Types**: `Optional[T]`, `List[T]`, `Dict[K,V]`, `@dataclass` for data structs.

**Naming**: Classes `PascalCase`, functions `snake_case`, constants `UPPER_SNAKE_CASE`, private `_prefix`.

**Error Handling**: Custom exceptions in `src/core/exceptions.py`. Use `LoggerManager.info/error()`. Never expose secrets.

**Docstrings**: Google-style with Chinese descriptions.

**Config**: `config.get("key.path", default)` / `config.set("key.path", value)`. ENV vars: `${VAR_NAME}`.

### TypeScript/React Code

**Imports**: Absolute `@/pages/Dashboard`. Destructure: `import { useState } from 'react'`.

**Types**: Interfaces in `src/types/index.ts`, `interface`, `enum`, `React.FC<Props>`, optional `?`.

**Components**: Functional + hooks, `useRef<HTMLDivElement>`, `useEffect`, Ant Design components.

**Styling**: Inline camelCase `style={{ color: '#fff' }}`, Ant Design, flexbox/grid.

**State**: `useState`, `useEffect`, `useCallback` for handlers.

## Project Structure

### Python Backend
```
src/
├── cli/          # CLI interface (prompt-toolkit, rich)
├── core/         # Config, logging, session, exceptions
├── llm/          # LLM client, analyzer, cache, provider manager
├── nlp/          # NLP processor, classifier, mapper, templates
├── output/       # Output models and display modes
├── web/          # FastAPI app, routes, services, websocket
└── windbg/       # WinDBG engine, executor, parser, symbols
```

### Frontend
```
web-ui/src/
├── api/          # Axios client, API endpoints
├── components/   # React components
├── pages/        # Page components
├── types/        # TypeScript interfaces
└── utils/        # Utility functions
```

## Testing Guidelines

### Python Tests
- Use pytest with async support: `pytest-asyncio`
- Place tests in `tests/` directory
- Name test files: `test_*.py`
- Name test functions: `test_*`
- Use fixtures for common setup

### TypeScript Tests
- Use vitest with jsdom environment
- Place tests in `src/**/__tests__/` or `src/test/`
- Name test files: `*.test.ts` or `*.test.tsx`
- Use `describe`, `it`, `expect` from vitest globals
- Mock external dependencies

## Security Guidelines

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Sanitize file paths to prevent directory traversal
- Use cryptography library for encryption
- Enable command validation in config

## Common Patterns

### Session Management
- SessionManager singleton for shared session state
- WinDBGEngine manages persistent cdb process
- Thread-safe operations with locks

### LLM Integration
- LLMClient wraps OpenAI SDK with streaming support
- SmartAnalyzer provides cached analysis
- Support multiple providers via ProviderManager

### WebSocket Communication
- `/ws/output` for real-time command output
- `/ws/session` for session state updates
- Send JSON messages with type field

## Important Notes

- This is a Windows-focused project using WinDBG (cdb.exe)
- Python 3.10+ required
- Node.js 18+ required for frontend development
- Use Chinese comments and user-facing strings
- Test with actual dump files in `examples/`
- Build frontend before running web mode: `cd web-ui && npm run build`
