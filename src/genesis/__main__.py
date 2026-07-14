from __future__ import annotations

import argparse
import json
import sys


def main() -> None:
    parser = argparse.ArgumentParser(prog="genesis", description="Genesis Media Engine CLI")
    parser.add_argument("prompt", nargs="?", help="Scene description prompt")
    parser.add_argument("--render", help="Output path for rendered video")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()
    prompt = args.prompt or "Create a 20 second intro in 9:16"

    from genesis.dsl import parse_scene_request, validate_scene
    from genesis.native_inhouse import InHousePipeline

    scene = parse_scene_request(prompt)
    validation = validate_scene(scene)

    if not validation["approved"]:
        print("Scene validation failed:")
        for issue in validation["issues"]:
            print(f"  [{issue['severity']}] {issue['issue']}")
        sys.exit(1)

    pipeline = InHousePipeline()
    if args.render:
        result = pipeline.render(prompt, args.render)
    else:
        result = pipeline.plan(prompt)

    if args.format == "json":
        json.dump(result, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        pid = result.get("project_id") or "unknown"
        ok = result.get("ok", result.get("veda_validation", {}).get("approved", False))
        status = "OK" if ok else "FAIL"
        print(f"[{status}] project_id={pid}")
        if not ok:
            issues = result.get("veda_validation", {}).get("issues", [])
            for issue in issues:
                print(f"  - {issue.get('issue', 'unknown')}")
        if args.render:
            print(f"  output: {result.get('output_path', 'N/A')}")


if __name__ == "__main__":
    main()
