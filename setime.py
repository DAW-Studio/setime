import curses
import curse


class SEtime(curse.Window):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        curses.noecho()

    def update(self):
        key = self.stdscr.getch()
        curse.text(self.stdscr, self.width()//2, self.height()//2, f"{key}", curse.Color((0,0,0),(255,255,255)), alignX="center")


if __name__ == "__main__":
    setime = curse.init(SEtime)
