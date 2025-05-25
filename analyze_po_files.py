import os
import polib
import json
import csv
from collections import defaultdict

PO_DIR = 'po_files'
DASHBOARD_DIR = 'dashboard'

def analyze_po_files(directory):
    stats = defaultdict(lambda: defaultdict(lambda: {'translated': 0, 'fuzzy': 0, 'untranslated': 0}))
    for filename in os.listdir(directory):
        if filename.endswith('.po'):
            lang_code = filename.split('-')[-1].split('.')[0]
            base_file = filename.replace(f"-{lang_code}.po", "")
            po = polib.pofile(os.path.join(directory, filename))
            for entry in po:
                if 'fuzzy' in entry.flags:
                    stats[lang_code][base_file]['fuzzy'] += 1
                elif entry.translated():
                    stats[lang_code][base_file]['translated'] += 1
                else:
                    stats[lang_code][base_file]['untranslated'] += 1
    return stats

def flatten_stats(nested_stats):
    flat = []
    for lang, files in nested_stats.items():
        for file, counts in files.items():
            total = counts['translated'] + counts['fuzzy'] + counts['untranslated']
            flat.append({
                'language': lang,
                'file': file,
                'translated': counts['translated'],
                'fuzzy': counts['fuzzy'],
                'untranslated': counts['untranslated'],
                'total': total,
                'pct_translated': round(100 * counts['translated'] / total, 1) if total else 0.0,
                'pct_fuzzy': round(100 * counts['fuzzy'] / total, 1) if total else 0.0,
                'pct_untranslated': round(100 * counts['untranslated'] / total, 1) if total else 0.0,
            })
    return flat

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def save_csv(data, path):
    if data:
        keys = data[0].keys()
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

def generate_dashboard_html(json_filename, output_path):
    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Translation Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body style="font-family:sans-serif; margin: 20px;">
  <h1>Translation Coverage by Language</h1>
  <div id="chart"></div>

  <h2>Detailed Table</h2>
  <table id="data-table" border="1" cellpadding="4" style="border-collapse: collapse; margin-top: 1em;"></table>

  <p style="margin-top:1em">
    <a href="stats.json" download>📥 Download JSON</a> |
    <a href="stats.csv" download>📥 Download CSV</a>
  </p>

  <script>
    fetch("{json_filename}")
      .then(response => response.json())
      .then(data => {{
        const langTotals = {{}};
        data.forEach(row => {{
          const lang = row.language;
          if (!langTotals[lang]) langTotals[lang] = {{translated: 0, fuzzy: 0, untranslated: 0}};
          langTotals[lang].translated += row.translated;
          langTotals[lang].fuzzy += row.fuzzy;
          langTotals[lang].untranslated += row.untranslated;
        }});

        const languages = Object.keys(langTotals).sort();
        const translated = languages.map(l => langTotals[l].translated);
        const fuzzy = languages.map(l => langTotals[l].fuzzy);
        const untranslated = languages.map(l => langTotals[l].untranslated);

        const total = languages.map((_, i) => translated[i] + fuzzy[i] + untranslated[i]);

        Plotly.newPlot('chart', [
          {{
            x: languages, y: translated, name: 'Translated', type: 'bar', marker: {{color: 'green'}},
            customdata: total.map((t, i) => (t ? Math.round(100 * translated[i] / t) : 0)),
            hovertemplate: '%{{y}} translated (%{{customdata}}%)'
          }},
          {{
            x: languages, y: fuzzy, name: 'Fuzzy', type: 'bar', marker: {{color: 'orange'}},
            customdata: total.map((t, i) => (t ? Math.round(100 * fuzzy[i] / t) : 0)),
            hovertemplate: '%{{y}} fuzzy (%{{customdata}}%)'
          }},
          {{
            x: languages, y: untranslated, name: 'Untranslated', type: 'bar', marker: {{color: 'red'}},
            customdata: total.map((t, i) => (t ? Math.round(100 * untranslated[i] / t) : 0)),
            hovertemplate: '%{{y}} untranslated (%{{customdata}}%)'
          }}
        ], {{
          barmode: 'stack',
          xaxis: {{title: 'Language'}},
          yaxis: {{title: 'Entries'}},
          hovermode: 'closest'
        }});

        const table = document.getElementById("data-table");
        const headers = Object.keys(data[0]);
        const headRow = document.createElement("tr");
        headers.forEach(h => {{
          const th = document.createElement("th");
          th.textContent = h;
          headRow.appendChild(th);
        }});
        table.appendChild(headRow);

        data.forEach(row => {{
          const tr = document.createElement("tr");
          headers.forEach(h => {{
            const td = document.createElement("td");
            td.textContent = row[h];
            tr.appendChild(td);
          }});
          table.appendChild(tr);
        }});
      }});
  </script>
</body>
</html>
"""
    with open(output_path, 'w') as f:
        f.write(html)

if __name__ == "__main__":
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    raw_stats = analyze_po_files(PO_DIR)
    flat_stats = flatten_stats(raw_stats)
    save_json(flat_stats, os.path.join(DASHBOARD_DIR, "stats.json"))
    save_csv(flat_stats, os.path.join(DASHBOARD_DIR, "stats.csv"))
    generate_dashboard_html("stats.json", os.path.join(DASHBOARD_DIR, "index.html"))
    print("✅ Dashboard built in ./dashboard with index.html + stats.json + stats.csv")
