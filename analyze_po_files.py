import os
import polib
import json
from collections import defaultdict

PO_DIR = 'po_files'
DASHBOARD_DIR = 'dashboard'

def analyze_po_files(directory):
    stats = defaultdict(lambda: {'translated': 0, 'fuzzy': 0, 'untranslated': 0})
    for filename in os.listdir(directory):
        if filename.endswith('.po'):
            lang_code = filename.split('-')[-1].split('.')[0]
            po = polib.pofile(os.path.join(directory, filename))
            for entry in po:
                if 'fuzzy' in entry.flags:
                    stats[lang_code]['fuzzy'] += 1
                elif entry.translated():
                    stats[lang_code]['translated'] += 1
                else:
                    stats[lang_code]['untranslated'] += 1
    return stats

def generate_dashboard_html(stats, output_path):
    languages = sorted(stats.keys())
    translated = [stats[lang]['translated'] for lang in languages]
    fuzzy = [stats[lang]['fuzzy'] for lang in languages]
    untranslated = [stats[lang]['untranslated'] for lang in languages]
    total = [t + f + u for t, f, u in zip(translated, fuzzy, untranslated)]

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
  <script>
    const data = [
      {{
        x: {languages},
        y: {translated},
        name: 'Translated',
        type: 'bar',
        marker: {{color: 'green'}},
        hovertemplate: '%{{y}} translated (%{{customdata}}%)',
        customdata: {[(round(t / tot * 100) if tot else 0) for t, tot in zip(translated, total)]}
      }},
      {{
        x: {languages},
        y: {fuzzy},
        name: 'Fuzzy',
        type: 'bar',
        marker: {{color: 'orange'}},
        hovertemplate: '%{{y}} fuzzy (%{{customdata}}%)',
        customdata: {[(round(f / tot * 100) if tot else 0) for f, tot in zip(fuzzy, total)]}
      }},
      {{
        x: {languages},
        y: {untranslated},
        name: 'Untranslated',
        type: 'bar',
        marker: {{color: 'red'}},
        hovertemplate: '%{{y}} untranslated (%{{customdata}}%)',
        customdata: {[(round(u / tot * 100) if tot else 0) for u, tot in zip(untranslated, total)]}
      }}
    ];

    const layout = {{
      barmode: 'stack',
      xaxis: {{title: 'Language'}},
      yaxis: {{title: 'Number of Entries'}},
      hovermode: 'closest'
    }};

    Plotly.newPlot('chart', data, layout);
  </script>
</body>
</html>
"""
    with open(output_path, 'w') as f:
        f.write(html)

if __name__ == "__main__":
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    stats = analyze_po_files(PO_DIR)
    generate_dashboard_html(stats, os.path.join(DASHBOARD_DIR, 'index.html'))
    print("✅ Interactive dashboard written to dashboard/index.html")
