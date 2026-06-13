# cluster-modules

Package registry for the Cluster programming language (`cluster-lang`).

## Usage

```bash
# Install a package
zk-pkg install cl-http

# Search packages
zk-pkg search json

# List installed packages
zk-pkg list

# Update all packages
zk-pkg update

# Publish your package
zk-pkg publish
```

## Adding a Package

1. Create a directory in `packages/<name>/`
2. Add `package.zk` manifest
3. Add source `.zk` files
4. Update `index.json`
5. Open a PR

## Package Manifest (`package.zk`)

```zk
name: "cl-http"
version: "0.1.0"
description: "HTTP client and server"
license: "MIT"
author: "Cluster Authors"
dependencies: ["cl-json@0.1.0"]
```

## Registry Index (`index.json`)

```json
{
  "cl-http": {
    "description": "HTTP client and server",
    "latest": "0.1.0",
    "path": "packages/cl-http",
    "license": "MIT"
  }
}
```
