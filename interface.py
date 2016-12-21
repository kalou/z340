#!/usr/bin/python

import string
import curses
import random
import pickle
from collections import namedtuple

codeA = """HER>pl^VPk|1LTG2d
Np+B(#O%DWY.<*Kf)
By:cM+UZGW()L#zHJ
Spp7^l8*V3pO++RK2
_9M+ztjd|5FP+&4k/
p8R^FlO-*dCkF>2D(
#5+Kq%;2UcXGV.zL|
(G2Jfj#O+_NYz+@L9
d<M+b+ZR2FBcyA64K""".replace('\n', '')

middle = """-zlUV+^J+Op7<FBy-"""

codeB = """U+R/5tE|DYBpbTMKO
2<clRJ|*5T4M.+&BF
z69Sy#+N|5FBc(;8R
lGFN^f524b.cV4t++
yBX1*:49CE>VUZ5-+
|c.3zBK(Op^.fMqG2
RcT+L16C<+FlWB|)L
++)WCzWcPOSHT/()p
|FkdW<7tB_YOB*-Cc
>MDHNpkS""".replace('\n', '')

code = codeA + middle + codeB + """zZO8A|K;+""".replace('\n', '')

buf = [{'cipher': x, 'style': 0,
    'repl': '', 'show': 'both'} for x in code]

capitals = [ l for l in string.ascii_letters if l == l.upper() ]

### freq/stat stuff
words = []

def read_dict(f):
    print 'Sampling words from %s' % f
    letters = {}
    with open(f) as dico:
        word = dico.readline().rstrip('\n')
        while word:
            words.append(word)
            for l in word:
                l = l.upper()
                cnt = letters.setdefault(l, 0)
                letters[l] += 1
            word = dico.readline().rstrip('\n')

    tot = sum(v for k,v in letters.items())
    print '%s tot letters' % tot
    for l in letters:
        letters[l] /= float(tot)
    return letters

#freqs = read_dict('english.txt')

freqs = {
'E': 12.49/100,
'T':  9.28/100,
'A':  8.04/100,
'O':  7.64/100,
'I':  7.57/100,
'N':  7.23/100,
'S':  6.51/100,
'R':  6.28/100,
'H':  5.05/100,
'L':  4.07/100,
'D':  3.82/100,
'C':  3.34/100,
'U':  2.73/100,
'M':  2.51/100,
'F':  2.40/100,
'P':  2.14/100,
'G':  1.87/100,
'W':  1.68/100,
'Y':  1.66/100,
'B':  1.48/100,
'V':  1.05/100,
'K':  0.54/100,
'X':  0.23/100,
'J':  0.16/100,
'Q':  0.12/100,
'Z':  0.09/100,
}

cletter = namedtuple('cletter', ['symbol','cnt'])

def symbols(txt):
    """extract weights"""
    cnt = {}
    for l in txt:
        cnt.setdefault(l, 0)
        cnt[l] += 1
    ret = []
    for l in cnt:
        ret.append(cletter(l, cnt[l]))
    return ret

def compose_for(value, li, pom=.20):
    # ret (prop, avail)
    ret = []
    rem = li
    for i in range(13):
        wtot = sum(w.cnt for w in ret)
        if abs(value - wtot) < value*pom:
            break
        c = random.sample(li, 1)[0]
        if wtot + c.cnt < value:
            rem.remove(c)
            ret.append(c)
    return ret, rem

def propose_mapping(txt):
    """map respecting frequencies"""
    avail = symbols(txt)

    cap = capitals[:]
    random.shuffle(cap)

    ret = {}

    for letter in cap:
        exp_cnt = freqs[letter] * len(txt) + 1
        prop, avail = compose_for(exp_cnt, avail)
        if not prop:
            break
        ret[letter] = [x.symbol for x in prop]

    return ret

def score_txt(txt):
    """Chances that a text is real"""
    bigrams = ['th','he','in','er','an','re','on','at','en','nd',
               'ti','es','or','te','of','ed','is','it','al','ar',
               'st','to','nt','ng','se','ha','as','ou','io','le']
    trigrams = ['the','and','ing','ion','tio','ent','ati','for',
                'her','ter','hat','tha','ere','ate','his','con',
                'res','ver','all','ons','nce','men','ith','ted']
    words = ['kill','slave','killing','paradice','cipher','button']

    score = 0
    return sum([1 for n in bigrams if n.upper() in txt] +
        [2 for n in trigrams if n.upper() in txt] +
        [10 for n in words if n.upper() in txt])

def good_proposal(txt):
    def score_mapping(mapping, txt):
        lset = ''.join(''.join(mapping[l]) for l in mapping)
        txt = ''.join(k if k in mapping else ' ' for k in txt)
        for l in mapping:
            for letter in m[l]:
                txt = txt.replace(letter, l)
        return score_txt(txt)

    while True:
        m = propose_mapping(txt)
        score = score_mapping(m, txt)
        if score > 8:
            return m

### XXX // interface stuff
def has_cipher(k):
    return any(x for x in buf if x['cipher'] == k)

def has_repl(k):
    return any(x for x in buf if x['repl'] == k)

def update_buf(show, style, repl=None, char=None):
    """Toggle mode to given style and show-style
    for char X (default all)"""
    def upd(x):
        if char==None or x['cipher'] == char:
            return {'cipher': x['cipher'],
                    'repl': repl if repl is not None else x['repl'],
                    'style': style,
                    'show': show}
        return x

    global buf
    buf = [upd(x) for x in buf]

def set_repl(c, l):
    update_buf('both', 0, l, c)

def show_cipher(win):
    for i in range(20):
        for x in range(17):
            char = buf[i*17+x]
            ls = 0
            dis = ' '
            if char['show'] == 'cipher' or (
                    char['show'] == 'both' and not char['repl']):
                dis = char['cipher']
            else:
                dis = char['repl'] or ' '
                ls = curses.A_BOLD

            win.addch(i, x, dis, ls | char['style'])
    win.refresh()

def say(win, txt):
    win.addstr(0, 0, txt + ' ' * (curses.COLS-1 * len(txt)))
    win.refresh()

def prompt(win, txt):
    say(win, txt)
    win.refresh()
    key = win.getkey()
    win.addstr(0, 0, ' '*len(txt))
    win.refresh()
    return key

def set_display(show='both', style=0, char=None):
    update_buf(show, style, None, char)

def toggle_display():
    dm = ['both', 'repl', 'cipher']
    cur = buf[0]['show']
    nxt = dm[(dm.index(cur)+1) % 3] if (cur in dm) else 'repl'
    set_display(nxt)

def show_letters(win, from_line=0):
    """win is a pad"""
    lmap = {}
    for x in buf:
        lmap.setdefault(x['repl'], [])
        lmap[x['repl']].append(x['cipher'])
    for n,k in enumerate(capitals):
        m = lmap.get(k, [])
        ll = ''.join(set(m))
        ll += (50 - len(ll)) * ' '
        cnt = len(m)
        pct = 100*cnt/float(340)
        exp = round(freqs.get(k, 0) * 340)

        win.addstr(n, 0, '%s[%d/%d]: %s' %
                    (k, cnt, exp, ll))
    win.refresh(from_line, 0, 2, 23, curses.LINES-4, curses.COLS-1)

def save(name):
    with open(name, 'w+') as f:
        f.write(pickle.dumps(buf))

def load(name):
    global buf
    with open(name, 'r') as f:
        buf = pickle.loads(f.read())

def main(stdscr):
    """XXX"""
    # Clear screen
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    cipherwin = curses.newwin(20, 18, 2, 2)
    show_cipher(cipherwin)
    lpad = curses.newpad(70, 50)
    show_letters(lpad)

    while True:
        show_cipher(cipherwin)
        show_letters(lpad)
        key = stdscr.getch()
        if key < 256 and has_cipher(chr(key)):
            new = prompt(stdscr, "map %s to :" % chr(key))
            if new not in string.ascii_letters:
                new = ''
            set_repl(chr(key), new.upper())
        if key == 27:
            break
        if key == 32:
            toggle_display()
        if key == 127:
            update_buf('repl', 0, '', None)
            say(stdscr, 'looking for a mapping')
            m = good_proposal(code)
            say(stdscr, '                     ')
            for l in m:
                for letter in m[l]:
                    set_repl(letter, l)
        if key == 9:
            what = prompt(stdscr, "highlight cipher:")
            set_display('cipher', curses.A_REVERSE, what)
            if not has_cipher(what):
                set_display('both', 0)
        if key == curses.KEY_F10:
            what = prompt(stdscr, 'save as letter:')
            save(what)
        if key == curses.KEY_F9:
            what = prompt(stdscr, 'load letter:')
            load(what)
        if key == curses.KEY_F1:
            say(stdscr, '(f9)load  (f10)save  (tab)higlight (backspace)randomize (space)switch dpy (esc)')

## XXX

curses.wrapper(main)
