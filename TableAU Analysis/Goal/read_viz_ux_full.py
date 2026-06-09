import openpyxl, sys
sys.stdout.reconfigure(encoding='utf-8')

FILEPATH = r'c:\Users\sridhar.vetrivel\OneDrive - psiog.com\Accounts\GTF\TableAU Analysis\Goal\Discovery.xlsx'
wb = openpyxl.load_workbook(FILEPATH)
ws = wb['Evaluation Matrix - 1']

EMPTY_J_ROWS = [12, 13, 14, 18, 19, 20, 21]  # S.No 11,12,13,17,18,19,20

for rnum in EMPTY_J_ROWS:
    row = ws[rnum]
    sno   = row[0].value
    item  = row[2].value
    pri   = row[3].value
    pbi   = row[5].value or ''
    tab   = row[6].value or ''
    j_val = row[9].value or ''
    k_val = row[10].value or ''
    print(f"=== Row {rnum} | S.No {sno} | {item} | Priority: {pri} ===")
    print(f"F (PowerBI): {pbi}")
    print(f"G (Tableau): {tab}")
    print(f"J (current): {j_val}")
    print(f"K (Status) : {k_val}")
    print()
