# libs/blueprint_arch/tests/debug_blueprint_mapper.py
from utils.config_loader import ConfigManager
from blueprint_arch.blueprint_mapper import BlueprintMapper
from pathlib import Path


def test_mapper():
    manifest_path = "config/manifests/pipelines/1_test_data_ST22_dummy.yaml"
    print(f"Testing BlueprintMapper with: {manifest_path}")

    if not Path(manifest_path).exists():
        print(f"ERROR: {manifest_path} not found.")
        return

    cm = ConfigManager(manifest_path)
    mapper = BlueprintMapper(cm.raw_config)
    mermaid_code = mapper.generate_mermaid()

    print("\n--- GENERATED MERMAID CODE ---")
    print(mermaid_code)
    print("------------------------------")

    # Save to tmp for @verify
    output_dir = Path("tmp/Blueprint_Audit")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "ST22_tubemap.mmd", "w") as f:
        f.write(mermaid_code)

    print(f"\nSaved to: {output_dir}/ST22_tubemap.mmd")


if __name__ == "__main__":
    test_mapper()
