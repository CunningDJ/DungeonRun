import re
import sys

path1 = sys.path

sys.path
for item in path1:
    print(item)
    if re.search('sdl', item):
        print('Found: {}'.format(item))



class IntroMenu():
    def __init__(self):
        master = tk.Tk()
        master.resizable(width=False, height=False)
        master.wm_title('Welcome to Dungeon Run.')

        window_frame = tk.Frame(master)
        win_height = 80
        win_width = 80
        window_frame.pack(fill=tkc.BOTH, height=win_height, width= win_width, bg='black')

        master.mainloop()