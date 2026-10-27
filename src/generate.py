"""Automatismes quotidiens 3e / Première spécialité + visuels style fiches pastel.

Pas d'API d'IA, de QR code ni de signes décoratifs à trois traits.
La dernière diapositive renvoie explicitement vers les fiches via le lien du profil.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from datetime import date, datetime
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs' / 'posts'
CONFIG = ROOT / 'config.json'
SIZE = 1080
NAVY = '#15263F'
PINK = '#DE245D'
BLUE = '#287FDE'
SOFTBLUE = '#DFF1FF'
SOFTPINK = '#FFE4EF'
CREAM = '#FFF2D2'
DARK = '#182433'
WHITE = '#FFFFFF'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
FONT_SERIF = 'DejaVuSerifCondensed.ttf'
FONT_BOLD = 'DejaVuSans-Bold.ttf'
FONT_REG = 'DejaVuSans.ttf'
FONT_ITALIC = 'DejaVuSerif-BoldItalic.ttf'


def fmt_fraction(x: Fraction | int) -> str:
    f = Fraction(x)
    return str(f.numerator) if f.denominator == 1 else f'{f.numerator}/{f.denominator}'


def signed(x: int) -> str:
    return ('+ ' if x >= 0 else '− ') + str(abs(x))


def polynomial(b: int, c: int, a: int=1) -> str:
    lead = 'x²' if a == 1 else f'{a}x²'
    bx = '' if b == 0 else ' ' + signed(b) + ('x' if abs(b) == 1 else 'x')
    # Ne pas écrire 1x ; 0x ou + 0 dans les énoncés.
    if b != 0:
        bx = ' ' + ('+ ' if b > 0 else '− ') + ('x' if abs(b) == 1 else f'{abs(b)}x')
    cx = '' if c == 0 else ' ' + signed(c)
    return lead + bx + cx


def exercise(level: str, kind: int, r: random.Random) -> dict:
    """Formules déterministes; variantes contrôlées par asserts arithmétiques."""
    if level == '3e':
        if kind == 0:  # Géométrie : ne dessine surtout pas un triangle impossible.
            a, b = sorted(r.sample(range(3, 10), 2))
            c = a + b + r.randint(1, 4)
            assert a+b < c
            return dict(topic='Inégalité triangulaire', question=f'Peut-on construire un triangle de côtés {a} cm, {b} cm et {c} cm ?', hint='Additionne les deux plus petits côtés et compare avec le plus grand.', steps=[f'{a} + {b} = {a+b}', f'{a+b} < {c}', 'L’inégalité triangulaire n’est pas respectée.'], answer='Non : ce triangle est impossible.', take='La somme des deux petits côtés doit être strictement supérieure au troisième.')
        if kind == 1:
            a, b, c = r.randint(2, 7), r.randint(2, 7), r.randint(2, 5)
            assert a*(b+c) == a*b+a*c
            return dict(topic='Calcul littéral', question=f'Développe et réduis : {a}(x + {b}) + {c}x', hint='Distribue le facteur, puis regroupe les termes en x.', steps=[f'{a}(x + {b}) = {a}x + {a*b}', f'{a}x + {a*b} + {c}x', f'= {a+c}x + {a*b}'], answer=f'{a+c}x + {a*b}', take='a(b + c) = ab + ac : c’est la distributivité.')
        if kind == 2:
            x = r.randint(-4, 8)
            a, b = r.randint(2, 8), r.randint(1, 10)
            c = a*x+b
            assert a*x+b == c
            return dict(topic='Équations', question=f'Résous : {a}x + {b} = {c}', hint='Soustrais le terme constant, puis divise par le coefficient de x.', steps=[f'{a}x = {c} − {b}', f'{a}x = {a*x}', f'x = {a*x} ÷ {a} = {x}'], answer=f'x = {x}', take='On effectue la même opération sur les deux membres.')
        if kind == 3:
            a, b = r.randint(2, 9), r.randint(2, 9)
            return dict(topic='Factorisation', question=f'Factorise : {a}x + {a*b}', hint='Cherche le facteur commun aux deux termes.', steps=[f'{a}x + {a*b} = {a} × x + {a} × {b}', f'On met {a} en facteur.', f'= {a}(x + {b})'], answer=f'{a}(x + {b})', take='Mettre en facteur, c’est appliquer la distributivité à l’envers.')
        if kind == 4:
            a, b = r.randint(2, 6), r.randint(-4, 4)
            val=a+b
            return dict(topic='Puissances de 10', question=f'Simplifie : 10^{a} × 10^({b}).', hint='Lorsqu’on multiplie deux puissances de 10, on additionne les exposants.', steps=[f'10^{a} × 10^({b}) = 10^({a} + ({b}))', f'On additionne : {a} + ({b}) = {val}', f'= 10^{val}'], answer=f'10^{val}', take='10^a × 10^b = 10^(a+b).')
        if kind == 5:
            a, b = r.randint(2, 8), r.randint(2, 9)
            x = r.randint(-3, 7)
            y = a*x+b
            assert y == a*x+b
            return dict(topic='Fonctions', question=f'Soit f(x) = {a}x + {b}. Calcule f({x}).', hint='Remplace x par sa valeur, sans oublier les parenthèses.', steps=[f'f({x}) = {a} × ({x}) + {b}', f'= {a*x} + {b}', f'= {y}'], answer=f'f({x}) = {y}', take='L’image de x se calcule en substituant x dans f(x).')
        if kind == 6:
            a, b, c = r.choice([(3,4,5), (5,12,13), (8,15,17)])
            k = r.randint(1, 3)
            a,b,c = a*k,b*k,c*k
            assert a*a+b*b == c*c
            return dict(topic='Pythagore', question=f'Dans un triangle rectangle, les côtés de l’angle droit mesurent {a} cm et {b} cm. Quelle est l’hypoténuse ?', hint='Applique la formule : hypoténuse² = côté 1² + côté 2².', steps=[f'c² = {a}² + {b}²', f'c² = {a*a} + {b*b} = {c*c}', f'c = √{c*c} = {c} cm'], answer=f'{c} cm', take='L’hypoténuse est le côté le plus long.')
        if kind == 7:
            red, blue = r.randint(2, 9), r.randint(2, 9)
            p = Fraction(red,red+blue)
            return dict(topic='Probabilités', question=f'Une urne contient {red} boules rouges et {blue} bleues. Quelle est P(rouge) ?', hint='Nombre de boules rouges / nombre total de boules.', steps=[f'Total : {red} + {blue} = {red+blue}', f'P(rouge) = {red}/{red+blue}', f'On simplifie : {fmt_fraction(p)}'], answer=fmt_fraction(p), take='Cas équiprobables : probabilité = favorables / possibles.')
        if kind == 8:
            initial, percentage = r.choice([100, 120, 200, 240, 400]), r.choice([10, 15, 20, 25])
            discount = Fraction(initial*percentage,100)
            final = Fraction(initial)-discount
            assert final >= 0
            return dict(topic='Pourcentages', question=f'Un article coûte {initial} €. Il est soldé à −{percentage} %. Quel est son nouveau prix ?', hint='Calcule la remise, puis retire-la au prix initial.', steps=[f'Remise : {initial} × {percentage}/100', f'= {fmt_fraction(discount)} €', f'Nouveau prix : {initial} − {fmt_fraction(discount)} = {fmt_fraction(final)} €'], answer=f'{fmt_fraction(final)} €', take='Après −p %, le prix est multiplié par (1 − p/100).')
        if kind == 9:
            n = r.randint(2, 8)
            a,b = n*r.randint(2, 5),n*r.randint(6, 9)
            ratio = Fraction(a,b)
            return dict(topic='Fractions', question=f'Simplifie la fraction {a}/{b}.', hint='Cherche un diviseur commun au numérateur et au dénominateur.', steps=[f'PGCD({a}, {b}) = {math.gcd(a,b)}', f'{a}/{b} = ({a} ÷ {math.gcd(a,b)}) / ({b} ÷ {math.gcd(a,b)})', f'= {fmt_fraction(ratio)}'], answer=fmt_fraction(ratio), take='Divise le numérateur et le dénominateur par le même nombre non nul.')
    if level == '1ère':
        if kind == 0:
            a,b,c = r.randint(1,5),r.randint(-6,6),r.randint(-6,6)
            return dict(topic='Dérivation', question=f'Dérive f(x) = {polynomial(b,c,a)}.', hint='Utilise (x²)′ = 2x et la dérivée d’une constante est nulle.', steps=[f'( {a}x² )′ = {2*a}x', f'({b}x)′ = {b}', f'La constante {c} disparaît.'], answer=f'f′(x) = {2*a}x {signed(b)}', take='(ax² + bx + c)′ = 2ax + b.')
        if kind == 1:
            u0, delta, n = r.randint(-5,12), r.choice([-4,-3,-2,2,3,4,5]), r.randint(4,9)
            result = u0+n*delta
            return dict(topic='Suites arithmétiques', question=f'Suite arithmétique : u₀ = {u0} et raison r = {delta}. Calcule u₍{n}₎.', hint='Pour une suite arithmétique, uₙ = u₀ + nr.', steps=[f'u₍{n}₎ = {u0} + {n} × ({delta})', f'= {u0} + ({n*delta})', f'= {result}'], answer=f'u₍{n}₎ = {result}', take='uₙ = u₀ + nr pour une suite arithmétique.')
        if kind == 2:
            u0, q, n = r.randint(1,5),r.randint(2,3),r.randint(3,5)
            val = u0*q**n
            return dict(topic='Suites géométriques', question=f'Suite géométrique : u₀ = {u0}, raison q = {q}. Calcule u₍{n}₎.', hint='Utilise uₙ = u₀ × qⁿ.', steps=[f'u₍{n}₎ = {u0} × {q}^{n}', f'{q}^{n} = {q**n}', f'{u0} × {q**n} = {val}'], answer=f'u₍{n}₎ = {val}', take='uₙ = u₀ × qⁿ pour une suite géométrique.')
        if kind == 3:
            u,v = sorted(r.sample(range(-5,7), 2))
            b,c = -(u+v),u*v
            delta = b*b-4*c
            assert delta==(u-v)**2
            return dict(topic='Second degré', question=f'Résous {polynomial(b,c)} = 0.', hint='Calcule le discriminant Δ = b² − 4ac.', steps=[f'Δ = ({b})² − 4 × 1 × ({c})', f'Δ = {delta}', f'Racines : {u} et {v}'], answer=f'S = {{{u} ; {v}}}', take='Si Δ > 0 : deux solutions réelles distinctes.')
        if kind == 4:
            a = r.randint(2,6)
            b = r.randint(1,6)
            x0 = r.randint(-2,4)
            slope = 2*a*x0+b
            intercept = (a*x0*x0+b*x0)-slope*x0
            assert slope*x0+intercept == a*x0*x0+b*x0
            return dict(topic='Tangente', question=f'Pour f(x) = {a}x² + {b}x, donne la pente de la tangente en x = {x0}.', hint='La pente de la tangente vaut f′(x₀).', steps=[f'f′(x) = {2*a}x + {b}', f'f′({x0}) = {2*a} × ({x0}) + {b}', f'= {slope}'], answer=f'Pente = {slope}', take='Le coefficient directeur de la tangente en a est f′(a).')
        if kind == 5:
            a,b = sorted(r.sample(range(-5,7),2))
            return dict(topic='Signe d’un trinôme', question=f'Étudie le signe de (x − ({a}))(x − ({b})).', hint='Les racines sont les deux valeurs qui annulent chaque facteur.', steps=[f'Racines : x = {a} et x = {b}', 'Produit positif à l’extérieur des racines.', f'Produit négatif si {a} < x < {b}.'], answer=f'Positif si x < {a} ou x > {b} ; nul aux racines.', take='Un trinôme de coefficient dominant positif est positif hors des racines.')
        if kind == 6:
            a,b,c,d = [r.randint(-4,5) for _ in range(4)]
            prod = a*c+b*d
            return dict(topic='Produit scalaire', question=f'Calcule u · v pour u = ({a} ; {b}) et v = ({c} ; {d}).', hint='En coordonnées : u · v = xᵤxᵥ + yᵤyᵥ.', steps=[f'u · v = {a} × ({c}) + {b} × ({d})', f'= {a*c} + ({b*d})', f'= {prod}'], answer=f'u · v = {prod}', take='Le produit scalaire vaut xx′ + yy′ dans un repère orthonormé.')
        if kind == 7:
            a,b = r.choice([(1,2),(2,3),(3,4),(3,5)]),r.choice([(1,2),(1,3),(2,5)])
            pa,pba = Fraction(*a),Fraction(*b)
            pab = pa*pba
            return dict(topic='Probabilités conditionnelles', question=f'Si P(A) = {fmt_fraction(pa)} et P(B | A) = {fmt_fraction(pba)}, combien vaut P(A ∩ B) ?', hint='Utilise P(A ∩ B) = P(A) × P(B | A).', steps=[f'P(A ∩ B) = {fmt_fraction(pa)} × {fmt_fraction(pba)}', f'= {pa.numerator*pba.numerator}/{pa.denominator*pba.denominator}', f'= {fmt_fraction(pab)}'], answer=f'P(A ∩ B) = {fmt_fraction(pab)}', take='P(A ∩ B) = P(A) × P(B sachant A).')
        if kind == 8:
            a,b,c = r.randint(1,5),r.randint(-5,5),r.randint(-5,5)
            v = r.randint(-3,4)
            value = a*v*v+b*v+c
            return dict(topic='Polynômes', question=f'Soit f(x) = {polynomial(b,c,a)}. Calcule f({v}).', hint='Attention au carré si x est négatif.', steps=[f'f({v}) = {a} × ({v})² + ({b}) × ({v}) + ({c})', f'= ({a*v*v}) + ({b*v}) + ({c})', f'= {value}'], answer=f'f({v}) = {value}', take='Pour calculer une image, remplace x puis respecte les priorités.')
        if kind == 9:
            n = r.randint(2,7)
            a = r.randint(1,4)
            b = r.randint(1,8)
            val = a*n*n+b*n
            return dict(topic='Suites explicites', question=f'On définit uₙ = {a}n² + {b}n. Calcule u₍{n}₎.', hint='Remplace n par le rang demandé dans la formule explicite.', steps=[f'u₍{n}₎ = {a} × {n}² + {b} × {n}', f'= {a*n*n} + {b*n}', f'= {val}'], answer=f'u₍{n}₎ = {val}', take='Une formule explicite donne directement uₙ en fonction de n.')
    raise ValueError(f'Combinaison niveau/modèle inconnue : {level} / {kind}')


def face(size: int, kind: str='regular') -> ImageFont.FreeTypeFont:
    name = {'regular':FONT_REG, 'bold':FONT_BOLD,'serif':FONT_SERIF,'italic':FONT_ITALIC}[kind]
    path = FONT_DIR / name
    if not path.exists():
        path = FONT_DIR / FONT_BOLD
    return ImageFont.truetype(str(path), size)


def textwidth(d: ImageDraw.ImageDraw, text: str, f) -> int:
    bb = d.textbbox((0, 0), text, font=f)
    return bb[2]-bb[0]


def center(d, text, xcenter, y, size, fill, kind='regular'):
    f=face(size,kind)
    d.text((xcenter-textwidth(d,text,f)/2,y),text,font=f,fill=fill)


def lines_fit(d, text, width, height, maxsize=55, minsize=25, kind='bold'):
    for size in range(maxsize,minsize-1,-2):
        f=face(size,kind)
        output=[]
        for para in text.split('\n'):
            line=''
            for word in para.split(' '):
                candidate=(line+' '+word).strip()
                if not line or textwidth(d,candidate,f) <= width:
                    line=candidate
                else:
                    output.append(line)
                    line=word
            output.append(line)
        gap=int(size*1.34)
        if len(output)*gap <= height and all(textwidth(d,line,f)<=width for line in output):
            return f,output,gap
    raise ValueError(f'Texte trop long pour le cadre : {text}')


def draw_centered(d, text, box, maxsize=58, minsize=25, color=NAVY,kind='bold'):
    x0,y0,x1,y1=box
    f, ls, gap = lines_fit(d,text,x1-x0-18,y1-y0-22,maxsize,minsize,kind)
    y = y0+(y1-y0-gap*len(ls))/2-2
    for line in ls:
        d.text(((x0+x1-textwidth(d,line,f))/2,y),line,font=f,fill=color)
        y += gap


def gradient_image() -> Image.Image:
    im = Image.new('RGB',(SIZE,SIZE))
    pixels=im.load()
    for y in range(SIZE):
        t=y/(SIZE-1)
        # Dégradé bleu ciel vers rose poudré
        color=tuple(round((1-t)*a+t*b) for a,b in zip((194,231,255),(255,207,227)))
        for x in range(SIZE):pixels[x,y]=color
    return im


def math_tile(im, glyph, x, y, fill, tilt):
    tile=Image.new('RGBA',(164,164),(0,0,0,0))
    d=ImageDraw.Draw(tile)
    d.rounded_rectangle((9,9,155,155),radius=25,fill=fill,outline='#FFFFFF',width=5)
    # Pas de motifs à trois traits : uniquement les symboles mathématiques.
    f=face(105,'bold')
    bb=d.textbbox((0,0),glyph,font=f)
    d.text(((164-(bb[2]-bb[0]))/2-bb[0],(164-(bb[3]-bb[1]))/2-bb[1]-4),glyph,font=f,fill='white')
    tile=tile.rotate(tilt,Image.Resampling.BICUBIC,expand=True)
    im.paste(tile,(x,y),tile)


def calculator(im):
    tile=Image.new('RGBA',(165,230),(0,0,0,0))
    d=ImageDraw.Draw(tile)
    d.rounded_rectangle((8,6,156,225),radius=19,fill='#0276C5',outline='#04518D',width=6)
    d.rounded_rectangle((24,27,140,67),radius=7,fill='#C6D9C9')
    for ri in range(4):
        for ci in range(3):
            x=24+ci*40; y=86+ri*33
            d.rounded_rectangle((x,y,x+31,y+26),radius=5,fill='#204E87')
            center(d,'7894561230.='[ri*3+ci],x+16,y+3,16,WHITE,'bold')
    tile=tile.rotate(-16,Image.Resampling.BICUBIC,expand=True)
    im.paste(tile,(923,849),tile)


def school_background():
    im=gradient_image()
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((66,55,1012,1030),radius=18,fill=WHITE,outline='#79A8ED',width=3)
    math_tile(im,'+',37,-39,'#EA7190',5)
    math_tile(im,'÷',-38,36,'#858BC6',-16)
    math_tile(im,'×',92,40,'#45B9EA',24)
    # Grands chiffres détourés en bas à gauche, style fiche de révision.
    d=ImageDraw.Draw(im)
    for digit,x,y,rot in [('2',-32,895,-10),('3',54,932,11)]:
        temp=Image.new('RGBA',(145,145),(0,0,0,0))
        dt=ImageDraw.Draw(temp)
        ft=face(117,'bold')
        dt.text((16,0),digit,font=ft,fill='white',stroke_width=4,stroke_fill='#17273B')
        temp=temp.rotate(rot,Image.Resampling.BICUBIC)
        im.paste(temp,(x,y),temp)
    calculator(im)
    return im


def header(d, level, handle):
    center(d,'L’AUTOMATISME DU JOUR',575,92,41,'#111111','serif')
    center(d,f'Niveau {level}',575,156,31,NAVY)
    center(d,'@'+handle.lstrip('@'),575,199,27,NAVY)


def capsule(d, num, name):
    label=f'{num}. {name}'
    f=face(31,'italic')
    width=textwidth(d,label,f)+53
    d.rounded_rectangle((101,266,101+width,319),radius=20,fill=SOFTPINK,outline='#EE99B3',width=2)
    d.text((123,272),label,font=f,fill='#101010')


def box(d, coords, color, outline=None, radius=23):
    d.rounded_rectangle(coords,radius=radius,fill=color,outline=outline,width=2 if outline else 1)


def bottom_bar(d, label):
    box(d,(184,884,896,975),SOFTPINK,'#F38CAC',22)
    draw_centered(d,label,(210,899,870,963),maxsize=35,minsize=23,color='#151515',kind='bold')


def slide(pos, level, e, config, out):
    im=school_background();d=ImageDraw.Draw(im)
    header(d,level,config.get('handle','tomsdrawingsoff'))
    section_names=['Question','Indice','Correction','Fiches de révision']
    capsule(d,['I','II','III','IV'][pos-1],section_names[pos-1])
    if pos==1:
        box(d,(105,347,977,599),SOFTBLUE)
        draw_centered(d,e['question'],(132,358,950,583),maxsize=54,minsize=27)
        box(d,(150,618,935,702),CREAM)
        draw_centered(d,'Prends quelques secondes pour réfléchir.',(170,624,914,695),maxsize=34,minsize=25,color=DARK,kind='regular')
        # Une illustration abstraite de cahier mathématique, sans tracé faux.
        box(d,(237,747,842,844),'#F0F8FF','#BBDCF8',15)
        topic_size=35
        while topic_size>18 and textwidth(d,e['topic'].upper(),face(topic_size,'bold')) > 555:
            topic_size-=1
        center(d,e['topic'].upper(),542,775,topic_size,BLUE,'bold')
        bottom_bar(d,'Fais défiler pour découvrir l’indice →')
    elif pos==2:
        box(d,(105,347,977,673),SOFTBLUE)
        draw_centered(d,e['hint'],(140,380,940,640),maxsize=55,minsize=27)
        box(d,(145,702,938,831),CREAM)
        draw_centered(d,'Essaie de résoudre avant de regarder la correction.',(175,713,912,815),maxsize=33,minsize=26,color=DARK,kind='regular')
        bottom_bar(d,'Découvre la correction à la suite →')
    elif pos==3:
        box(d,(102,347,976,778),'#EAF5FF')
        for idx, step in enumerate(e['steps'],1):
            y = 369+(idx-1)*128
            box(d,(125,y,952,y+113),WHITE)
            box(d,(147,y+25,203,y+82),'#F9C9DA')
            center(d,str(idx),175,y+31,31,PINK,'bold')
            draw_centered(d,step,(215,y+11,928,y+103),maxsize=33,minsize=22,color=NAVY,kind='regular')
        box(d,(156,783,931,884),CREAM)
        draw_centered(d,e['answer'],(177,789,914,877),maxsize=39,minsize=21,color=PINK,kind='bold')
        bottom_bar(d,'Tu veux progresser ? Dernière slide →')
    else:
        box(d,(119,349,968,546),SOFTBLUE)
        draw_centered(d,'MES FICHES DE RÉVISION',(142,368,945,526),maxsize=54,minsize=30,color=NAVY)
        box(d,(220,574,423,657),SOFTPINK,'#F19EB8')
        box(d,(643,574,858,657),SOFTPINK,'#F19EB8')
        draw_centered(d,'3e',(235,578,407,648),maxsize=46,minsize=35,color=PINK)
        draw_centered(d,'1ère',(662,578,841,648),maxsize=46,minsize=35,color=PINK)
        draw_centered(d,'Révise les méthodes et entraîne-toi', (167,682,917,754),maxsize=39,minsize=25,color=NAVY,kind='regular')
        draw_centered(d,'avec mes fiches de maths !',(167,744,917,821),maxsize=42,minsize=26,color=NAVY,kind='bold')
        bottom_bar(d,config.get('last_slide_call_to_action','Clique sur le lien sur mon profil →'))
    out.parent.mkdir(parents=True,exist_ok=True)
    im.save(out,format='JPEG',quality=90,subsampling=0,optimize=True)


def build(day: str) -> Path:
    dt=date.fromisoformat(day)
    config=json.loads(CONFIG.read_text(encoding='utf-8'))
    # Alternance stricte : 3e les jours de parité 0 depuis l'origine, 1ère les autres.
    levels = config.get('levels', ['3e', '1ère'])
    if levels != ['3e', '1ère']:
        raise ValueError('La série doit rester limitée aux niveaux 3e et 1ère.')
    level = levels[dt.toordinal()%2]
    kind = (dt.toordinal()//2)%10
    seed=int.from_bytes(hashlib.sha256(day.encode()).digest()[:8],'big')
    e=exercise(level,kind,random.Random(seed))
    folder=BASE/day
    for pos in range(1,5):
        slide(pos,level,e,config,folder/f'{pos}.jpg')
    caption=(f'✏️ L’AUTOMATISME DU JOUR — {level} | {e["topic"]}\n\n'
             f'{e["question"]}\n\n'
             'Fais défiler pour voir l’indice, la correction puis mes fiches de révision. '
             'Tu veux t’entraîner davantage ? Clique sur le lien sur mon profil 📚\n\n'
             '#maths #mathematiques #revisions ' + ('#brevet #troisieme' if level=='3e' else '#premierespe #premiere'))
    payload={'date':day,'level':level,'topic':e['topic'],'images':[f'{i}.jpg' for i in range(1,5)],'caption':caption,'exercise':e,'style':'fiches-pastel-v2','handle':'@'+config.get('handle','tomsdrawingsoff').lstrip('@')}
    (folder/'post.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'docs'/'index.html').write_text('''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Automatisme du jour</title><style>body{font-family:sans-serif;max-width:700px;margin:2rem auto;padding:1rem;background:#E8F3FF;color:#182433}img{display:block;max-width:100%;margin:1.5rem auto;border-radius:1rem;box-shadow:0 3px 16px #2343}</style><h1>Automatisme du jour</h1><p>Carrousel du '''+day+''' — niveau '''+level+'''</p>'''+''.join(f'<img alt="Slide {i}" src="posts/{day}/{i}.jpg">' for i in range(1,5)),encoding='utf-8')
    print(f'✅ {day} : {level} / {e["topic"]} — 4 slides pastel, CTA fiches sur la 4e')
    return folder


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--date',help='YYYY-MM-DD (défaut : jour courant Europe/Paris)')
    args=parser.parse_args()
    day=args.date or datetime.now(ZoneInfo('Europe/Paris')).date().isoformat()
    build(day)


if __name__=='__main__':
    main()
