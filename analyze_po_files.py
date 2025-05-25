import os
import polib
import matplotlib.pyplot as plt
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

def generate_dashboard_image(stats, output_path):
    languages = sorted(stats.keys())
    translated = [stats[lang]['translated'] for lang in languages]
    fuzzy = [stats[lang]['fuzzy'] for lang in languages]
    untranslated = [stats[lang]['untranslated'] for lang in languages]
    indices = range(len(languages))

    plt.figure(figsize=(12, 6))
    plt.bar(indices, translated, label='Translated', color='green')
    plt.bar(indices, fuzzy, bottom=translated, label='Fuzzy', color='yellow')
    plt.bar(indices, untranslated, bottom=[t+f for t, f in zip(translated, fuzzy)], label='Untranslated', color='red')
    plt.xticks(indices, languages)
    plt.xlabel('Language')
    plt.ylabel('Entries')
    plt.title('Translation Status by Language')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def generate_dashboard_html(image_filename, output_path):
    html = f"""<!DOCTYPE html>
<html>
<head><title>Translation Dashboard</title></head>
<body style="text-align: center;">
<h1>Translation Coverage</h1>
<img src="{image_filename}" alt="Dashboard">
</body>
</html>
"""
    with open(output_path, 'w') as f:
        f.write(html)

if __name__ == "__main__":
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    stats = analyze_po_files(PO_DIR)
    generate_dashboard_image(stats, os.path.join(DASHBOARD_DIR, 'index.png'))
    generate_dashboard_html('index.png', os.path.join(DASHBOARD_DIR, 'index.html'))
