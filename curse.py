import curses
import re
from sys import stderr


COLORS = []
class Color:
    def __init__(self, text:tuple|str, background:tuple|str):
        self.text = text
        self.background = background

        if isinstance(text, str):
            _hex = text.lstrip("#")
            text = tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))
        if isinstance(background, str):
            _hex = background.lstrip("#")
            background = tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))

        tr, tg, tb = self.scale(text[0]), self.scale(text[1]), self.scale(text[2])
        br, bg, bb = self.scale(background[0]), self.scale(background[1]), self.scale(background[2])
        text_index = 16 + (tr * 36) + (tg * 6) + tb
        background_index = 16 + (br * 36) + (bg * 6) + bb

        print(len(COLORS))
        item = str(text_index).zfill(3) + str(background_index).zfill(3)
        if item in COLORS:
            self.pair = COLORS.index(item)+1
        else:
            self.pair = len(COLORS)+1
            curses.init_pair(self.pair, text_index, background_index)
            COLORS.append(item)
        self.color_pair = curses.color_pair(self.pair)
        
    def scale(self, value): 
        return round(value / 255 * 5)


def style(text):
    pattern = r"<style\s+([^>]+)>(.*?)</style>|([^<]+)"

    def parse_attributes(style_string):
        attributes = {}
        style_parts = style_string.split(";")
        for part in style_parts:
            part = part.strip()
            if part:
                if "color" in part:
                    rgb_match = re.match(r"color=\(\((\d+),(\d+),(\d+)\),\s*\((\d+),(\d+),(\d+)\)\)", part)
                    if rgb_match:
                        r1, g1, b1, r2, g2, b2 = map(int, rgb_match.groups())
                        attributes['color'] = ((r1, g1, b1), (r2, g2, b2))
                elif "bold" in part and "true" in part:
                    attributes['bold'] = True
        return attributes

    output = []
    x = 0
    for match in re.finditer(pattern, text):
        style_string, styled_text, plain_text = match.groups()
        if styled_text:
            attributes = parse_attributes(style_string)
            attributes['text'] = styled_text
        else:
            attributes = {
                "color": None,
                "bold": None,
                "text": plain_text
            }
        attributes['x'] = x
        x += len(attributes["text"])
        output.append(attributes)

    return "".join([a["text"] for a in output]), output


def text(stdscr:curses.window, x:int, y:int, text:str, color:Color|int=1, alignX="left", alignY="top"):
    if isinstance(color, int):
        color_pair = curses.color_pair(color)
    elif isinstance(color, Color):
        color_pair = color.color_pair
        
    lines = text.splitlines()
    if alignY == "center":
        y -= len(lines)//2
    elif alignY == "bottom":
        y -= len(lines)
    for i, line in enumerate(lines):
        col = x
        string, sections = style(line)
        if alignX == "center":
            col -= len(string)//2
        elif alignX == "right":
            col -= len(string)
        for attr in sections:
            c = color_pair if attr["color"] == None else Color(*attr["color"]).color_pair
            stdscr.attron(c)
            stdscr.addstr(y+i, col+attr["x"], attr["text"])
            stdscr.attroff(c)


class Window:
    def __init__(self, stdscr:curses.window):
        self.stdscr = stdscr
        self.running = True
        subclasses = [sub.__name__ for sub in Window.__subclasses__()]
        self.class_name = "Window" if subclasses == [] else subclasses[0]
        self.init_screen()

    def init_screen(self):
        curses.curs_set(0)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.default_color = Color((255,255,255),(0,0,0))

    def update(self):
        docs(self)

    def run(self):
        while self.running:
            self.stdscr.clear()
            self.update()
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == ord("q"):
                self.running = False

    def width(self): return self.stdscr.getmaxyx()[1]
    def height(self): return self.stdscr.getmaxyx()[0]
    def size(self): return self.stdscr.getmaxyx()[-1:]


def wrapper(_stdscr):
    global stdscr
    stdscr = _stdscr

def init(window):
    curses.wrapper(wrapper)
    w = window(stdscr)
    w.run()
    return w


def docs(window:Window):
    stdscr = window.stdscr

    text(stdscr, window.width()//2, 1, "Welcome to curse!", alignX="center")

    text(stdscr, window.width()//2, 3, f"Override <style color=((255,0,0),(0,0,0))>{window.class_name}.update()</style> to get started.", alignX="center")

    text(stdscr, 0, 6, f"""
import curses
import curse


class {window.class_name}(curse.Window):
    def __init__(self):
        pass

    def update(self):
        key = self.stdscr.getch()
        curse.text(self.stdscr, self.width()//2, self.height()//2, f\"{{key}}\", curse.Color((0,0,0),(255,255,255)), alignX=\"center\")



if __name__ == "__main__":
    curse.init({window.class_name})
    """)
