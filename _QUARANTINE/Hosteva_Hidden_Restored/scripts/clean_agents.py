import os
import shutil

base_dir = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/agents"

# Mapping CamelCase to kebab-case based on previous ls output
mapping = {
    "AgentCoulson": "phil-coulson",
    "BlackWidow": "black-widow",
    "CaptainAmerica": "captain-america",
    "Hawkeye": "hawkeye",
    "Heimdall": "heimdall",
    "NickFury": "nick-fury",
    "RocketRaccoon": "rocket-raccoon"
}

print("Starting Agent Directory Consolidation...")

for camel, kebab in mapping.items():
    camel_dir = os.path.join(base_dir, camel)
    kebab_dir = os.path.join(base_dir, kebab)
    
    if os.path.exists(camel_dir):
        print(f"Processing duplicate: {camel} -> {kebab}")
        if not os.path.exists(kebab_dir):
            os.makedirs(kebab_dir)
        
        for item in os.listdir(camel_dir):
            camel_item = os.path.join(camel_dir, item)
            kebab_item = os.path.join(kebab_dir, item)
            
            if os.path.isfile(camel_item):
                if os.path.exists(kebab_item):
                    # Merge contents to prevent data loss
                    print(f"  Merging {item} into {kebab_dir}")
                    with open(camel_item, "r") as f_camel:
                        camel_content = f_camel.read()
                    with open(kebab_item, "a") as f_kebab:
                        f_kebab.write("\n\n<!-- --- MERGED FROM DUPLICATE DIRECTORY --- -->\n\n")
                        f_kebab.write(camel_content)
                else:
                    # Move file if it doesn't exist in target
                    print(f"  Moving {item} to {kebab_dir}")
                    shutil.copy2(camel_item, kebab_item)
        
        # Remove the CamelCase directory
        shutil.rmtree(camel_dir)
        print(f"Deleted duplicate directory: {camel}")

# Handle internal redundant files like `rocket-raccoon_soul.md` vs `SOUL.md`
print("\nScanning for redundant internal files (e.g., *_soul.md)...")
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith("_soul.md") or file.endswith("_skill.md") or file.endswith("_style.md"):
            redundant_file = os.path.join(root, file)
            
            # Determine the primary target file name (SOUL.md, SKILL.md, STYLE.md)
            if "_soul" in file.lower():
                primary_name = "SOUL.md"
            elif "_skill" in file.lower():
                primary_name = "SKILL.md"
            elif "_style" in file.lower():
                primary_name = "STYLE.md"
            else:
                continue
                
            primary_file = os.path.join(root, primary_name)
            
            print(f"  Merging {file} into {primary_name} inside {os.path.basename(root)}")
            
            with open(redundant_file, "r") as f_red:
                red_content = f_red.read()
            
            if os.path.exists(primary_file):
                with open(primary_file, "a") as f_prim:
                    f_prim.write(f"\n\n<!-- --- MERGED FROM LEGACY FILE: {file} --- -->\n\n")
                    f_prim.write(red_content)
            else:
                with open(primary_file, "w") as f_prim:
                    f_prim.write(red_content)
            
            os.remove(redundant_file)

print("\nCleanup Complete.")
