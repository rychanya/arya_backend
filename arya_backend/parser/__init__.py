from openpyxl import load_workbook

def parse_xl(file):
    wb = load_workbook(filename=file, read_only=True)
    for ws in wb.worksheets:
        for row in ws.iter_rows(min_row=2, values_only=True):
            print(row)
            break

parse_xl('/home/rychanya/Загрузки/41l5hd117r162382120814657.xlsx')