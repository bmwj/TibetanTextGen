import random
import os
import sys
import argparse

def select_sample(input_file, output_file, sample_percentage=5):
    """
    从大文件中随机选择指定百分比的内容并保存到新文件（内存优化版）
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        sample_percentage (float): 采样百分比 (默认5%)
    """
    # 第一次遍历：计算文件总行数
    print("正在计算文件总行数...")
    total_lines = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        for _ in f:
            total_lines += 1
    
    print(f"文件总行数: {total_lines}")
    
    # 计算需要选择的行数
    sample_size = int(total_lines * sample_percentage / 100)
    print(f"需要选择的行数: {sample_size} ({sample_percentage}%)")
    
    # 使用 reservior sampling 算法进行随机采样（节省内存）
    print("正在进行随机采样...")
    selected_lines = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(infile, 1):
            if line_num <= sample_size:
                selected_lines.append(line)
            else:
                # 以 sample_size/line_num 的概率替换已选行中的一个
                rand_index = random.randint(1, line_num)
                if rand_index <= sample_size:
                    selected_lines[rand_index - 1] = line
            
            # 显示进度
            if line_num % 10000 == 0:
                print(f"已处理 {line_num} 行...")
    
    # 写入选中的行到新文件
    print("正在写入选中的行到文件...")
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for line in selected_lines:
            outfile.write(line)
    
    print(f"完成！已将 {len(selected_lines)} 行内容保存到 {output_file}")

def select_first_lines(input_file, output_file, sample_percentage=5):
    """
    选择文件前指定百分比的内容并保存到新文件（最节省内存的方法）
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        sample_percentage (float): 采样百分比 (默认5%)
    """
    # 第一次遍历：计算文件总行数
    print("正在计算文件总行数...")
    total_lines = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        for _ in f:
            total_lines += 1
    
    print(f"文件总行数: {total_lines}")
    
    # 计算需要选择的行数
    sample_size = int(total_lines * sample_percentage / 100)
    print(f"需要选择的行数: {sample_size} ({sample_percentage}%)")
    
    # 读取前sample_size行并写入新文件
    print("正在选择并写入文件...")
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            if line_num <= sample_size:
                outfile.write(line)
            else:
                break
            
            # 显示进度
            if line_num % 10000 == 0:
                print(f"已处理 {line_num} 行...")
    
    print(f"完成！已将前 {sample_size} 行内容保存到 {output_file}")

def select_first_n_lines(input_file, output_file, num_lines=10000):
    """
    选择文件前指定行数的内容并保存到新文件
    
    Args:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        num_lines (int): 要保留的行数 (默认10000行)
    """
    print(f"正在选择并写入文件的前 {num_lines} 行...")
    
    lines_written = 0
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            if line_num <= num_lines:
                outfile.write(line)
                lines_written += 1
            else:
                break
            
            # 显示进度
            if line_num % 10000 == 0:
                print(f"已处理 {line_num} 行...")
    
    print(f"完成！已将前 {lines_written} 行内容保存到 {output_file}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='从大文件中抽取指定百分比的内容')
    parser.add_argument('--input', '-i', type=str, 
                        default="/root/autodl-tmp/synthtiger/tib_text/new_file.txt",
                        help='输入文件路径 (默认: /root/autodl-tmp/synthtiger/tib_text/new_file.txt)')
    parser.add_argument('--output', '-o', type=str,
                        default="/root/autodl-tmp/synthtiger/tib_text/sampled_new_file.txt",
                        help='输出文件路径 (默认: /root/autodl-tmp/synthtiger/tib_text/sampled_new_file.txt)')
    parser.add_argument('--percentage', '-p', type=float, default=5,
                        help='抽取百分比 (默认: 5)')
    parser.add_argument('--method', '-m', type=str, choices=['first', 'random'], default='first',
                        help='抽取方法: first(前N行) 或 random(随机) (默认: first)')
    parser.add_argument('--lines', '-l', type=int, default=10000,
                        help='要保留的行数 (默认: 10000)')
    parser.add_argument('--mode', type=str, choices=['percentage', 'lines'], default='lines',
                        help='选择模式: percentage(按百分比) 或 lines(按行数) (默认: lines)')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # 根据选择的模式执行相应操作
    if args.mode == 'percentage':
        # 根据选择的方法执行采样
        if args.method == 'random':
            print(f"使用随机采样方法选择{args.percentage}%内容...")
            select_sample(args.input, args.output, args.percentage)
        else:
            print(f"使用前N行采样方法选择{args.percentage}%内容...")
            select_first_lines(args.input, args.output, args.percentage)
    else:
        print(f"保留文件的前 {args.lines} 行...")
        select_first_n_lines(args.input, args.output, args.lines)

if __name__ == "__main__":
    main()


# 执行命令如下
# 使用默认参数（保留前10000行）
# python tools/sample_text_selector.py --mode lines

# 保留前5000行
# python tools/sample_text_selector.py --mode lines --lines 5000

# 抽取10%的内容
# python tools/sample_text_selector.py --mode percentage --percentage 10

# 抽取3%的随机内容
# python tools/sample_text_selector.py --mode percentage --percentage 3 --method random

# 指定自定义输入输出文件
# python tools/sample_text_selector.py --input /path/to/input.txt --output /path/to/output.txt --mode lines --lines 10000