import os
import sys

def update_bed_name_column(directory_path):
    """
    遍历指定目录下的所有.bed文件，将每个文件的第四列（name）
    修改为文件本身的名称（不含.bed后缀）。

    Args:
        directory_path (str): 包含.bed文件的文件夹路径。
    """
    # 检查文件夹是否存在
    if not os.path.isdir(directory_path):
        print(f"错误: 文件夹 '{directory_path}' 不存在。请检查路径。", file=sys.stderr)
        return

    print(f"正在处理文件夹: {directory_path}")
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(directory_path):
        # 筛选出以 '.bed' 结尾的文件
        if filename.endswith(".bed"):
            input_filepath = os.path.join(directory_path, filename)
            
            # 创建输出文件路径
            # 例如：'AA_Ogla_hap1.bed' -> 'AA_Ogla_hap1_updated.bed'
            file_base_name = os.path.splitext(filename)[0]
            output_filename = f"{file_base_name}_updated.bed"
            output_filepath = os.path.join(directory_path, output_filename)
            
            print(f"正在处理文件: {filename}")
            
            try:
                # 以列表形式存储修改后的所有行
                updated_lines = []
                
                with open(input_filepath, 'r') as infile:
                    for line in infile:
                        parts = line.strip().split('\t')
                        
                        # 确保行有足够的列，至少4列
                        if len(parts) >= 4:
                            # 将第四列更新为文件名
                            parts[3] = file_base_name
                            
                            # 重新组合成一行
                            updated_line = '\t'.join(parts)
                            updated_lines.append(updated_line)
                        else:
                            # 如果行不符合预期格式，保留原样或跳过
                            updated_lines.append(line.strip())
                            
                # 将修改后的内容写入新的文件
                with open(output_filepath, 'w') as outfile:
                    outfile.write('\n'.join(updated_lines) + '\n')
                    
                print(f"文件 '{filename}' 处理完毕。已保存到 '{output_filename}'.")
                
            except Exception as e:
                print(f"处理文件 '{filename}' 时发生错误: {e}", file=sys.stderr)
                
    print("\n所有文件处理完成。")

# --- 主程序入口 ---
if __name__ == "__main__":
    # 请将此路径替换为您实际的文件夹路径
    bed_directory = r"C:\Users\10042\Desktop\13.bed"
    update_bed_name_column(bed_directory)