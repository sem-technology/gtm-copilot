import os
import shutil
import zipfile

def get_version_from_skill_md(skill_md_path):
    """
    Extracts the version from the YAML frontmatter of SKILL.md.
    """
    if not os.path.exists(skill_md_path):
        return "0.0.0"
    
    with open(skill_md_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip()
    return "0.0.0"

def main():
    # Configuration
    project_root = os.getcwd()
    skill_md_path = os.path.join(project_root, "src", "SKILL.md")
    version = get_version_from_skill_md(skill_md_path)
    project_name = "gtm-copilot"
    
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
    src_dir = os.path.join(project_root, "src")
    
    if os.path.exists(src_dir):
        # Copy scripts directory
        scripts_src = os.path.join(src_dir, "scripts")
        if os.path.exists(scripts_src):
            shutil.copytree(scripts_src, os.path.join(build_dir, "scripts"), 
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
            print(f"  - Copied scripts to {os.path.join(build_dir, 'scripts')} (excluding __pycache__)")
            
        # Copy resources directory
        resources_src = os.path.join(src_dir, "resources")
        if os.path.exists(resources_src):
            shutil.copytree(resources_src, os.path.join(build_dir, "resources"),
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
            print(f"  - Copied resources to {os.path.join(build_dir, 'resources')}")
            
        # Copy SKILL.md
        skill_src = os.path.join(src_dir, "SKILL.md")
        if os.path.exists(skill_src):
            shutil.copy2(skill_src, build_dir)
            print(f"  - Copied SKILL.md to root")

        # Copy .env.example (now inside src/)
        env_src = os.path.join(src_dir, ".env.example")
        if os.path.exists(env_src):
            shutil.copy2(env_src, build_dir)
            print(f"  - Copied .env.example to root")

        # Copy LICENSE.txt (now inside src/)
        license_src = os.path.join(src_dir, "LICENSE.txt")
        if os.path.exists(license_src):
            shutil.copy2(license_src, build_dir)
            print(f"  - Copied LICENSE.txt to root")

    # 5. Process SKILL.md in build_dir
    dest_file = os.path.join(build_dir, "SKILL.md")
    if os.path.exists(dest_file):
        with open(dest_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Update paths from src/ to scripts/
        final_content = content.replace("src/bin/", "scripts/bin/")
        final_content = final_content.replace("src/helpers/", "scripts/helpers/")
        # Also handle any cases where gtm_client.py or authentication.py are referenced directly if needed
        # (Though SKILL.md mostly lists them in the directory structure section)
        
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
