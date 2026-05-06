# Installing becraft

## Method 1: From NPM (recommended after publish)

```bash
# One-shot (always latest)
npx becraft install

# Or install globally
npm install -g becraft
becraft install
```

## Method 2: From GitHub (no NPM publish required)

```bash
# Replace phitsanu07 with your GitHub username
npx github:phitsanu07/becraft install

# Or install globally from GitHub
npm install -g github:phitsanu07/becraft
becraft install
```

## Method 3: From any Git URL

```bash
# HTTPS
npm install -g git+https://github.com/phitsanu07/becraft.git

# SSH
npm install -g git+ssh://git@github.com/phitsanu07/becraft.git

# Specific branch / tag / commit
npm install -g github:phitsanu07/becraft#v0.1.0
npm install -g github:phitsanu07/becraft#main
```

## Method 4: Local development

```bash
git clone https://github.com/phitsanu07/becraft.git
cd becraft
npm install
npm link              # makes `becraft` available globally
becraft install       # install into another project
```

## Verify install

```bash
becraft --version       # 0.1.0
becraft list            # Show all commands/agents/skills
becraft status          # Check installation in current dir
```

## Common installation flows

### New project from scratch
```bash
mkdir my-api && cd my-api
npx becraft install --quick
# Then:
/be-bootstrap user management API   # in Claude Code or Antigravity
```

### Existing project (add becraft)
```bash
cd existing-project
npx becraft install
# Choose IDE(s) interactively
```

### Update to latest
```bash
# If using npx (always latest)
npx becraft@latest install

# If installed globally
npm update -g becraft
becraft install
```
