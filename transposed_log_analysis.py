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
        'completion': re.compile(r'completion: (\d+) document: (.+)$'),
        'subcontextNum': re.compile(r'subcontextNum: (\d+) document: (.+)$')
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
            'completion': data.get('completion', (0, 1))[0] / data.get('completion', (0, 1))[1],
            'subcontextNum': data.get('subcontextNum', (0, 1))[0] / data.get('subcontextNum', (0, 1))[1]
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
                  'search_component', 'NOD', 'DEF', 'OCC', 'LOC','subcontextNum',
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
    features = ['LOC', 'DEF', 'OCC', 'NOD','subcontextNum']
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


def linear_regression_fit(all_results, target, feature, x_param,
                          summary_file="linear_regression_results.csv",
                          detail_file="detailed_predictions.csv"):
    """
    用 souffle_{feature}.log 训练一元线性回归 (y = kx + b)，
    在其他 log 数据以及 ALL (整体数据) 上测试预测效果。

    参数:
        all_results: dict, 不同 metric 的数据
        target: str, 预测目标列
        feature: str, 训练集选用的 metric
        x_param: str, 用于训练/预测的自变量列（替代原来的 feature）
    """

    # 训练集
    train_data = pd.DataFrame(all_results[feature]).drop_duplicates(subset=["document"])
    x_train = train_data[[x_param]].values
    y_train = train_data[target].values

    model = LinearRegression()
    model.fit(x_train, y_train)
    k = model.coef_[0]
    b = model.intercept_

    # summary 文件表头
    summary_fields = [
        "train_feature", "x_param", "target", "test_metric",
        "k", "b", "MSE", "RMAE", "R2", "mean_real", "mean_pred"
    ]
    summary_exists = os.path.isfile(summary_file)

    # detail 文件表头
    detail_fields = [
        "train_feature", "x_param", "target", "test_metric",
        "document", "real_value", "pred_value"
    ]
    detail_exists = os.path.isfile(detail_file)

    # a 追加 ， w 清空后写入
    with open(summary_file, "w", newline="", encoding="utf-8") as sf, \
         open(detail_file, "w", newline="", encoding="utf-8") as df:
        summary_writer = csv.DictWriter(sf, fieldnames=summary_fields)
        detail_writer = csv.DictWriter(df, fieldnames=detail_fields)
        if not summary_exists:
            summary_writer.writeheader()
        if not detail_exists:
            detail_writer.writeheader()

        # 遍历测试集 (单独的 metric)
        for test_metric, test_results in all_results.items():
            if test_metric == feature:  # 跳过训练集
                continue
            test_df = pd.DataFrame(test_results).drop_duplicates(subset=["document"])
            if target not in test_df.columns or x_param not in test_df.columns:
                continue

            real_y = test_df[target].values
            x_test = test_df[[x_param]].values
            pred_y = k * x_test.flatten() + b

            # 计算统计指标
            mse = mean_squared_error(real_y, pred_y)
            mae = mean_absolute_error(real_y, pred_y)
            rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
            r2 = r2_score(real_y, pred_y)
            mean_real = np.mean(real_y)
            mean_pred = np.mean(pred_y)

            # 写入 summary
            summary_writer.writerow({
                "train_feature": feature,
                "x_param": x_param,
                "target": target,
                "test_metric": test_metric,
                "k": k,
                "b": b,
                "MSE": mse,
                "RMAE": rmae,
                "R2": r2,
                "mean_real": mean_real,
                "mean_pred": mean_pred
            })

            # 写入 detail
            for doc, real, pred in zip(test_df["document"], real_y, pred_y):
                detail_writer.writerow({
                    "train_feature": feature,
                    "x_param": x_param,
                    "target": target,
                    "test_metric": test_metric,
                    "document": doc,
                    "real_value": real,
                    "pred_value": pred
                })

        # ========= 新增 ALL 测试集 =========
        all_test_data = []
        for m, res in all_results.items():
            all_test_data.extend(res)

        if all_test_data:
            all_df = pd.DataFrame(all_test_data).drop_duplicates(subset=["document"])
            if target in all_df.columns and x_param in all_df.columns:
                real_y = all_df[target].values
                x_test = all_df[[x_param]].values
                pred_y = k * x_test.flatten() + b

                mse = mean_squared_error(real_y, pred_y)
                mae = mean_absolute_error(real_y, pred_y)
                rmae = mae / np.mean(real_y) if np.mean(real_y) != 0 else np.nan
                r2 = r2_score(real_y, pred_y)
                mean_real = np.mean(real_y)
                mean_pred = np.mean(pred_y)

                summary_writer.writerow({
                    "train_feature": feature,
                    "x_param": x_param,
                    "target": target,
                    "test_metric": "ALL",
                    "k": k,
                    "b": b,
                    "MSE": mse,
                    "RMAE": rmae,
                    "R2": r2,
                    "mean_real": mean_real,
                    "mean_pred": mean_pred
                })

                for doc, real, pred in zip(all_df["document"], real_y, pred_y):
                    detail_writer.writerow({
                        "train_feature": feature,
                        "x_param": x_param,
                        "target": target,
                        "test_metric": "ALL",
                        "document": doc,
                        "real_value": real,
                        "pred_value": pred
                    })

    print(f"[完成] {target} ~ {x_param} (训练集: {feature}) 的结果已保存到 {summary_file} 和 {detail_file}")
    return k, b, all_df



def train_and_validate_cnum(all_results, k, b, 
                            output_file="cnum_results.csv",
                            summary_file="cnum_summary.csv"):
    """
    用 OCC 数据集训练 cnum 模型: cnum = f(DEF, OCC)
    然后在 LOC, NOD, DEF 数据集上验证。
    评估指标: MSE, RMAE, R²
    """
    results = []
    summary = []

    # Step1: 训练集 OCC
    if "OCC" not in all_results:
        raise ValueError("all_results 中必须包含 OCC 数据集！")
    train_df = pd.DataFrame(all_results["OCC"]).copy()

    required_cols = {"OCC", "DEF", "search_component", "rename","subcontextNum"}
    if not required_cols.issubset(train_df.columns):
        raise KeyError(f"训练数据缺少必要列: {required_cols - set(train_df.columns)}")

    # Step2: 用 LOC 拟合的公式预测 search
    train_df["search_pred"] = k * train_df["subcontextNum"] + b

    # Step3: 计算 cnum
    train_df["cnum"] = train_df["rename"] * 10000 / train_df["search_pred"]

    # Step4: 拟合 cnum ~ (DEF, OCC)
    X_train = train_df[["OCC","subcontextNum"]].values
    y_train = train_df["cnum"].values
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import Ridge

    model = make_pipeline(PolynomialFeatures(degree=3), LinearRegression())
    model.fit(X_train, y_train)
    
    # X_train = train_df[["subcontextNum"]].values
    # y_train = train_df["cnum"].values
    # model = LinearRegression()
    # model.fit(X_train, y_train)
    # model.fit(X_train, y_train)

    # === 新增：评估训练集效果 ===
    train_df["cnum_pred"] = model.predict(X_train)
    mse = mean_squared_error(y_train, train_df["cnum_pred"])
    rmae = np.mean(np.abs((y_train - train_df["cnum_pred"]) / y_train))
    r2 = r2_score(y_train, train_df["cnum_pred"])

    summary.append({
        "test_metric": "OCC (Train)",
        "MSE": mse,
        "RMAE": rmae,
        "R2": r2
    })

    # Step5: 在其他数据集验证
    for metric in all_results:
        if metric == "OCC":
            continue
        df = pd.DataFrame(all_results[metric]).copy()
        if not {"OCC", "DEF", "rename","subcontextNum"}.issubset(df.columns):
            continue

        df["search_pred"] = k * df["subcontextNum"] + b
        df["cnum_pred"] = model.predict(df[["OCC","subcontextNum"]].values)
        df["rename_pred"] = df["search_pred"] * df["cnum_pred"] / 10000

        # 保存逐条结果
        for _, row in df.iterrows():
            results.append({
                "test_metric": metric,
                "document": row["document"],
                "rename_true": row["rename"],
                "rename_pred": row["rename_pred"]
            })

        # 计算指标
        y_true = df["rename"].values
        y_pred = df["rename_pred"].values
        mse = mean_squared_error(y_true, y_pred)
        rmae = np.mean(np.abs((y_true - y_pred) / y_true))
        r2 = r2_score(y_true, y_pred)

        summary.append({
            "test_metric": metric,
            "MSE": mse,
            "RMAE": rmae,
            "R2": r2
        })

    # 保存结果
    pd.DataFrame(results).to_csv(output_file, index=False)
    pd.DataFrame(summary).to_csv(summary_file, index=False)

    print(f"[+] CNUM 拟合与验证结果已保存到 {output_file}")
    print(f"[+] 评估指标已保存到 {summary_file}")

    return model




def train_and_validate_cnum_completion(all_results, k, b, 
                            output_file="cnum_results.csv",
                            summary_file="cnum_summary.csv"):
    """
    用 OCC 数据集训练 cnum 模型: cnum = f(DEF, OCC)
    然后在 LOC, NOD, DEF 数据集上验证。
    评估指标: MSE, RMAE, R²
    """
    results = []
    summary = []

    # Step1: 训练集 OCC
    if "OCC" not in all_results:
        raise ValueError("all_results 中必须包含 OCC 数据集！")
    train_df = pd.DataFrame(all_results["OCC"]).copy()

    required_cols = {"OCC", "DEF", "search_component", "rename","subcontextNum"}
    if not required_cols.issubset(train_df.columns):
        raise KeyError(f"训练数据缺少必要列: {required_cols - set(train_df.columns)}")

    # Step2: 用 LOC 拟合的公式预测 search
    train_df["search_pred"] = k * train_df["subcontextNum"] + b

    # Step3: 计算 cnum
    train_df["cnum"] = train_df["completion"] * 10000 / train_df["search_pred"]

    # Step4: 拟合 cnum ~ (DEF, OCC)
    X_train = train_df[["OCC","subcontextNum"]].values
    y_train = train_df["cnum"].values
    from sklearn.preprocessing import StandardScaler, PolynomialFeatures
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import Ridge

    model = make_pipeline(PolynomialFeatures(degree=3), LinearRegression())
    model.fit(X_train, y_train)
    
    # X_train = train_df[["subcontextNum"]].values
    # y_train = train_df["cnum"].values
    # model = LinearRegression()
    # model.fit(X_train, y_train)
    # model.fit(X_train, y_train)

    # === 新增：评估训练集效果 ===
    train_df["cnum_pred"] = model.predict(X_train)
    mse = mean_squared_error(y_train, train_df["cnum_pred"])
    rmae = np.mean(np.abs((y_train - train_df["cnum_pred"]) / y_train))
    r2 = r2_score(y_train, train_df["cnum_pred"])

    summary.append({
        "test_metric": "OCC (Train)",
        "MSE": mse,
        "RMAE": rmae,
        "R2": r2
    })

    # Step5: 在其他数据集验证
    for metric in all_results:
        if metric == "OCC":
            continue
        df = pd.DataFrame(all_results[metric]).copy()
        if not {"OCC", "DEF", "rename","subcontextNum"}.issubset(df.columns):
            continue

        df["search_pred"] = k * df["subcontextNum"] + b
        df["cnum_pred"] = model.predict(df[["OCC","subcontextNum"]].values)
        df["completion_pred"] = df["search_pred"] * df["cnum_pred"] / 10000

        # 保存逐条结果
        for _, row in df.iterrows():
            results.append({
                "test_metric": metric,
                "document": row["document"],
                "completion_true": row["completion"],
                "completion_pred": row["completion_pred"]
            })

        # 计算指标
        y_true = df["completion"].values
        y_pred = df["completion_pred"].values
        mse = mean_squared_error(y_true, y_pred)
        rmae = np.mean(np.abs((y_true - y_pred) / y_true))
        r2 = r2_score(y_true, y_pred)

        summary.append({
            "test_metric": metric,
            "MSE": mse,
            "RMAE": rmae,
            "R2": r2
        })

    # 保存结果
    pd.DataFrame(results).to_csv(output_file, index=False)
    pd.DataFrame(summary).to_csv(summary_file, index=False)

    print(f"[+] CNUM 拟合与验证结果已保存到 {output_file}")
    print(f"[+] 评估指标已保存到 {summary_file}")

    return model


if __name__ == "__main__":
    root = "gen_datasets"
    metrics = ["LOC", "NOD", "OCC", "DEF"]
    all_results = {}

    for metric in metrics:
        metric_folder = os.path.join(root, metric)
        merged_log = os.path.join(root, f"souffle_{metric}.log")
        # merge_logs(metric_folder, merged_log)
        results = process_log_file(merged_log)
        all_results[metric] = results
        # print(f"[{metric}] 合并完成，生成 {merged_log}")

    # export_multi_to_csv(all_results, "results_all.csv")
    # analyze_feature_importance(all_results, "feature_importance.csv")
    
    # 把 all_results 合并成一个 DataFrame（去重 document，避免重复行）
    all_data = []
    for metric, results in all_results.items():
        all_data.extend(results)
    df = pd.DataFrame(all_data).drop_duplicates(subset=["document"])
    
    
    k,b,all_df = linear_regression_fit(all_results, target="search_component", feature="OCC",x_param="subcontextNum")
    model = train_and_validate_cnum(all_results, k, b)
    # model2 = train_and_validate_cnum_completion(all_results, k, b)
    
    
    # linear_regression_fit(df, target="rename", feature="DEF")
    # linear_regression_fit(df, target="completion", feature="LOC")
    
    
    
