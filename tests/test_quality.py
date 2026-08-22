from pathlib import Path
from flight_quality.core import check_file,generate

def test_clean_generated_data_is_accepted(tmp_path:Path)->None:
    p=tmp_path/"d.csv";generate(p,100);rules={"required_columns":["seq","t","altitude_m","vn_mps","ve_mps","vz_mps","speed_mps"],"ranges":{"altitude_m":[0,20000]},"max_time_gap_s":0.2,"max_rate":{"altitude_m":30},"speed_consistency_tolerance":0.25,"minimum_quality_score":95};assert check_file(p,rules)["accepted"]
