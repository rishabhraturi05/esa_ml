import json

with open('Transmission_Line_Fault_Classification.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

for idx in [11, 12, 13, 14, 15]:
    cell = nb['cells'][idx]
    print(f"\n================ CELL {idx} ({cell['cell_type']}) ================")
    print("".join(cell['source']))
