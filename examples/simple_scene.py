"""Simple example: create a scene plan and print the storyboard."""

from genesis.dsl import parse_scene_request, validate_scene
from genesis.native_inhouse import InHousePipeline


def main():
    prompt = "Create a 20 second product launch intro in 9:16"

    print(f"Prompt: {prompt}\n")

    scene = parse_scene_request(prompt)
    validation = validate_scene(scene)

    print("=== Validation ===")
    for issue in validation["issues"]:
        print(f"  [{issue['severity']}] {issue['issue']}")
    print(f"  Approved: {validation['approved']}\n")

    if not validation["approved"]:
        print("Scene not approved — cannot proceed.")
        return

    pipeline = InHousePipeline()
    plan = pipeline.plan(prompt)

    print("=== Storyboard ===")
    for beat in plan["storyboard"]:
        print(f"  Shot {beat['shot']}: {beat['visual']} ({beat['duration']})")
    print()

    print("=== Quality Gate ===")
    qg = plan["quality_gate"]
    print(f"  Approved: {qg['approved']}")
    for issue in qg["issues"]:
        print(f"  - {issue['severity']}: {issue['issue']}")
    print()

    print("=== Manifest ===")
    manifest = plan["manifest"]
    print(f"  Project: {manifest['project_id']}")
    print(f"  Mode: {manifest['mode']}")
    print(f"  Native components: {', '.join(manifest['native_components'])}")
    print(f"  Plugin components: {', '.join(manifest['plugin_components']) or 'none'}")

    print("\nDone.")


if __name__ == "__main__":
    main()
