"""Extract exact proof data from numerical discovery output."""
import json
from pathlib import Path


def main():
    root=Path(__file__).resolve().parent
    target=root/"certificates"
    target.mkdir(exist_ok=True)
    for name in ("two","three","four","parity","five","six"):
        source=json.loads((root/f"cover-{name}-scout.json").read_text())
        if not source["complete"] or source["pending"]:
            raise ValueError("Discovery tree is incomplete")
        data={"format":"rbm31-convex-cover-v1","support":source["support"],
              "splits":source["splits"],
              "leaves":[{"path":r["path"],"witness":r["witness"]} for r in source["leaves"]]}
        path=target/f"{name}.json"
        path.write_text(json.dumps(data,sort_keys=True,separators=(",",":"))+"\n")
        print(path.name,len(data["leaves"]),"leaves")


if __name__=="__main__":
    main()
