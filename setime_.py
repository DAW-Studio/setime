import curses
from datetime import datetime
import time

today = str(datetime.today().date())

log_lines = ["e"]


header = ["Date", "Task", "Start", "End", "Break", "Time (0h)"]
table_data = [
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["2025-03-29", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
    ["0000-00-00", "Task", "00:00", "00:00", "0m", "0h"],
]
padding = [2, 0, 4, 4, 4, 10]


def calculate_column_widths(stdscr, table_data, padding=[2, 5, 4, 4, 6, 10], expandable_col=1):
    term_width = curses.COLS

    num_columns = len(table_data[0])

   
    col_widths = [max(len(str(item)) for item in col) + padding[i] for i, col in enumerate(zip(*table_data))]

    
    total_non_expandable_width = sum(col_widths[i] for i in range(num_columns) if i != expandable_col)
    remaining_width = term_width - total_non_expandable_width
    col_widths[expandable_col] = remaining_width

    return col_widths


def draw_table(stdscr, focus_row, focus_col, col_widths, active_breaks, break_timer):
    global log_lines
    
    stdscr.clear()
    
    for j, cell in enumerate(header):
        stdscr.attron(curses.color_pair(2))  
        stdscr.addstr(0, sum(col_widths[:j]), cell.ljust(col_widths[j]))  
        stdscr.attroff(curses.color_pair(2))
    
    for i, row in enumerate(table_data):
        active_break = True if i in active_breaks else False
        for j, cell in enumerate(row):
            
            if i == focus_row and j == focus_col:
                stdscr.attron(curses.color_pair(1))  
                if j == 4 and active_break:
                    stdscr.attron(curses.color_pair(6))  
            else:
                stdscr.attroff(curses.color_pair(1))  
                stdscr.attron(curses.color_pair(4))  
                if j == 0 and today in cell:
                    stdscr.attron(curses.color_pair(3))  
                if j == 4 and active_break:
                    stdscr.attron(curses.color_pair(5))  
            
            if j == 4 and active_break:
                cell = str(round((time.time() - break_timer[active_breaks.index(i)])/60, 1))+"m"
                table_data[i][j] = cell

            stdscr.addstr(i + 1, sum(col_widths[:j]), str(cell).ljust(col_widths[j]))  

    
    stdscr.refresh()

def draw_log(stdscr, log_lines):
    
    term_height = curses.LINES

    
    log_start_row = term_height - len(log_lines)

    
    for i, line in enumerate(log_lines):
        stdscr.addstr(log_start_row + i, 0, line[:curses.COLS])  

    stdscr.refresh()

def main(stdscr):
    global log_lines
    output = ""
    for d in dir(stdscr):
        output += d+" " if not d.startswith("__") else ""
    log_lines = output.split(" ")
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  
    curses.init_pair(2, curses.COLOR_WHITE, 68)  
    curses.init_pair(3, curses.COLOR_YELLOW, 235) 
    curses.init_pair(4, 230, 235)
    curses.init_pair(5, 167, 235)
    curses.init_pair(6, 167, curses.COLOR_WHITE)

    focus_row = 0
    focus_col = 0

    col_widths = calculate_column_widths(stdscr, table_data, expandable_col=1)

    active_breaks = []
    break_timer = []

    draw_table(stdscr, focus_row, focus_col, col_widths, active_breaks, break_timer)
    draw_log(stdscr, log_lines)

    while True:
        row = table_data[focus_row]
        cell = row[focus_col]

        key = stdscr.getch()

        if key == curses.KEY_UP and focus_row > 0:
            focus_row -= 1
        elif key == curses.KEY_DOWN and focus_row < len(table_data) - 1:
            focus_row += 1
        elif key == curses.KEY_LEFT and focus_col > 0:
            focus_col -= 1
        elif key == curses.KEY_RIGHT and focus_col < len(table_data[0]) - 1:
            focus_col += 1

        elif key in [10, 13]:
            if focus_col == 4:
                if focus_row in active_breaks:
                    break_timer.pop(active_breaks.index(focus_row))
                    active_breaks.remove(focus_row)
                else:
                    active_breaks.append(focus_row)
                    break_timer.append(time.time()-float(cell[:-1])*60)
            else:

                stdscr.move(focus_row + 1, sum(col_widths[:focus_col]))  
                stdscr.clrtoeol()
                curses.echo()  
                stdscr.refresh()
                new_text = stdscr.getstr().decode("utf-8")  
                curses.noecho()  
                row[focus_col] = new_text  



        elif key == ord('q'):  
            break

        s = [int(n) for n in table_data[focus_row][2].split(":")]
        e = [int(n) for n in table_data[focus_row][3].split(":")]
        h = e[0] - s[0]
        m = h*60 + (e[1] - s[1]) - float(row[4][:-1])
        t = m/60
        table_data[focus_row][-1] = str(t)
        
        draw_table(stdscr, focus_row, focus_col, col_widths, active_breaks, break_timer)
        draw_log(stdscr, log_lines)



if __name__ == "__main__":
    curses.wrapper(main)

