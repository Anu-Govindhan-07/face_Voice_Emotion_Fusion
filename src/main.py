from __future__ import annotations

import argparse
import json

from src.pipeline.run_job import run_job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run full video pipeline job")
    parser.add_argument("--video", required=True, help="Path to input video")
    parser.add_argument("--job_id", required=True, help="Unique job id")
    parser.add_argument("--config", default="config/default.yaml", help="Config YAML path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_job(video_path=args.video, job_id=args.job_id, config_path=args.config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
