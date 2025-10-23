import os
import argparse
import pandas as pd
import sys
import pyranges as pr # 导入 pyranges 库

# --- 1. 参数解析 ---
parser = argparse.ArgumentParser(description="诊断Pyranges重叠操作的输出列名和数据。")
parser.add_argument('--bed', type=str, required=True, help='TE注释BED文件路径。')
args = parser.parse_args()

# --- 2. 检查文件是否存在 ---
if not os.path.exists(args.bed):
    print(f"错误: BED文件 '{args.bed}' 不存在。", file=sys.stderr)
    sys.exit(1)

print(f"\n--- 正在诊断 BED 文件: '{args.bed}' 的Pyranges重叠结果 ---")

try:
    # 使用pandas读取BED文件，指定分隔符和列名，跳过注释行
    bed_columns = ['Chromosome', 'Start', 'End', 'Name', 'Score', 'Strand', 'ThickStart', 'ThickEnd', 'ItemRgb']
    raw_bed_df = pd.read_csv(args.bed, sep='\t', header=None, comment='#', names=bed_columns)
    
    # 过滤掉可能存在的“track”或其他非数据行
    bed_df = raw_bed_df[~raw_bed_df['Chromosome'].astype(str).str.startswith('track')].reset_index(drop=True)

    # 从Name字段中提取TE种类（冒号前的部分）到新列 'te_kind'
    def extract_te_kind(name_field):
        if pd.isna(name_field): # 处理NaN值
            return None
        name_field_str = str(name_field)
        first_colon_index = name_field_str.find(':')
        if first_colon_index != -1:
            return name_field_str[:first_colon_index]
        else:
            return name_field_str

    bed_df['te_kind'] = bed_df['Name'].apply(extract_te_kind)
    
    # 添加一个原始索引列，用于区分同一TE的重复条目
    bed_df['original_bed_idx'] = bed_df.index
    
    print(f"BED文件包含 {len(bed_df)} 条有效TE注释。")

    # 为Pyranges准备数据框 (作为A端)
    # Pyranges需要 Chromosome, Start, End
    # 我们传入所有原始列，它们将作为重叠结果中的A端列
    pr_A_df = bed_df.copy() # 复制整个DataFrame
    gr_A = pr.PyRanges(pr_A_df)

    # 为Pyranges准备第二个数据框 (作为B端)
    # 这里不进行任何预重命名，让 Pyranges 自动处理列名冲突，以便我们诊断其默认行为
    pr_B_df = bed_df.copy() # 复制整个DataFrame
    pr_B = pr.PyRanges(pr_B_df)

    print("\n--- 执行 Pyranges 重叠操作... ---")
    overlaps = gr_A.overlap(pr_B) 

    # 检查重叠结果的列名
    print("\n--- 重叠结果 DataFrame 的列名 ---")
    print(overlaps.df.columns.tolist())

    # 检查重叠结果的前几行数据
    print("\n--- 重叠结果 DataFrame 的前 5 行数据示例 ---")
    # 为了避免输出过长，只打印部分列，并且如果列不存在则跳过
    display_cols = ['Chromosome', 'Start', 'End', 'Name', 'te_kind', 'original_bed_idx', 
                    'Start_b', 'End_b', 'Name_b', 'te_kind_b', 'original_bed_idx_b']
    
    # 过滤掉不存在的列，只打印实际存在的列
    actual_display_cols = [col for col in display_cols if col in overlaps.df.columns]
    
    if not overlaps.df.empty:
        # 使用 .loc 来避免SettingWithCopyWarning，并确保只选择实际存在的列
        print(overlaps.df.loc[:, actual_display_cols].head())
    else:
        print("重叠结果 DataFrame 为空。可能没有重叠或数据处理错误。")
    
    # 额外诊断：打印重叠结果中有哪些_b后缀的列
    _b_cols_found = [col for col in overlaps.df.columns if col.endswith('_b')]
    if _b_cols_found:
        print(f"\n--- 额外诊断: 发现以下带 '_b' 后缀的列 ---")
        print(_b_cols_found)
    else:
        print(f"\n--- 额外诊断: 未发现带 '_b' 后缀的列。Pyranges可能以不同方式处理了列名冲突。---")


except pd.errors.EmptyDataError:
    print(f"错误: BED文件 '{args.bed}' 为空。", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"错误: 执行Pyranges操作时发生错误: {e}", file=sys.stderr)
    # 打印完整的Traceback以便调试
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

print("\n--- 诊断完成 ---")