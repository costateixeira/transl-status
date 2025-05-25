import os
import polib
import matplotlib.pyplot as plt
from collections import defaultdict

# Directory containing the .po files
PO_FILES_DIR = 'po_files'  # Adjust this path if necessary

def analyze_po_files(directory):
    stats = defaultdict(lambda: {'translated': 0, 'fuzzy': 0, 'untranslated': 0})
    
    for filename in os.listdir(directory):
        if filename.endswith('.po'):
            # Extract language code from filename (e.g., 'validator-messages-es.po' -> 'es')
            parts = filename.split('-')
            lang_code = parts[-1].split('.')[0]
            
            po_path = os.path.join(directory, filename)
            po = polib.pofile(po_path)
            
            for entry in po:
                if 'fuzzy' in entry.flags:
                    stats[lang_code]['fuzzy'] += 1
                elif entry.translated():
                    stats[lang_code]['translated'] += 1
                else:
                    stats[lang_code]['untranslated'] += 1
    return stats

def generate_dashboard(stats, output_path):
    languages = sorted(stats.keys())
    translated = [stats[lang]['translated'] for lang in languages]
    fuzzy = [stats[lang]['fuzzy'] for lang in languages]
    untranslated = [stats[lang]['untranslated'] for lang in languages]
    
    bar_width = 0.5
    indices = range(len(languages))
    
    plt.figure(figsize=(12, 8))
    
    # Plot stacked bars
    plt.bar(indices, translated, bar_width, label='Translated', color='green')
    plt.bar(indices, fuzzy, bar_width, bottom=translated, label='Fuzzy', color='yellow')
    bottom_untranslated = [t + f for t, f in zip(translated, fuzzy)]
    plt.bar(indices, untranslated, bar_width, bottom=bottom_untranslated, label='Untranslated', color='red')
    
    plt.xlabel('Language')
    plt.ylabel('Number of Entries')
    plt.title('Translation Status per Language')
    plt.xticks(indices, languages)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

if __name__ == '__main__':
    stats = analyze_po_files(PO_FILES_DIR)
    os.makedirs('dashboard', exist_ok=True)
    generate_dashboard(stats, 'dashboard/index.png')
