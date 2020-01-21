
import sys
from time import sleep

import pyautogui
import pyscreenshot as IG
import pytesseract
import requests

pyautogui.PAUSE = 0.05

L = 1355
U = 345
R = 1645
D = 635
wi = (R - L) / 4
hi = (D - U) / 4

class Node():
    def __init__(self):
        self.ch = [None for i in range(26)]
        self.end = False

    def Walk(self, s):
        if len(s) == 1:
            return self.ch[ord(s[0]) - ord('a')]
        else:
            if self.ch[ord(s[0]) - ord('a')] is None:
                return None
            return self.ch[ord(s[0]) - ord('a')].Walk(s[1])

def Normalize(word):
    s = ""
    for c in word:
        if c.isupper():
            s += chr(ord(c) - ord('A') + ord('a'))
        elif c.islower():
            s += c
        else:
            return None
    return s

def Build(now, word, idx):
    if idx >= len(word):
        now.end = True
        return
    
    z = ord(word[idx]) - ord('a')
    if not 0 <= z < 26:
        return
    if now.ch[z] is None:
        now.ch[z] = Node()
    Build(now.ch[z], word, idx + 1)

def GetDict():
    r = requests.get('https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt').text 
    print(r.split('\r\n'))
    return r.split('\r\n')

def GetPicGrid():
    return [[IG.grab(bbox=(int(L+j*wi+7), int(U+i*hi+21), 
                           int(L+(j+1)*wi-7), int(U+(i+1)*hi-21))) 
                for j in range(0, 4)] 
            for i in range(0, 4)]

def GetPos(pos):
    return (int(L+(pos[1]+0.5)*wi), int(U+(pos[0]+0.5)*hi))

def Walk(path):
    if len(path) == 0:
        return
    pos = GetPos(path[0])
    pyautogui.moveTo(pos[0], pos[1])
    pyautogui.mouseDown()
    for p in path[1:]:
        pos = GetPos(p)
        pyautogui.moveTo(pos[0], pos[1])

    pyautogui.mouseUp()

def Dfs(pos, cur, path, word):
    print(pos, cur, path, word)
    if cur is None:
        return
    if cur.end:
        if len(word) >= 3:
            print(path, word)
            Walk(path)

    for dx, dy in [[0, 1], [1, 0], [0, -1], [-1, 0]]:
        nx = pos[0] + dx
        ny = pos[1] + dy
        ob = (nx, ny)
        if 0 <= nx < 4 and 0 <= ny < 4 and ob not in path:
            path.append(ob)
            Dfs(ob, cur.Walk(letters[nx][ny]), path, word + letters[nx][ny])
            path.pop()

for i in range(4):
    for j in range(4):
        Dfs((i, j), root, [], "")

root = Node()
for word in GetDict():
    word = Normalize(word)
    if word is not None:
        Build(root, word, 0)

print('Finish building trie')


# img = IG.grab(bbox=(1355,345,1645,635))
# img.show()
# 
# sys.exit(0)

imgs = GetPicGrid()
letters = [["" for i in range(4)] for j in range(4)]
for i in range(4):
    for j in range(4):
        wo = \
            pytesseract.image_to_string(imgs[i][j], config="-c tessedit"
            "_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            " --psm 10")
        for c in wo:
            letters[i][j] += chr(ord(c) - ord('A') + ord('a'))


print(letters)
