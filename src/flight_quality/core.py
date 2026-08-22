from __future__ import annotations
import csv,json,math
from pathlib import Path
from typing import Any

def check_file(source:str|Path,rules:dict[str,Any])->dict[str,Any]:
    with Path(source).open(newline="") as h:rows=list(csv.DictReader(h))
    findings=[];required=set(rules["required_columns"])
    if rows and not required<=set(rows[0]):findings.append({"rule":"SCHEMA","severity":"error","row":None,"detail":f"missing {sorted(required-set(rows[0]))}"})
    previous=None;seen=set()
    for idx,row in enumerate(rows,2):
        for col in required:
            if row.get(col,"")=="":findings.append({"rule":"NULL","severity":"error","row":idx,"detail":col})
        try:seq=int(row["seq"]);t=float(row["t"])
        except (ValueError,KeyError):continue
        if seq in seen:findings.append({"rule":"DUPLICATE_SEQ","severity":"error","row":idx,"detail":str(seq)})
        seen.add(seq)
        for col,bounds in rules.get("ranges",{}).items():
            try:value=float(row[col])
            except (ValueError,KeyError):continue
            if value<float(bounds[0]) or value>float(bounds[1]):findings.append({"rule":"RANGE","severity":"error","row":idx,"detail":f"{col}={value}"})
        if previous is not None:
            pt=float(previous["t"]);dt=t-pt
            if dt<=0:findings.append({"rule":"TIME_ORDER","severity":"error","row":idx,"detail":str(t)})
            elif dt>float(rules.get("max_time_gap_s",1.0)):findings.append({"rule":"TIME_GAP","severity":"warning","row":idx,"detail":str(dt)})
            for col,limit in rules.get("max_rate",{}).items():
                if dt>0:
                    rate=abs(float(row[col])-float(previous[col]))/dt
                    if rate>float(limit):findings.append({"rule":"RATE","severity":"warning","row":idx,"detail":f"{col}={rate}"})
        if all(k in row for k in ("vn_mps","ve_mps","vz_mps","speed_mps")):
            mag=math.sqrt(sum(float(row[k])**2 for k in ("vn_mps","ve_mps","vz_mps")))
            if abs(mag-float(row["speed_mps"]))>float(rules.get("speed_consistency_tolerance",0.5)):findings.append({"rule":"SPEED_CONSISTENCY","severity":"warning","row":idx,"detail":f"expected {mag}"})
        previous=row
    errors=sum(f["severity"]=="error" for f in findings);warnings=sum(f["severity"]=="warning" for f in findings);score=max(0.0,100.0-errors*10-warnings*2);minimum=float(rules.get("minimum_quality_score",90));return {"rows":len(rows),"findings":findings,"errors":errors,"warnings":warnings,"quality_score":score,"minimum_quality_score":minimum,"accepted":errors==0 and score>=minimum}

def markdown(result:dict[str,Any])->str:
    lines=["# Flight Data Quality Report","",f"Status: **{'ACCEPTED' if result['accepted'] else 'REJECTED'}**",f"Quality score: **{result['quality_score']}**","", "| Rule | Severity | Row | Detail |","|---|---|---:|---|"]
    for f in result["findings"]:lines.append(f"| {f['rule']} | {f['severity']} | {f['row'] or '-'} | {f['detail']} |")
    return "\n".join(lines)+"\n"

def generate(path:str|Path,samples:int=300)->None:
    target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);fields=["seq","t","altitude_m","vn_mps","ve_mps","vz_mps","speed_mps"]
    with target.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=fields);w.writeheader()
        for i in range(samples):
            t=i*0.1;vn=120-0.01*i;ve=2*math.sin(i/30);vz=1.5;speed=math.sqrt(vn*vn+ve*ve+vz*vz);w.writerow({"seq":i,"t":t,"altitude_m":1000+1.5*t,"vn_mps":vn,"ve_mps":ve,"vz_mps":vz,"speed_mps":speed})
