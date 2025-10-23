#!/usr/bin/env python3
import os
import subprocess
import glob

# 你的输入文件所在文件夹
input_dir = "/share/org/YZWL/yzwl_liubx/guotb/HOR/HOR_SCORE/results_AA_Ogla"   # 改成你的文件夹路径，例如 "D:/HOR_analysis/"
script = "/share/org/YZWL/yzwl_liubx/lxr/HOR/Recompute_Hor_Score.py"  # 脚本路径

# 扫描目录下所有 hor_pairs 文件
pairs_files = sorted(glob.glob(os.path.join(input_dir, "*.hor_pairs.tsv")))

for pairs in pairs_files:
    # 推断对应的 hor_score 文件
    prefix = pairs.replace(".hor_pairs.tsv", "")
    score = prefix + ".hor_score.tsv"
    
    if not os.path.exists(score):
        print(f"[跳过] 找不到对应的 hor_score 文件: {score}")
        continue
    
    # 输出文件名
    out = prefix + ".hor_score_continuous.tsv"
    
    # 构造命令
    cmd = [
        "python", script,
        "--hor_pairs", pairs,
        "--hor_score", score,
        "--out", out,
        "--decimals", "4",        # 可调
        "--scheme", "paper"       # 可改为 partners_only / forms_only / hybrid
    ]
    
    print("[运行] " + " ".join(cmd))
    subprocess.run(cmd)
