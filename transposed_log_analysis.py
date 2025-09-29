import re
from collections import defaultdict
import csv
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


RENAME = 1.25

def process_log_file(log_file_path):
    from collections import defaultdict
    import os, re

    document_data = defaultdict(dict)

    # 支持浮点数
    patterns = {
        'search': re.compile(r'search: (\d+(?:\.\d+)?) document: (.+)$'),
        'locate': re.compile(r'locate: (\d+(?:\.\d+)?) document: (.+)$'),
        'traverse': re.compile(r'traverse: (\d+(?:\.\d+)?) document: (.+)$'),
        'traverseTimes': re.compile(r'traverseTimes: (\d+(?:\.\d+)?) document: (.+)$'),
        'NOD': re.compile(r'NOD: (\d+(?:\.\d+)?) document: (.+)$'),
        'DEF': re.compile(r'DEF: (\d+(?:\.\d+)?) document: (.+)$'),
        'OCC': re.compile(r'OCC: (\d+(?:\.\d+)?) document: (.+)$'),
        'LOC': re.compile(r'LOC: (\d+(?:\.\d+)?) document: (.+)$'),
        'gotoDefinition': re.compile(r'gotoDefinition: (\d+(?:\.\d+)?) document: (.+)$'),
        'rename': re.compile(r'rename: (\d+(?:\.\d+)?) document: (.+)$'),
        'completion': re.compile(r'completion: (\d+(?:\.\d+)?) document: (.+)$'),
        # 'subcontextNum': re.compile(r'subcontextNum: (\d+(?:\.\d+)?) document: (.+)$')
    }

    # 从文件名推断 dataset
    base = os.path.basename(log_file_path)         # e.g. souffle_LOC.log
    dataset = base.replace("souffle_", "").replace(".log", "").upper()

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            for key, pattern in patterns.items():
                match = pattern.search(line)
                if match:
                    value = float(match.group(1))
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
            'dataset': dataset,  #  新增 dataset 列
            'traverse_component': data.get('traverse', (0, 1))[0] / data.get('traverse', (0, 1))[1],
            'traverseTimes': data.get('traverseTimes', (0, 1))[0] / data.get('traverseTimes', (0, 1))[1],
            'locate_component': data.get('locate', (0, 1))[0] / data.get('locate', (0, 1))[1],
            'search_component': data.get('search', (0, 1))[0] / data.get('search', (0, 1))[1],
            'NOD': data.get('NOD', (0, 1))[0] / data.get('NOD', (0, 1))[1],
            'DEF': data.get('DEF', (0, 1))[0] / data.get('DEF', (0, 1))[1],
            'OCC': data.get('OCC', (0, 1))[0] / data.get('OCC', (0, 1))[1],
            'LOC': data.get('LOC', (0, 1))[0] / data.get('LOC', (0, 1))[1],
            'gotoDefinition': data.get('gotoDefinition', (0, 1))[0] / data.get('gotoDefinition', (0, 1))[1],
            'rename': data.get('rename', (0, 1))[0] / data.get('rename', (0, 1))[1],
            'completion': data.get('completion', (0, 1))[0] / data.get('completion', (0, 1))[1],
            # 'subcontextNum': data.get('subcontextNum', (0, 1))[0] / data.get('subcontextNum', (0, 1))[1]
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
    fieldnames = ['document', 'traverse_component', 'traverseTimes', 'locate_component',
                  'search_component', 'NOD', 'DEF', 'OCC', 'LOC',
                #   'subcontextNum',
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
    targets = ['locate_component', 'search_component', 'traverse_component',
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


def linear_regression_fit(results, target, train_dataset, x_param,
                          summary_file="linear_regression_results.csv",
                          detail_file="detailed_predictions.csv"):
    """
    用指定数据集 (train_dataset) 训练一元线性回归 (y = kx + b)，
    在其余数据集以及 ALL(全部数据) 上测试预测效果。

    参数:
        results: list[dict]，process_log_file 解析得到的结果
        target: str，要预测的目标列
        train_dataset: str，用作训练集的数据集名称（例如 'LOC'）
        x_param: str，自变量
    """

    df = pd.DataFrame(results).drop_duplicates(subset=["document"])

    # 按 dataset 分组
    datasets = {d: g for d, g in df.groupby("dataset")}

    if train_dataset not in datasets:
        raise ValueError(f"训练集 {train_dataset} 不存在！可选: {list(datasets.keys())}")

    train_df = datasets[train_dataset]
    if target not in train_df.columns or x_param not in train_df.columns:
        raise ValueError(f"训练数据缺少列: {target} 或 {x_param}")

    # 训练回归模型
    x_train = train_df[[x_param]].values
    y_train = train_df[target].values
    model = LinearRegression()
    model.fit(x_train, y_train)
    k = model.coef_[0]
    b = model.intercept_

    # summary/detail 文件表头
    summary_fields = [
        "train_dataset", "x_param", "target", "test_dataset",
        "k", "b", "MSE", "RMAE", "R2", "mean_real", "mean_pred"
    ]
    detail_fields = [
        "train_dataset", "x_param", "target", "test_dataset",
        "document", "real_value", "pred_value"
    ]

    with open(summary_file, "w", newline="", encoding="utf-8") as sf, \
         open(detail_file, "w", newline="", encoding="utf-8") as df_out:
        summary_writer = csv.DictWriter(sf, fieldnames=summary_fields)
        detail_writer = csv.DictWriter(df_out, fieldnames=detail_fields)
        summary_writer.writeheader()
        detail_writer.writeheader()

        # 其余 dataset 测试
        for test_dataset, test_df in datasets.items():
            if test_dataset == train_dataset:
                continue
            if target not in test_df.columns or x_param not in test_df.columns:
                continue

            real_y = test_df[target].values
            x_test = test_df[[x_param]].values
            pred_y = model.predict(x_test)

            mse = mean_squared_error(real_y, pred_y)
            mae = mean_absolute_error(real_y, pred_y)
            rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
            r2 = r2_score(real_y, pred_y)
            mean_real = np.mean(real_y)
            mean_pred = np.mean(pred_y)

            summary_writer.writerow({
                "train_dataset": train_dataset,
                "x_param": x_param,
                "target": target,
                "test_dataset": test_dataset,
                "k": k,
                "b": b,
                "MSE": mse,
                "RMAE": rmae,
                "R2": r2,
                "mean_real": mean_real,
                "mean_pred": mean_pred
            })

            for doc, real, pred in zip(test_df["document"], real_y, pred_y):
                detail_writer.writerow({
                    "train_dataset": train_dataset,
                    "x_param": x_param,
                    "target": target,
                    "test_dataset": test_dataset,
                    "document": doc,
                    "real_value": real,
                    "pred_value": pred
                })

        # ========= ALL: 全部数据一起作为测试集 =========
        real_y = df[target].values
        x_test = df[[x_param]].values
        pred_y = model.predict(x_test)

        mse = mean_squared_error(real_y, pred_y)
        mae = mean_absolute_error(real_y, pred_y)
        rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
        r2 = r2_score(real_y, pred_y)
        mean_real = np.mean(real_y)
        mean_pred = np.mean(pred_y)

        summary_writer.writerow({
            "train_dataset": train_dataset,
            "x_param": x_param,
            "target": target,
            "test_dataset": "ALL",  # 注意: ALL 是整体数据，不是某个 dataset
            "k": k,
            "b": b,
            "MSE": mse,
            "RMAE": rmae,
            "R2": r2,
            "mean_real": mean_real,
            "mean_pred": mean_pred
        })

        for doc, real, pred in zip(df["document"], real_y, pred_y):
            detail_writer.writerow({
                "train_dataset": train_dataset,
                "x_param": x_param,
                "target": target,
                "test_dataset": "ALL",
                "document": doc,
                "real_value": real,
                "pred_value": pred
            })

    print(f"[完成] {target} ~ {x_param} (训练集: {train_dataset}) 的结果已保存到 {summary_file} 和 {detail_file}")
    return k, b, df


def derived_prediction_eval(results, 
                            k_locate, b_locate, 
                            k_traverse, b_traverse, 
                            k_search, b_search,
                            summary_file="derived_results_summary.csv",
                            detail_file="derived_results_detail.csv"):
    """
    基于已有的线性回归结果，计算:
    - locate_component_pred = k_locate * NOD + b_locate
    - traverse_component_pred = k_traverse * NOD + b_traverse
    - search_component_pred = k_search * LOC + b_search

    派生目标:
    - rename_pred = locate_component_pred * 2 + search_component_pred
    - completion_pred = locate_component_pred + traverse_component_pred * traverseTimes
    - gotoDefinition_pred = locate_component_pred
    """

    df = pd.DataFrame(results).drop_duplicates(subset=["document"])
    datasets = {d: g for d, g in df.groupby("dataset")}
    datasets["ALL"] = df  # 整体测试集

    summary_fields = [
        "target", "test_dataset", "MSE", "MAE", "RMAE", "R2", "mean_real", "mean_pred"
    ]
    detail_fields = [
        "target", "test_dataset", "document", "real_value", "pred_value"
    ]

    with open(summary_file, "w", newline="", encoding="utf-8") as sf, \
         open(detail_file, "w", newline="", encoding="utf-8") as df_out:
        summary_writer = csv.DictWriter(sf, fieldnames=summary_fields)
        detail_writer = csv.DictWriter(df_out, fieldnames=detail_fields)
        summary_writer.writeheader()
        detail_writer.writeheader()

        # ========== rename ==========
        for test_dataset, test_df in datasets.items():
            if "rename" not in test_df.columns or "LOC" not in test_df.columns or "NOD" not in test_df.columns:
                continue

            real_y = test_df["rename"].values
            x_nod = test_df[["NOD"]].values
            x_loc = test_df[["LOC"]].values

            locate_pred = k_locate * x_nod.flatten() + b_locate
            search_pred = k_search * x_loc.flatten() + b_search
            pred_y = locate_pred * 2 + search_pred / 1000 + RENAME

            mse = mean_squared_error(real_y, pred_y)
            mae = mean_absolute_error(real_y, pred_y)
            rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
            r2 = r2_score(real_y, pred_y)

            summary_writer.writerow({
                "target": "rename",
                "test_dataset": test_dataset,
                "MSE": mse, "MAE": mae, "RMAE": rmae,
                "R2": r2, "mean_real": np.mean(real_y), "mean_pred": np.mean(pred_y)
            })

            for doc, real, pred in zip(test_df["document"], real_y, pred_y):
                detail_writer.writerow({
                    "target": "rename",
                    "test_dataset": test_dataset,
                    "document": doc,
                    "real_value": real,
                    "pred_value": pred
                })

        # ========== completion ==========
        for test_dataset, test_df in datasets.items():
            if "completion" not in test_df.columns or "NOD" not in test_df.columns or "traverseTimes" not in test_df.columns:
                continue

            real_y = test_df["completion"].values
            x_nod = test_df[["NOD"]].values
            x_times = test_df[["traverseTimes"]].values

            locate_pred = k_locate * x_nod.flatten() + b_locate
            traverse_pred = k_traverse * x_nod.flatten() + b_traverse
            pred_y = locate_pred + traverse_pred * x_times.flatten()

            mse = mean_squared_error(real_y, pred_y)
            mae = mean_absolute_error(real_y, pred_y)
            rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
            r2 = r2_score(real_y, pred_y)

            summary_writer.writerow({
                "target": "completion",
                "test_dataset": test_dataset,
                "MSE": mse, "MAE": mae, "RMAE": rmae,
                "R2": r2, "mean_real": np.mean(real_y), "mean_pred": np.mean(pred_y)
            })

            for doc, real, pred in zip(test_df["document"], real_y, pred_y):
                detail_writer.writerow({
                    "target": "completion",
                    "test_dataset": test_dataset,
                    "document": doc,
                    "real_value": real,
                    "pred_value": pred
                })

        # ========== gotoDefinition ==========
        for test_dataset, test_df in datasets.items():
            if "gotoDefinition" not in test_df.columns or "NOD" not in test_df.columns:
                continue

            real_y = test_df["gotoDefinition"].values
            x_nod = test_df[["NOD"]].values

            locate_pred = k_locate * x_nod.flatten() + b_locate
            pred_y = locate_pred

            mse = mean_squared_error(real_y, pred_y)
            mae = mean_absolute_error(real_y, pred_y)
            rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
            r2 = r2_score(real_y, pred_y)

            summary_writer.writerow({
                "target": "gotoDefinition",
                "test_dataset": test_dataset,
                "MSE": mse, "MAE": mae, "RMAE": rmae,
                "R2": r2, "mean_real": np.mean(real_y), "mean_pred": np.mean(pred_y)
            })

            for doc, real, pred in zip(test_df["document"], real_y, pred_y):
                detail_writer.writerow({
                    "target": "gotoDefinition",
                    "test_dataset": test_dataset,
                    "document": doc,
                    "real_value": real,
                    "pred_value": pred
                })

    print(f"[完成] 派生预测 (rename, completion, gotoDefinition) 的结果已保存到 {summary_file} 和 {detail_file}")




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
    
    # 把 all_results 合并成一个 DataFrame（去重 document，避免重复行）
    all_data = []
    for metric, results in all_results.items():
        all_data.extend(results)
    # df = pd.DataFrame(all_data).drop_duplicates(subset=["document"])
    
    
    k_s, b_s, _ = linear_regression_fit(all_data, target="search_component", train_dataset="LOC", x_param="LOC")
    k_l, b_l, _ = linear_regression_fit(all_data, target="locate_component", train_dataset="NOD", x_param="NOD")
    k_t, b_t, _ = linear_regression_fit(all_data, target="traverse_component", train_dataset="NOD", x_param="NOD")
    derived_prediction_eval(all_data, k_l, b_l, k_t, b_t, k_s, b_s)
    
    # model = train_and_validate_cnum(all_results, k, b)
    # model2 = train_and_validate_cnum_completion(all_results, k, b)
    
    
    # linear_regression_fit(df, target="rename", feature="DEF")
    # linear_regression_fit(df, target="completion", feature="LOC")
    
    
    
