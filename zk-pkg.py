#!/usr/bin/env python3
"""zk-pkg: Cluster Language Package Manager"""
import os, sys, json, urllib.request, hashlib, shutil

CACHE_DIR = os.path.expanduser("~/.zk/cache")
REGISTRY_URL = "https://raw.githubusercontent.com/cl-andro/cluster-modules/main/index.json"
LOCAL_REGISTRY = os.path.join(os.path.dirname(__file__), "index.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_registry():
    if os.path.exists(LOCAL_REGISTRY):
        with open(LOCAL_REGISTRY) as f:
            return json.load(f)
    try:
        resp = urllib.request.urlopen(REGISTRY_URL)
        return json.loads(resp.read())
    except:
        print("⚠️  Could not fetch remote registry.")
        return {"packages": {}}

def cmd_install(args):
    if not args:
        print("Usage: zk-pkg install <package>[@version]")
        return
    pkg_spec = args[0]
    version = None
    if "@" in pkg_spec:
        pkg_name, version = pkg_spec.split("@", 1)
    else:
        pkg_name = pkg_spec
    registry = load_registry()
    pkgs = registry.get("packages", {})
    if pkg_name not in pkgs:
        print(f"❌ Package '{pkg_name}' not found in registry.")
        return
    pkg = pkgs[pkg_name]
    ver = version or pkg["latest"]
    pkg_path = pkg.get("path", f"packages/{pkg_name}")
    main_file = pkg.get("main", f"{pkg_name}.zk")
    print(f"📦 Installing {pkg_name}@{ver}...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_key = hashlib.md5(pkg_path.encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, cache_key)
    os.makedirs("zk_modules", exist_ok=True)
    target = os.path.join("zk_modules", f"{pkg_name}.zk")
    local_pkg = os.path.join(SCRIPT_DIR, "packages", pkg_name, main_file)
    sibling_pkg = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "cluster-modules", pkg_path, main_file))
    if os.path.exists(local_pkg):
        shutil.copy(local_pkg, target)
        print(f"✅ {pkg_name}@{ver} installed (local)")
    elif os.path.exists(sibling_pkg):
        shutil.copy(sibling_pkg, target)
        print(f"✅ {pkg_name}@{ver} installed (local)")
    elif os.path.exists(cache_path):
        shutil.copy(cache_path, target)
        print(f"✅ {pkg_name}@{ver} installed (cached)")
    else:
        gh_url = f"https://raw.githubusercontent.com/cl-andro/cluster-modules/main/{pkg_path}/{main_file}"
        try:
            resp = urllib.request.urlopen(gh_url)
            content = resp.read().decode()
            with open(cache_path, "w") as f:
                f.write(content)
            with open(target, "w") as f:
                f.write(content)
            print(f"✅ {pkg_name}@{ver} installed")
        except Exception as e:
            print(f"❌ Failed to download: {e}")

def cmd_search(args):
    query = " ".join(args).lower()
    registry = load_registry()
    pkgs = registry.get("packages", {})
    results = [(n, p) for n, p in pkgs.items() if query in n.lower() or query in p.get("description", "").lower()]
    if not results:
        print(f"No packages matching '{query}'")
        return
    print(f"\n📦 Packages matching '{query}':\n")
    for name, pkg in results:
        print(f"  {name:15s} {pkg.get('latest', '?'):8s}  {pkg.get('description', '')}")

def cmd_list(args):
    os.makedirs("zk_modules", exist_ok=True)
    files = [f for f in os.listdir("zk_modules") if f.endswith(".zk")]
    if not files:
        print("No packages installed.")
        return
    print("\n📦 Installed packages:\n")
    for f in sorted(files):
        name = f.replace(".zk", "")
        print(f"  {name}")

def cmd_update(args):
    print("🔄 Updating packages...")
    registry = load_registry()
    pkgs = registry.get("packages", {})
    os.makedirs("zk_modules", exist_ok=True)
    for name, pkg in pkgs.items():
        target = os.path.join("zk_modules", f"{name}.zk")
        pkg_path = pkg.get("path", f"packages/{name}")
        main_file = pkg.get("main", f"{name}.zk")
        gh_url = f"https://raw.githubusercontent.com/cl-andro/cluster-modules/main/{pkg_path}/{main_file}"
        try:
            resp = urllib.request.urlopen(gh_url)
            content = resp.read().decode()
            with open(target, "w") as f:
                f.write(content)
            print(f"  ✅ {name}@{pkg['latest']}")
        except:
            print(f"  ⚠️  Could not update {name}")

def cmd_publish(args):
    print("📤 Publishing requires a GitHub token and repository access.")
    print("   Run: zk-pkg publish <package_directory>")
    print("\n   Make sure your package has a package.zk manifest.")

def main():
    if len(sys.argv) < 2:
        print("Usage: zk-pkg <command> [args]")
        print("\nCommands:")
        print("  install <pkg>[@ver]   Install a package")
        print("  search <query>        Search packages")
        print("  list                  List installed packages")
        print("  update                Update all packages")
        print("  publish <dir>         Publish a package")
        return
    cmd = sys.argv[1]
    args = sys.argv[2:]
    cmds = {
        "install": cmd_install,
        "search": cmd_search,
        "list": cmd_list,
        "update": cmd_update,
        "publish": cmd_publish,
    }
    if cmd in cmds:
        cmds[cmd](args)
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
