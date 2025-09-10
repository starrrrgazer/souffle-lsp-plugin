import re
from collections import defaultdict
import csv
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold
import numpy as np
def process_log_file(log_file_path):
    document_data = defaultdict(dict)

    patterns = {
        'compile': re.compile(r'compile component: (\d+) document: (.+)$'),
        'locate': re.compile(r'locate: (\d+) document: (.+)$'),
        'search': re.compile(r'search: (\d+) document: (.+)$'),
        'NOD': re.compile(r'NOD: (\d+) document: (.+)$'),
        'DEF': re.compile(r'DEF: (\d+) document: (.+)$'),
        'OCC': re.compile(r'OCC: (\d+) document: (.+)$'),
        'LOC': re.compile(r'LOC: (\d+) document: (.+)$'),
        'gotoDefinition': re.compile(r'gotoDefinition: (\d+) document: (.+)$'),
        'rename': re.compile(r'rename: (\d+) document: (.+)$'),
        'completion': re.compile(r'completion: (\d+) document: (.+)$')
    }

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            for key, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    value = int(match.group(1))
                    document = match.group(2)
                    if key in document_data[document]:
                        current_value, count = document_data[document][key]
                        document_data[document][key] = (current_value + value, count + 1)
                    else:
                        document_data[document][key] = (value, 1)

    results = []
    for doc, data in document_data.items():
        result = {
            'document': doc,
            'compile_component': data.get('compile', (0, 1))[0] / data.get('compile', (0, 1))[1],
            'locate_component': data.get('locate', (0, 1))[0] / data.get('locate', (0, 1))[1],
            'search_component': data.get('search', (0, 1))[0] / data.get('search', (0, 1))[1],
            'NOD': data.get('NOD', (0, 1))[0] / data.get('NOD', (0, 1))[1],
            'DEF': data.get('DEF', (0, 1))[0] / data.get('DEF', (0, 1))[1],
            'OCC': data.get('OCC', (0, 1))[0] / data.get('OCC', (0, 1))[1],
            'LOC': data.get('LOC', (0, 1))[0] / data.get('LOC', (0, 1))[1],
            'gotoDefinition': data.get('gotoDefinition', (0, 1))[0] / data.get('gotoDefinition', (0, 1))[1],
            'rename': data.get('rename', (0, 1))[0] / data.get('rename', (0, 1))[1],
            'completion': data.get('completion', (0, 1))[0] / data.get('completion', (0, 1))[1]
        }
        results.append(result)

    return results


def merge_logs(metric_folder, output_log):
    """合并某个指标文件夹下所有 souffle.log"""
    with open(output_log, "w", encoding="utf-8") as out:
        for subdir, _, files in os.walk(metric_folder):
            if "souffle.log" in files:
                log_path = os.path.join(subdir, "souffle.log")
                with open(log_path, "r", encoding="utf-8") as f:
                    out.write(f.read())
                    out.write("\n")


def export_multi_to_csv(all_results, output_file):
    """把四个表导出到一个 CSV 文件"""
    fieldnames = ['document', 'compile_component', 'locate_component',
                  'search_component', 'NOD', 'DEF', 'OCC', 'LOC',
                  'gotoDefinition', 'rename', 'completion']
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        for metric, results in all_results.items():
            # 表名
            writer.writerow([f"===== {metric} Results ====="])
            # 表头
            writer.writerow(fieldnames)
            # 数据
            for r in results:
                writer.writerow([r[k] for k in fieldnames])
            writer.writerow([])  # 空行分隔

def analyze_feature_importance(all_results, output_file="feature_importance.csv"):
    """基于 permutation importance + KFold 计算特征重要性"""
    features = ['LOC', 'DEF', 'OCC', 'NOD']
    targets = ['locate_component', 'search_component',
               'gotoDefinition', 'rename', 'completion']

    # 收集所有数据
    all_data = []
    for metric, results in all_results.items():
        all_data.extend(results)

    
    df = pd.DataFrame(all_data).drop_duplicates(subset=["document"])
    X = df[features].to_numpy()
    importance_rows = []

    for target in targets:
        y = df[target].to_numpy()

        if len(np.unique(y)) <= 1:
            print(f"[跳过] {target} 没有有效数据")
            continue

        # KFold
        KF = KFold(n_splits=5, shuffle=True, random_state=42)
        avg_weights = np.zeros(len(features))

        for train_idx, test_idx in KF.split(X):
            xtrain, xtest = X[train_idx], X[test_idx]
            ytrain, ytest = y[train_idx], y[test_idx]

            model = RandomForestRegressor(n_estimators=200, random_state=42)
            model.fit(xtrain, ytrain)

            result = permutation_importance(model, xtest, ytest, n_repeats=10, random_state=42)

            avg_weights += result['importances_mean']

        avg_weights /= KF.get_n_splits()

        # 保存一行：target + 四个特征的重要性
        row = {"target": target}
        for f, w in zip(features, avg_weights):
            row[f] = w
        importance_rows.append(row)

    # 写 CSV
    fieldnames = ["target"] + features
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(importance_rows)

    print(f"基于 KFold 的特征重要性矩阵已保存到 {output_file}")



if __name__ == "__main__":
    root = "gen_datasets"
    metrics = ["LOC", "NOD", "OCC", "DEF"]
    all_results = {}

    for metric in metrics:
        metric_folder = os.path.join(root, metric)
        merged_log = os.path.join(root, f"souffle_{metric}.log")
        merge_logs(metric_folder, merged_log)
        results = process_log_file(merged_log)
        all_results[metric] = results
        print(f"[{metric}] 合并完成，生成 {merged_log}")

    export_multi_to_csv(all_results, "results_all.csv")
    analyze_feature_importance(all_results, "feature_importance.csv")
