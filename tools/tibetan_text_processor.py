import re
import random
import csv
import os
import argparse
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from PIL import Image
import numpy as np


class TextMerger:
    def __init__(self, file_path, output_folder, max_length=20):
        self.file_path = file_path
        self.output_folder = output_folder
        self.max_length = max_length  # 添加最大长度参数
        self.output_file_path_txt = os.path.join(output_folder, 'merged_output.txt')
        self.output_file_path_csv = os.path.join(output_folder, 'merged_output.csv')
        os.makedirs(self.output_folder, exist_ok=True)

    def process(self):
        if not os.path.exists(self.file_path):
            print("文件未找到")
            return
            
        try:
            print(f"开始流式处理文件，最大文本长度: {self.max_length}...")
            self.stream_process()
            print("处理完成")
        except IOError as e:
            print(f"处理文件时发生错误: {e}")
        except MemoryError:
            print("内存不足，请尝试减小文件大小或增加系统内存")
        except Exception as e:
            print(f"处理过程中发生未知错误: {e}")

    def stream_process(self):
        # 初始化输出文件
        with open(self.output_file_path_txt, 'w', encoding='utf-8') as output_file_txt:
            pass  # 创建空文件
        with open(self.output_file_path_csv, 'w', encoding='utf-8', newline='') as output_file_csv:
            writer = csv.writer(output_file_csv)
            writer.writerow(['编号', '内容', '长度'])
        
        # 流式处理
        current_text = ''
        line_count = 0
        
        # 逐行读取输入文件
        with open(self.file_path, 'r', encoding='utf-8') as input_file:
            for line_num, line in enumerate(input_file, 1):
                if line_num % 1000 == 0:
                    print(f"已处理 {line_num} 行...")
                
                # 按藏文分词符分割
                parts = re.split(r'(?<=་)', line.strip())
                
                # 处理每个部分
                for part in parts:
                    if part == '་':
                        current_text += part
                    else:
                        # 使用动态设置的最大长度
                        if len(current_text) + len(part) <= self.max_length:
                            current_text += part
                        else:
                            if current_text:  # 只添加非空文本
                                line_count += 1
                                self.append_output(current_text, line_count)
                            current_text = part
        
        # 处理最后一个文本块
        if current_text:
            line_count += 1
            self.append_output(current_text, line_count)
            
        print(f"总共生成了 {line_count} 行文本")

    def append_output(self, text, line_number):
        # 追加到TXT文件
        with open(self.output_file_path_txt, 'a', encoding='utf-8') as output_file_txt:
            output_file_txt.write(text + '\n')
        
        # 追加到CSV文件
        with open(self.output_file_path_csv, 'a', encoding='utf-8', newline='') as output_file_csv:
            writer = csv.writer(output_file_csv)
            writer.writerow([line_number, text, len(text)])


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='藏文文本处理器')
    parser.add_argument('--input', '-i', type=str, 
                        default='./tib_text/Fiveline_10000.txt',
                        help='输入文件路径 (默认: ./tib_text/Fiveline_10000.txt)')
    parser.add_argument('--output', '-o', type=str,
                        default='./tib_text',
                        help='输出文件夹路径 (默认: ./tib_text)')
    parser.add_argument('--max-length', '-l', type=int, default=20,
                        help='最大文本长度 (默认: 20)')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 创建并运行TextMerger
    merger = TextMerger(args.input, args.output, args.max_length)
    merger.process()


if __name__ == "__main__":
    main()


# # 使用默认参数（最大长度20）
# python tools/tibetan_text_processor.py

# # 设置最大文本长度为15
# python tools/tibetan_text_processor.py --max-length 15

# # 指定自定义输入输出路径
# python tools/tibetan_text_processor.py --input /path/to/input.txt --output /path/to/output --max-length 25

# # 使用短参数格式
# python tools/tibetan_text_processor.py -i /path/to/input.txt -o /path/to/output -l 30