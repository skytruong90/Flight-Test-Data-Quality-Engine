import argparse,json
from pathlib import Path
from .core import check_file,generate,markdown

def main()->None:
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True);g=s.add_parser("generate");g.add_argument("path");g.add_argument("--samples",type=int,default=300);c=s.add_parser("check");c.add_argument("source");c.add_argument("--rules",required=True);c.add_argument("--report",default="output/report.json");c.add_argument("--markdown",default="output/report.md");a=p.parse_args()
    if a.cmd=="generate":generate(a.path,a.samples);return
    r=check_file(a.source,json.loads(Path(a.rules).read_text()));rp=Path(a.report);rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(r,indent=2));mp=Path(a.markdown);mp.parent.mkdir(parents=True,exist_ok=True);mp.write_text(markdown(r));print(json.dumps({k:v for k,v in r.items() if k!="findings"},indent=2));raise SystemExit(0 if r["accepted"] else 2)
