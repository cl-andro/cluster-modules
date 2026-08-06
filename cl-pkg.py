#!/usr/bin/env python3
"""cl-pkg: Cluster Language Package Manager"""
import os
import sys
import json
import urllib.request
import urllib.parse
import hashlib
import shutil
import subprocess

CACHE_DIR = os.path.expanduser("~/.cl/cache")
REGISTRY_URL = "https://raw.githubusercontent.com/cl-andro/cluster-modules/main/index.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_REGISTRY = os.path.join(SCRIPT_DIR, "index.json")

def load_registry():
    if os.path.exists(LOCAL_REGISTRY):
        try:
            with open(LOCAL_REGISTRY) as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error reading local registry: {e}")
    try:
        resp = urllib.request.urlopen(REGISTRY_URL, timeout=5)
        return json.loads(resp.read().decode())
    except Exception as e:
        print(f"⚠️  Could not fetch remote registry: {e}")
        return {"packages": {}}

def parse_manifest(directory):
    manifest_path = os.path.join(directory, "package.cl")
    if not os.path.exists(manifest_path):
        return None
    
    metadata = {}
    try:
        with open(manifest_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or ":" not in line:
                    continue
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == "dependencies":
                    # Simple parse for dependency list
                    metadata[key] = []
                elif key.startswith("-") and "dependencies" in metadata:
                    metadata["dependencies"].append(val)
                else:
                    metadata[key] = val
    except Exception as e:
        print(f"⚠️  Error parsing package.cl: {e}")
        return None
    return metadata

def cmd_install(args):
    if not args:
        print("Usage: cl-pkg install <package>[@version]")
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
    ver = version or pkg.get("latest", "1.0.0")
    
    # Handle version mapping details
    ver_info = pkg.get("versions", {}).get(ver, {})
    pkg_path = ver_info.get("path", f"packages/{pkg_name}")
    main_file = ver_info.get("main", f"{pkg_name}.cl")
    
    print(f"📦 Installing {pkg_name}@{ver}...")
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    cache_key = hashlib.md5(f"{pkg_name}@{ver}".encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, cache_key)
    
    os.makedirs("cl_modules", exist_ok=True)
    target = os.path.join("cl_modules", f"{pkg_name}.cl")
    
    # Check local sources
    local_pkg = os.path.join(SCRIPT_DIR, "packages", pkg_name, "src", main_file)
    sibling_pkg = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", "cluster-modules", "packages", pkg_name, "src", main_file))
    
    if os.path.exists(local_pkg):
        shutil.copy(local_pkg, target)
        print(f"✅ {pkg_name}@{ver} installed (local development source)")
    elif os.path.exists(sibling_pkg):
        shutil.copy(sibling_pkg, target)
        print(f"✅ {pkg_name}@{ver} installed (local sibling toolchain)")
    elif os.path.exists(cache_path):
        shutil.copy(cache_path, target)
        print(f"✅ {pkg_name}@{ver} installed (from cache)")
    else:
        # Download from Git repository URL
        git_url = ver_info.get("url")
        if not git_url:
            # Fallback to main registry repository raw content
            git_url = f"https://raw.githubusercontent.com/cl-andro/cluster-modules/main/{pkg_path}/src/{main_file}"
        
        try:
            if git_url.startswith("http"):
                resp = urllib.request.urlopen(git_url)
                content = resp.read().decode()
                with open(cache_path, "w") as f:
                    f.write(content)
                with open(target, "w") as f:
                    f.write(content)
                print(f"✅ {pkg_name}@{ver} installed successfully.")
            else:
                print(f"❌ Invalid git repository URL configured for version {ver}.")
        except Exception as e:
            print(f"❌ Failed to download package components: {e}")

def cmd_search(args):
    query = " ".join(args).lower()
    registry = load_registry()
    pkgs = registry.get("packages", {})
    results = [(n, p) for n, p in pkgs.items() if query in n.lower() or query in p.get("description", "").lower()]
    
    if not results:
        print(f"No packages matching '{query}' found.")
        return
        
    print(f"\n📦 Cluster Packages matching '{query}':\n")
    for name, pkg in results:
        print(f"  {name:18s} {pkg.get('latest', '1.0.0'):8s}  {pkg.get('description', '')}")

def cmd_list(args):
    os.makedirs("cl_modules", exist_ok=True)
    files = [f for f in os.listdir("cl_modules") if f.endswith(".cl")]
    if not files:
        print("No packages installed in cl_modules.")
        return
    print("\n📦 Installed Cluster modules:\n")
    for f in sorted(files):
        name = f.replace(".cl", "")
        print(f"  {name}")

def cmd_update(args):
    print("🔄 Updating all modules inside cl_modules...")
    registry = load_registry()
    pkgs = registry.get("packages", {})
    
    if not os.path.exists("cl_modules"):
        print("No active modules directory found. Run 'cl-pkg install' first.")
        return
        
    installed = [f.replace(".cl", "") for f in os.listdir("cl_modules") if f.endswith(".cl")]
    for name in installed:
        if name in pkgs:
            cmd_install([name])

def cmd_publish(args):
    directory = args[0] if args else "."
    if not os.path.exists(directory):
        print(f"❌ Directory '{directory}' does not exist.")
        return
        
    manifest = parse_manifest(directory)
    if not manifest:
        print("❌ Could not find or parse package.cl manifest.")
        print("   Make sure the package follows the layout standard specified in CONTRIBUTING.md.")
        return
        
    pkg_name = manifest.get("name")
    version = manifest.get("version")
    description = manifest.get("description", "")
    license_type = manifest.get("license", "Proprietary")
    
    if not pkg_name or not version:
        print("❌ Manifest must specify 'name' and 'version'.")
        return
        
    print(f"📤 Preparing submission for package: {pkg_name}@{version}...")
    
    # Try resolving local git details
    git_url = ""
    try:
        git_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], cwd=directory).decode().strip()
    except:
        pass
        
    if not git_url:
        print("⚠️  Warning: No git remote origin URL found.")
        git_url = input("Enter package Git Repository URL: ").strip()
        if not git_url:
            print("❌ Git Repository URL is required to publish a package.")
            return

    # Check for local registry edit (highly useful for local registration tests)
    if os.path.exists(LOCAL_REGISTRY):
        try:
            with open(LOCAL_REGISTRY, "r") as f:
                registry = json.load(f)
        except:
            registry = {"packages": {}}
            
        if "packages" not in registry:
            registry["packages"] = {}
            
        if pkg_name not in registry["packages"]:
            registry["packages"][pkg_name] = {
                "description": description,
                "latest": version,
                "license": license_type,
                "versions": {}
            }
            
        registry["packages"][pkg_name]["latest"] = version
        registry["packages"][pkg_name]["versions"][version] = {
            "url": git_url,
            "path": f"packages/{pkg_name}",
            "main": f"{pkg_name}.cl"
        }
        
        with open(LOCAL_REGISTRY, "w") as f:
            json.dump(registry, f, indent=2)
            
        print(f"✅ Local registry updated in index.json! Package {pkg_name}@{version} is registered.")
        print("   Commit and push index.json to update the global registry index.")
        return
        
    # Remote API call fallback
    api_url = os.environ.get("CLUSTER_REGISTRY_API", "http://localhost:3000/api/publish")
    payload = {
        "name": pkg_name,
        "version": version,
        "description": description,
        "license": license_type,
        "url": git_url
    }
    
    print(f"Connecting to Package API at {api_url}...")
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(api_url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode())
            if res_data.get("success"):
                print(f"🎉 Package {pkg_name}@{version} published successfully!")
            else:
                print(f"❌ Publish failed: {res_data.get('message', 'Unknown API error')}")
    except Exception as e:
        print(f"❌ Failed to reach Central Registry API: {e}")
        print("   Make sure the API server is running or set CLUSTER_REGISTRY_API env variable.")

def main():
    if len(sys.argv) < 2:
        print("Usage: cl-pkg <command> [args]")
        print("\nCommands:")
        print("  install <pkg>[@ver]   Install a package")
        print("  search <query>        Search packages")
        print("  list                  List installed packages")
        print("  update                Update all packages")
        print("  publish [dir]         Publish a package (default: current directory)")
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
