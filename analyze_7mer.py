import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 设置绘图风格
sns.set_style('whitegrid')

# 假设文件路径
# 请将这些文件放置在脚本运行的同一目录下
te_abundance_file = "AA_Osat_jap_hap1.All.all.bed"
satellite_abundance_file = "AA_Osat_jap_hap1_satellite.bed"
overlap_file = "te_satellite_overlaps_final.csv"

# 1. 加载数据
print("--- 正在加载数据 ---")
try:
    # 修复：TE文件实际只有4列，根据你之前提供的信息，这4列应该是：
    # chrom, chromStart, chromEnd, name (TE的详细名称)
    te_cols = ['chrom', 'chromStart', 'chromEnd', 'name']
    te_df = pd.read_csv(te_abundance_file, sep='\t', header=None, names=te_cols)
    
    # 修复：Satellite文件实际有8列，前4列应该是：
    # chrom, chromStart, chromEnd, name (卫星家族名称)
    satellite_cols = ['chrom', 'chromStart', 'chromEnd', 'name', 'score', 'strand', 'thickStart', 'thickEnd']
    satellite_df = pd.read_csv(satellite_abundance_file, sep='\t', header=None, names=satellite_cols, usecols=[0, 1, 2, 3])

    # 加载重叠文件 (格式没有变化)
    overlap_df = pd.read_csv(overlap_file)
    
    print("所有文件加载成功。")

except FileNotFoundError as e:
    print(f"错误: 文件 {e.filename} 未找到。请确保文件与脚本在同一目录下。")
    print(f"当前工作目录是: {os.getcwd()}")
    exit()
except pd.errors.ParserError as e:
    print(f"错误: 解析文件时出错。请检查文件分隔符是否为制表符，以及列数是否与代码中的设定一致。")
    print(f"具体错误: {e}")
    exit()
except Exception as e:
    print(f"加载文件时发生未知错误: {e}")
    exit()

# 2. 数据清洗和归类
print("\n--- 正在处理 TE 和 Satellite 丰度数据 ---")

# 从TE的详细名称中提取大类
te_df['TE_Category'] = te_df['name'].str.split(':').str[0]
te_df['TE_Length'] = te_df['chromEnd'] - te_df['chromStart']

# 计算每个TE大类的总丰度（总长度）
te_abundance = te_df.groupby('TE_Category')['TE_Length'].sum().reset_index()
te_abundance.rename(columns={'TE_Length': 'Total_TE_Length'}, inplace=True)

# 计算每个卫星家族的总丰度（总长度）
satellite_df['Satellite_Length'] = satellite_df['chromEnd'] - satellite_df['chromStart']
satellite_abundance = satellite_df.groupby('name')['Satellite_Length'].sum().reset_index()
satellite_abundance.rename(columns={'name': 'Satellite_Name', 'Satellite_Length': 'Total_Satellite_Length'}, inplace=True)

# 打印一些摘要信息
print("\nTE 大类总丰度:")
print(te_abundance.head())
print("\nSatellite 家族总丰度:")
print(satellite_abundance.head())


# 3. 计算重叠丰度
print("\n--- 正在计算 TE 与 Satellite 的总重叠长度 ---")

# 从重叠文件中提取 TE 大类
overlap_df['TE_Category'] = overlap_df['TE_Kind'].str.split(':').str[0]
overlap_counts = overlap_df.groupby(['TE_Category', 'Satellite_Name'])['Overlap_Length'].sum().reset_index()

print("\n重叠总长度摘要:")
print(overlap_counts.head())


# 4. 构建丰度矩阵
print("\n--- 正在构建丰度矩阵 ---")
abundance_matrix = overlap_counts.pivot_table(
    index='TE_Category', 
    columns='Satellite_Name', 
    values='Overlap_Length', 
    fill_value=0
)

# 5. 归一化：将重叠长度除以TE或卫星的总丰度
# 这里选择除以TE大类的总丰度，来衡量“一个TE家族的DNA有多少百分比与某个卫星重叠”
abundance_matrix_normalized = abundance_matrix.copy()
for te_category in abundance_matrix_normalized.index:
    # 确保te_abundance数据框不为空
    if not te_abundance[te_abundance['TE_Category'] == te_category]['Total_TE_Length'].empty:
        total_te_length = te_abundance[te_abundance['TE_Category'] == te_category]['Total_TE_Length'].iloc[0]
        if total_te_length > 0:
            abundance_matrix_normalized.loc[te_category] = abundance_matrix_normalized.loc[te_category] / total_te_length
        else:
            abundance_matrix_normalized.loc[te_category] = 0
    else:
        abundance_matrix_normalized.loc[te_category] = 0

print("\n归一化后的丰度矩阵（TE总丰度占比）:")
print(abundance_matrix_normalized)


# 6. 可视化：绘制热图
print("\n--- 正在绘制热图 ---")

plt.figure(figsize=(12, 10))
sns.heatmap(
    abundance_matrix_normalized, 
    annot=True, 
    fmt=".2%",  # 以百分比格式显示，保留两位小数
    cmap="viridis", 
    cbar_kws={'label': '重叠长度占TE总长度的比例'}
)
plt.title('TE大类与卫星家族重叠丰度（归一化）', fontsize=16)
plt.xlabel('卫星家族', fontsize=12)
plt.ylabel('TE大类', fontsize=12)
plt.tight_layout()
plt.show()

print("\n分析完成。")