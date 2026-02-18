import os
import shutil
import zipfile

def main():
    # Configuration
    version = "1.0.0"
    project_name = "gtm-copilot"
    project_root = os.getcwd()
    
    build_dir = os.path.join(project_root, "build", project_name)
    artifacts_dir = os.path.join(project_root, "artifacts")
    zip_filename = f"{project_name}_v{version}.zip"
    zip_path = os.path.join(artifacts_dir, zip_filename)

    print(f"Building {project_name} v{version}...")

    # Clear and recreate build directory
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # 1. Copy src contents to build_dir
    src_src = os.path.join(project_root, "src")
    scripts_dest = os.path.join(build_dir, "scripts")
    
    if os.path.exists(src_src):
        for item in os.listdir(src_src):
            s = os.path.join(src_src, item)
            
            # Logic files and folders go into 'scripts/'
            if item in ["bin", "helpers"] or item.endswith(".py"):
                d = os.path.join(scripts_dest, item)
                os.makedirs(scripts_dest, exist_ok=True)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            # SKILL.md and resources folder stay at build_dir root
            elif item == "SKILL.md":
                d = os.path.join(build_dir, item)
                shutil.copy2(s, d)
            elif item == "resources" and os.path.isdir(s):
                d = os.path.join(build_dir, item)
                shutil.copytree(s, d)
                
        print(f"  - Reorganized source logic into {scripts_dest} and resources to {build_dir}")

    # 3. Copy .env.example to root
    env_src = os.path.join(project_root, ".env.example")
    if os.path.exists(env_src):
        shutil.copy2(env_src, build_dir)
        print(f"  - Copied .env.example to root")

    # 4. Copy LICENSE.txt to root
    license_src = os.path.join(project_root, "LICENSE.txt")
    if os.path.exists(license_src):
        shutil.copy2(license_src, build_dir)
        print(f"  - Copied LICENSE.txt to root")

    # 5. Process SKILL.md in build_dir
    dest_file = os.path.join(build_dir, "SKILL.md")
    if os.path.exists(dest_file):
        with open(dest_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Update paths from ./bin/ to ./scripts/bin/
        final_content = content.replace("./bin/", "./scripts/bin/")
        final_content = final_content.replace("./helpers/", "./scripts/helpers/")
        
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"  - Processed portable SKILL.md and updated paths to scripts/")

    # 5. Create Zip Archive in artifacts/
    if not os.path.exists(artifacts_dir):
        os.makedirs(artifacts_dir)
    
    # Remove existing zip if it exists
    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, build_dir)
                # Nest everything inside project_name folder
                zip_internal_path = os.path.join(project_name, rel_path)
                zf.write(abs_path, zip_internal_path)
    
    print(f"\nCreated Zip: {zip_path}")

    # Cleanup build directory
    shutil.rmtree(os.path.join(project_root, "build"))
    print("Cleanup build temporary files.")

    print(f"\nBuild complete! Distributed as {zip_filename}")

if __name__ == "__main__":
    main()
