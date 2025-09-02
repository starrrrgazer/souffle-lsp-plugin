import re
import random
from collections import defaultdict
import os
import csv

tolerances = {
    "LOC": 50,
    "NOD": 1250,
    "OCC": 100,
    "DEF": 12
}

def process_log_file(log_file_path):
    document_data = defaultdict(dict)
    patterns = {
        'compile': re.compile(r'compile component: (\d+) document: (.+)$'),
        'locate': re.compile(r'locate component: (\d+) document: (.+)$'),
        'search': re.compile(r'traverse component: (\d+) document: (.+)$'),
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
        results.append({
            'document': doc,
            'LOC': data.get('LOC', (0, 1))[0] / data.get('LOC', (0, 1))[1],
            'NOD': data.get('NOD', (0, 1))[0] / data.get('NOD', (0, 1))[1],
            'OCC': data.get('OCC', (0, 1))[0] / data.get('OCC', (0, 1))[1],
            'DEF': data.get('DEF', (0, 1))[0] / data.get('DEF', (0, 1))[1],
        })
    return results


def generate_combined_files(documents, output_folder, metric, target_values):
    os.makedirs(output_folder, exist_ok=True)
    summary = []

    for target in target_values:
        combined_docs = []
        total_value = 0

        while total_value < target - tolerances[metric]:
            doc = random.choice(documents)
            val = doc[metric]
            if val <= 0:
                continue
            if total_value + val > target + 50:
                continue
            combined_docs.append(doc)
            total_value += val

        output_path = os.path.join(output_folder, f"{metric}_combined_{target}.dl")
        with open(output_path, "w", encoding="utf-8") as out:
            for d in combined_docs:
                if os.path.exists(d['document']):
                    out.write(f"// ==== BEGIN: {d['document']} ====\n")
                    with open(d['document'], "r", encoding="utf-8") as f:
                        out.write(f.read())
                    out.write(f"\n// ==== END: {d['document']} ====\n\n")

        total_LOC = sum(d["LOC"] for d in combined_docs)
        total_NOD = sum(d["NOD"] for d in combined_docs)
        total_OCC = sum(d["OCC"] for d in combined_docs)
        total_DEF = sum(d["DEF"] for d in combined_docs)

        summary.append({
            "file": os.path.basename(output_path),
            "metric": metric,
            "target": target,
            "LOC": total_LOC,
            "NOD": total_NOD,
            "OCC": total_OCC,
            "DEF": total_DEF,
        })

        print(f"[{metric}] Generated {output_path} with {metric} ~ {total_value}")

    return summary


def save_summary_to_csv(summary, output_csv):
    headers = ["file", "metric", "target", "LOC", "NOD", "OCC", "DEF"]

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in summary:
            writer.writerow(row)

    print(f"Summary saved to {output_csv}")


if __name__ == "__main__":
    log_file_path = "./example/souffle.log"
    output_root = "gen_datasets"
    csv_output = "gen_datasets.csv"

    documents = process_log_file(log_file_path)

    target_ranges = {
        "LOC": list(range(400, 10001, 400)),
        "NOD": list(range(10000, 250001, 10000)),
        "OCC": list(range(800, 20001, 800)),
        "DEF": list(range(100, 2501, 100)),
    }
    

    all_summary = []
    for metric, targets in target_ranges.items():
        output_folder = os.path.join(output_root, metric)
        summary = generate_combined_files(documents, output_folder, metric, targets)
        all_summary.extend(summary)

    save_summary_to_csv(all_summary, csv_output)
