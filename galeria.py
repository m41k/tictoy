import curses
import os
import subprocess

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(0)
    stdscr.keypad(1)

    arquivos = sorted([f for f in os.listdir('.') if f.startswith("cover.gif")])
    index = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        list_width = 30
        preview_width = width - list_width - 2

        # Desenha lista
        stdscr.addstr(0, 0, "↑ ↓ navegar | q sair")
        for i, nome in enumerate(arquivos):
            if i == index:
                stdscr.addstr(i + 2, 0, f"> {nome}", curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 0, f"  {nome}")

        # Preview com chafa
        try:
            result = subprocess.run(
		["chafa", "--colors=none", "--symbols=block", arquivos[index], "-s", f"{preview_width}x{height-2}"],
                capture_output=True,
                text=True
            )
            preview_lines = result.stdout.splitlines()
            for i, line in enumerate(preview_lines):
                if i < height - 2:
                    stdscr.addstr(i + 2, list_width + 2, line[:preview_width])
        except:
            pass

        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == curses.KEY_UP:
            index = (index - 1) % len(arquivos)
        elif key == curses.KEY_DOWN:
            index = (index + 1) % len(arquivos)

curses.wrapper(main)
