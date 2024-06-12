from tkinter import *
from tkinter import filedialog
import re
import threading
from os import _exit


def cleanstring2(string):
        string = (string.replace("'", "").replace("`", "").replace('"', '').replace('(','').replace(')','').replace('\n','').replace('\r', '')).strip() 
        return string


def find_tables_and_columns(sql_file):
    
    sql_keywords = {
        "PRIMARY", "KEY", "FOREIGN", "REFERENCES", "UNIQUE", "CONSTRAINT", "CHECK",
        "DEFAULT", "NOT", "NULL", "AUTO_INCREMENT", "ENGINE", "CHARSET", "COLLATE",
        "COMMENT", "IF", "NOT", "EXISTS"
    }
    sql_keywords_set = set(sql_keywords)
    table_definitions = {}

    with open(sql_file, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    print("SQL FILE CONTENT READ!")

    create_table_pattern = re.compile(r"CREATE(?: TEMPORARY)? TABLE(?: IF NOT EXISTS)? [`']?(\w+)[`']?\s*\(\s*(.*?)\s*;", re.IGNORECASE | re.DOTALL)
    create_table_matches = create_table_pattern.findall(sql_content)
    print("create_table_matches:", create_table_matches)

    insert_pattern = re.compile(r"INSERT INTO [`']?(\w+)[`']?\s*\((.*?)\)\s*VALUES\s*\((.*?)\);", re.IGNORECASE | re.DOTALL)

    for table_name, columns_block in create_table_matches:
        column_definitions = {}
        column_lines = [line.strip() for line in columns_block.split(',')]
        print("table:", table_name)

        insert_matches = insert_pattern.findall(sql_content)
        insert_cols = []
        insert_items = []

        for match in insert_matches:
            if match[0] == table_name:
                insert_cols = [col.strip() for col in match[1].split(',')]
                insert_items = [item.strip() for item in match[2].split(',')]
                break
        
        print(column_lines)
        for column_line in column_lines:
            column_name = cleanstring2(column_line.split()[0])

            if column_name.upper() in sql_keywords_set:
                if any(previous in column_line for previous in column_definitions.keys()):
                    continue

            print("column_name:", column_name)
            print("insert_cols:", insert_cols)
            column_datas = []

            if column_name in insert_cols:
                print("column_name here!")
                insert_colindex = insert_cols.index(column_name)
                print("inscol:", insert_colindex)
                for i in range(insert_colindex, len(insert_items), len(insert_cols)):
                    item = cleanstring2(insert_items[i])
                    column_datas.append(item)

            column_definitions[column_name] = column_datas

        table_definitions[table_name] = column_definitions

    print(table_definitions)
    return table_definitions



def clear_listbox(lb):
    try:
        lb.delete(0, END)
    except Exception as e:
        print("Exception in deleting listbox items: ",e)


tc = {}
def select_file():
    filetypes = [("SQL files", "*.sql")]
    fpath = filedialog.askopenfilename(title="Select SQL File", filetypes=filetypes)
    if len(fpath) == 0:
        return
    pathlabel.config(text="Loading...")
    def functhread():
        global tc
        tables_data = (find_tables_and_columns(fpath))
        tc = tables_data
        for table in tables_data.keys():
            tables_lb.insert(END, table)
        pathlabel.config(text=fpath) 
        num_tables = len(tables_data)
        num_columns = sum(len(cols) for cols in tables_data.values())
        tlabel.config(text=f"Tables: {num_tables}")
        clabel.config(text=f"|Columns: {num_columns}")
    clear_listbox(tables_lb)
    clear_listbox(columns_lb)
    threading.Thread(target=functhread).start()


def on_table_select(event):
    selection = event.widget.curselection()
    if selection:
        actual_table_index.set(selection[0])
        selected_item = event.widget.get(selection[0])
        needed_columns = tc[selected_item]
        clear_listbox(columns_lb)
        clear_listbox(datas_lb)
        for column in needed_columns:
            columns_lb.insert(END, column)
        columns_lb.update()


def on_column_select(event):
    selection = event.widget.curselection()
    if selection:
        selected_col = event.widget.get(selection[0])
        current_table = tables_lb.get(actual_table_index.get())
        needed_datas = tc[current_table][selected_col]
        clear_listbox(datas_lb)
        for data in needed_datas:
            datas_lb.insert(END, data)
        datas_lb.update()



#GUI
bgcolor = "#2A323B"
fontcolor = "#C0CBE1"

root = Tk()
actual_table_index = IntVar(None)
root.title("SQL Reader")
width = int(root.winfo_screenwidth()/2)
height = int(root.winfo_screenheight()/2)
x = int((root.winfo_screenwidth() - width)/2)
y = int((root.winfo_screenheight() - height)/2) 
root.geometry(f"{width}x{height}+{x}+{y}")
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=20)
root.rowconfigure(3, weight=1)
root.columnconfigure(0, weight=1)
root.state('zoomed')
root.configure(background=bgcolor)

firstline = Frame(root, bg=bgcolor)
firstline.grid(row=0, column=0, sticky="wesn")
firstline.rowconfigure(0, weight=1)
firstline.columnconfigure(0, weight=1)
firstline.columnconfigure(1, weight=15)
firstline.columnconfigure(2, weight=1)
firstline.columnconfigure(3, weight=1)
sqllabel = Label(firstline, text="SQL-File:", fg=fontcolor, bg=bgcolor)
sqllabel.grid(row=0, column=0)
pathlabel = Label(firstline, bg=bgcolor, fg=fontcolor, borderwidth=2, relief="groove")
pathlabel.grid(row=0, column=1, sticky="we")
selectbutton = Button(firstline, text="...", bg=bgcolor, fg=fontcolor, borderwidth=0, command=select_file)
selectbutton.grid(row=0, column=2)
rip_button = Button(firstline, text="Rip", bg="purple", fg="white", width=10, borderwidth=0)
rip_button.grid(row=0, column=3)

secondline = Frame(root, bg=bgcolor)
secondline.grid(row=1, column=0, sticky="wesn")
secondline.rowconfigure(0, weight=1)
secondline.columnconfigure(0, weight=1)
secondline.columnconfigure(1, weight=35)
keepsql = BooleanVar(False)
cb = Checkbutton(secondline, bg=bgcolor, variable=keepsql)
cb.grid(row=0, column=0, sticky="w")
label1 = Label(secondline, text="Keep SQL-File in Memory", bg=bgcolor, fg=fontcolor)
label1.grid(row=0, column=0)
blank = Label(secondline, borderwidth=1, relief="groove", bg=bgcolor)
blank.grid(row=0, column=1, sticky="we")


thirdline = Frame(root, bg="red")
thirdline.grid(row=2, column=0, sticky="nsew")
thirdline.rowconfigure(0, weight=1)
thirdline.columnconfigure(0, weight=12)
thirdline.columnconfigure(1, weight=5)
thirdline.columnconfigure(2, weight=60)
tables_lb = Listbox(thirdline, bg=bgcolor, fg=fontcolor, borderwidth=2, relief="groove")
tables_lb.grid(row=0, column=0, sticky="nsew")
tables_lb.bind('<<ListboxSelect>>', on_table_select)
columns_lb = Listbox(thirdline, bg=bgcolor, fg=fontcolor, borderwidth=2, relief="groove")
columns_lb.grid(row=0, column=1, sticky="nsew")
columns_lb.bind('<<ListboxSelect>>', on_column_select)
datas_lb = Listbox(thirdline, bg=bgcolor, borderwidth=2, relief="groove", fg=fontcolor)
datas_lb.grid(row=0, column=2, sticky="nsew")


fline = Frame(root, bg=bgcolor)
fline.grid(row=3, column=0, sticky="nsew")
fline.rowconfigure(0, weight=1)
fline.columnconfigure(0, weight=5)
fline.columnconfigure(1, weight=7)
fline.columnconfigure(2, weight=5)
fline.columnconfigure(3, weight=60)
tlabel = Label(fline, text="Tables: n/a", bg=bgcolor, fg=fontcolor)
tlabel.grid(row=0, column=0)
clabel = Label(fline, text="|Columns: n/a", bg=bgcolor, fg=fontcolor)
clabel.grid(row=0, column=1)
dlabel = Label(fline, text="|Datas: n/a", bg=bgcolor, fg=fontcolor)
dlabel.grid(row=0, column=2)
drt = Label(fline, text="|data ripped in n/a", bg=bgcolor, fg=fontcolor)
drt.grid(row=0, column=3, sticky="w")



root.mainloop()
if keepsql.get():
    print("checked")
_exit(1)