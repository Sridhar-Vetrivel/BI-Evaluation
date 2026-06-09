import openpyxl, sys
sys.stdout.reconfigure(encoding='utf-8')

FILEPATH = r'c:\Users\sridhar.vetrivel\OneDrive - psiog.com\Accounts\GTF\TableAU Analysis\Goal\Discovery.xlsx'
wb = openpyxl.load_workbook(FILEPATH)
ws = wb['Evaluation Matrix - 1']

# A=1 S.No | B=2 Category | C=3 Breakdown Item | D=4 Priority | E=5 Discovery Reasoning
# F=6 PowerBI | G=7 Tableau | H=8 PBI Proof | I=9 TAB Proof | J=10 Findings/Conclusion | K=11 Status

print(f"{'Row':<5} {'S.No':<6} {'Breakdown Item':<55} {'J (Findings) - first 60 chars':<65} {'K (Status)'}")
print("-" * 200)

for row in ws.iter_rows(min_row=2):
    cat = row[1].value  # B
    if cat and '2.' in str(cat) and 'Visualization' in str(cat):
        sno   = row[0].value   # A
        item  = str(row[2].value or '')[:54]  # C
        pbi   = str(row[5].value or '')[:60]  # F
        tab   = str(row[6].value or '')[:60]  # G
        j_val = str(row[9].value or '')[:60]  # J
        k_val = row[10].value                 # K
        rnum  = row[0].row
        print(f"{rnum:<5} {str(sno):<6} {item:<55} J={j_val:<65} K={k_val}")
        print(f"       F(PBI): {pbi}")
        print(f"       G(TAB): {tab}")
        print()
