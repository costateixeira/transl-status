import os
import polib
import json
import csv
import yaml
import argparse
import datetime

from collections import defaultdict

def collect_stats(po_root, label):
    stats = []
    for dirpath, _, files in os.walk(po_root):
        for fname in files:
            if not fname.endswith(".po"):
                continue
            lang = fname.split('-')[-1].split('.')[0]
            file_base = fname.replace(f'-{lang}.po', '')
            path = os.path.join(dirpath, fname)
            po = polib.pofile(path)
            translated = fuzzy = untranslated = 0
            for entry in po:
                if entry.msgid.strip() == "":
                    continue  # skip header
                if 'fuzzy' in entry.flags:
                    fuzzy += 1
                elif entry.translated():
                    translated += 1
                else:
                    untranslated += 1
            total = translated + fuzzy + untranslated
            stats.append({
                "source": label,
                "file": file_base,
                "language": lang,
                "translated": translated,
                "fuzzy": fuzzy,
                "untranslated": untranslated,
                "total": total,
                "pct_translated": round(100 * translated / total, 1) if total else 0,
                "pct_fuzzy": round(100 * fuzzy / total, 1) if total else 0,
                "pct_untranslated": round(100 * untranslated / total, 1) if total else 0,
            })
    return stats

def write_json(data, outpath):
    with open(outpath, 'w') as f:
        json.dump(data, f, indent=2)

def write_csv(data, outpath):
    if not data:
        return
    with open(outpath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build translation stats from YAML config.")
    parser.add_argument('--config', required=True, help='YAML file with sources')
    parser.add_argument('--output', default='translation-status/dashboard', help='Output folder')
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    all_stats = []
    for source in config.get('sources', []):
        folder = source['local']
        label = source['label']
        if not os.path.isdir(folder):
            print(f"⚠️ Warning: folder '{folder}' not found, skipping.")
            continue
        stats = collect_stats(folder, label)
        all_stats.extend(stats)


    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    output_data = {
        "generated_at": timestamp,
        "records": all_stats
    }

    os.makedirs(args.output, exist_ok=True)
    write_json(output_data, os.path.join(args.output, 'stats.json'))  # ✅ FIXED HERE
    write_csv(all_stats, os.path.join(args.output, 'stats.csv'))
    print(f"✅ Wrote {len(all_stats)} records to {args.output}/stats.(json|csv)")

