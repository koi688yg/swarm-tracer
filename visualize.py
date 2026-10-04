import json
import matplotlib.pyplot as plt
from collections import Counter

try:
    with open("final_insights.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: final_insights.json not found!")
    exit()


distortion_types = [item["analysis"].get("distortion_type", "Unknown") for item in data]
scores = []
for item in data:
    try:
        scores.append(int(item["analysis"].get("absurdity_score", 0)))
    except (ValueError, TypeError):
        scores.append(0)

if not data:
    print("final_insights.json is empty — nothing to plot yet.")
    raise SystemExit(0)

plt.style.use('ggplot')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
fig.suptitle('LLM Multi-Agent Network: Information Distortion Analysis', fontsize=16, fontweight='bold', y=1.05)


type_counts = Counter(distortion_types)
sorted_types = dict(sorted(type_counts.items(), key=lambda item: item[1]))

bars = ax1.barh(list(sorted_types.keys()), list(sorted_types.values()), color='#2c3e50')
ax1.set_title('Distribution of Distortion Types', fontsize=12)
ax1.set_xlabel('Number of Occurrences')
ax1.grid(axis='x', linestyle='--', alpha=0.7)

for bar in bars:
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, 
             f'{int(bar.get_width())}', 
             va='center', ha='left', fontsize=10)

score_counts = Counter(scores)
xs = sorted(score_counts.keys())
ax2.bar(xs, [score_counts[x] for x in xs], color='#e74c3c', edgecolor='white', alpha=0.8)
ax2.set_title('Severity of Mutations (Absurdity Score)', fontsize=12)
ax2.set_xlabel('Absurdity Score (1-10)')
ax2.set_ylabel('Frequency')
ax2.set_xticks(xs)
ax2.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('hackathon_visuals.png', dpi=300, bbox_inches='tight')
print("[Success] High-res visualization saved to 'hackathon_visuals.png'!")