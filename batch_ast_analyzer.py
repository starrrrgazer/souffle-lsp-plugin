import os
import sys
import pandas as pd
from antlr4 import *
from pathlib import Path
from datetime import datetime

from python_grammar.SouffleLexer import SouffleLexer
from python_grammar.SouffleParser import SouffleParser


class TreeStats:
    def __init__(self):
        self.max_degree = 0
        self.max_depth = 0


def compute_stats_non_recursive(root):
    """非递归计算 AST 最大度数与最大深度"""
    stats = TreeStats()
    stack = [(root, 1)]  # (node, depth)

    while stack:
        node, depth = stack.pop()
        child_count = node.getChildCount()

        stats.max_degree = max(stats.max_degree, child_count)
        stats.max_depth = max(stats.max_depth, depth)

        for i in range(child_count):
            stack.append((node.getChild(i), depth + 1))

    return stats


def compute_file_ast_stats(file_path):
    """解析单个文件并返回 (maxDegree, maxDepth)"""
    input_stream = FileStream(file_path, encoding="utf-8")
    lexer = SouffleLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = SouffleParser(tokens)

    tree = parser.program()

    stats = compute_stats_non_recursive(tree)
    return stats.max_degree, stats.max_depth


def normalize_path_windows_to_unix(p: str) -> str:
    """将 Windows 路径改为 d:/path/like/this 格式，盘符小写"""
    path = Path(p).resolve().as_posix()
    # 如果是 Windows 驱动器路径，把开头的 "D:" -> "d:"
    if len(path) >= 2 and path[1] == ":":
        path = path[0].lower() + path[1:]
    return path


def get_log_time_str():
    """返回中文时间格式，例如 10月 09, 2025 10:05:05 上午"""
    now = datetime.now()
    am_pm = "上午" if now.hour < 12 else "下午"
    return now.strftime(f"%m月 %d, %Y %I:%M:%S {am_pm}")


def append_log(dataset_name: str, deg: int, dep: int, filepath: str):
    """将 DEG 和 DEP 结果追加到对应 log 文件"""
    log_dir = Path("gen_datasets")
    log_path = log_dir / f"souffle_{dataset_name}.log"

    time_str = get_log_time_str()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{time_str} SouffleTextDocumentService countMaxDegree\n")
        f.write(f"信息: DEG: {deg} document: {filepath}\n\n")
        f.write(f"{time_str} SouffleTextDocumentService countMaxDepth\n")
        f.write(f"信息: DEP: {dep} document: {filepath}\n\n")


def main():
    # 防止递归深度过浅
    sys.setrecursionlimit(20000)

    project_root = Path(__file__).resolve().parent
    dataset_dir = project_root / "gen_datasets"
    output_path = project_root / "ast_stats.xlsx"

    dataset_whitelist = {"LOC", "OCC", "DEF", "NOD"}

    if not dataset_dir.exists():
        print(f"文件夹不存在: {dataset_dir}")
        return

    dl_files = sorted(dataset_dir.glob("**/*.dl"))
    if not dl_files:
        print(f"未找到 .dl 文件于 {dataset_dir}")
        return

    print(f"扫描到 {len(dl_files)} 个 .dl 文件")

    results = []

    for i, file_path in enumerate(dl_files, 1):
        abs_path = file_path.resolve()
        unix_path = normalize_path_windows_to_unix(abs_path)

        # 推断 dataset_name
        try:
            relative_parts = file_path.relative_to(dataset_dir).parts
            candidate = relative_parts[0] if relative_parts else "unknown"
            dataset_name = candidate if candidate in dataset_whitelist else "unknown"
        except Exception:
            dataset_name = "unknown"

        try:
            max_degree, max_depth = compute_file_ast_stats(str(abs_path))
            results.append({
                "File (Absolute Path)": unix_path,
                "Dataset": dataset_name,
                "Max Degree": max_degree,
                "Max Depth": max_depth
            })

            # 仅在白名单 dataset 时写日志
            if dataset_name != "unknown":
                append_log(dataset_name, max_degree, max_depth, unix_path)

            print(f"[{i}/{len(dl_files)}]  {unix_path}")
        except Exception as e:
            print(f"[{i}/{len(dl_files)}] {unix_path}: {e}")

    if results:
        df = pd.DataFrame(results)
        df.to_excel(output_path, index=False)
        print(f"\n结果已写入: {output_path}")
    else:
        print("没有成功的结果，未生成Excel。")


if __name__ == "__main__":
    main()
