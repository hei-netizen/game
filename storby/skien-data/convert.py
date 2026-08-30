#!/usr/bin/env python3
"""OSM + DTM for Skien sentrum -> spillklar JSON i lokale meter-koordinater.

Verdensramme: EPSG:25833 (UTM33N), sentrert på Skien torg.
  spill-x = E - E0   (ost = +x)      x i [-1500, 1500]   -> CITY_W 3000
  spill-z = -(N - N0) (nord = -z)    z i [-1000, 1000]   -> CITY_D 2000
Matcher three.js-konvensjonen i storby/index.html.
"""
import json, math, struct
from utm import ll2utm33
from PIL import Image

E0, N0 = 192365.6, 6575315.6   # 400 m sor for Torget: far med Klosteroya og vannspeilet
HW, HD = 1500.0, 1000.0

VEIBREDDE = {   # meter, brukt som gatebredde i spillet
    'motorway':30,'trunk':28,'primary':26,'secondary':22,'tertiary':18,
    'motorway_link':14,'trunk_link':14,'primary_link':14,'secondary_link':12,
    'tertiary_link':12,'unclassified':14,'residential':15,'living_street':12,
    'pedestrian':10,'service':8,'track':6,
    'footway':4,'path':4,'cycleway':4,'steps':3,
}
ART = {'motorway','trunk','primary','secondary','tertiary'}   # hovedgater
ETASJEHOYDE = 3.2
STD_HOYDE = {   # fallback når OSM mangler height/levels
    'house':7,'detached':7,'semidetached_house':7,'terrace':8,'cabin':4,
    'garage':3,'garages':3,'shed':3,'hut':3,'carport':3,
    'apartments':14,'residential':11,'office':16,'commercial':12,'retail':9,
    'industrial':10,'warehouse':10,'civic':12,'school':9,'kindergarten':5,
    'church':18,'hospital':16,'hotel':16,'barn':7,'farm':7,
}

def proj(geom):
    out=[]
    for p in geom:
        E,N = ll2utm33(p['lat'], p['lon'])
        out.append((round(E-E0,1), round(-(N-N0),1)))
    return out

def signert_areal(p):
    a=0.0
    for i in range(len(p)-1): a+=p[i][0]*p[i+1][1]-p[i+1][0]*p[i][1]
    return a/2

def rens(ring, mot_klokka=True):
    """Lukk ringen, fjern duplikatpunkter, og legg den i riktig omlopsretning.

    91 % av OSM-ringene gar MED klokka. Da peker veggnormalen innover, og
    baksidekutting gjor at man ser rett gjennom bygningen. Alt normaliseres
    til mot klokka (positivt areal) her, en gang, sa motoren slipper a tenke."""
    if len(ring)<3: return None
    ut=[ring[0]]
    for q in ring[1:]:
        if abs(q[0]-ut[-1][0])>1e-4 or abs(q[1]-ut[-1][1])>1e-4: ut.append(q)
    if abs(ut[0][0]-ut[-1][0])>1e-4 or abs(ut[0][1]-ut[-1][1])>1e-4: ut.append(ut[0])
    else: ut[-1]=ut[0]
    if len(ut)<4: return None
    if (signert_areal(ut)<0)==mot_klokka: ut.reverse()
    return ut

def sy_ringer(biter, toler=1.0):
    """Sy sammen linjebiter ende-mot-ende til lukkede ringer."""
    rester=[list(b) for b in biter if len(b)>=2]
    ringer=[]
    while rester:
        ring=rester.pop(0)
        endret=True
        while endret and not (len(ring)>=4 and math.dist(ring[0],ring[-1])<toler):
            endret=False
            for i,r in enumerate(rester):
                if   math.dist(ring[-1], r[0])  < toler: ring+=r[1:];            rester.pop(i); endret=True; break
                elif math.dist(ring[-1], r[-1]) < toler: ring+=r[::-1][1:];      rester.pop(i); endret=True; break
                elif math.dist(ring[0],  r[-1]) < toler: ring=r[:-1]+ring;       rester.pop(i); endret=True; break
                elif math.dist(ring[0],  r[0])  < toler: ring=r[::-1][:-1]+ring; rester.pop(i); endret=True; break
        if len(ring)>=4: ringer.append(ring)
    return ringer

def innenfor(pts, slark=200):
    return any(abs(x)<=HW+slark and abs(z)<=HD+slark for x,z in pts)

im = Image.open('skien_dtm.tif')
d = json.load(open('skien.osm.json'))
els = d['elements']
byid = {e['id']:e for e in els if e['type']=='way'}

veier, bygg, vann, gronn = [], [], [], []

for e in els:
    tg = e.get('tags',{})
    if e['type']=='way':
        g = e.get('geometry')
        if not g or len(g)<2: continue
        pts = proj(g)
        if not innenfor(pts): continue
    elif e['type']=='relation':
        # Multipolygon-medlemmer er BITER av en ring, ikke ferdige ringer.
        # Sys sammen ende-mot-ende, ellers blir en elv til 46 loerevne flater.
        ytre=[m for m in e.get('members',[]) if m.get('geometry') and m.get('role')!='inner']
        indre=[m for m in e.get('members',[]) if m.get('geometry') and m.get('role')=='inner']
        deler=sy_ringer([proj(m['geometry']) for m in ytre]) + \
              sy_ringer([proj(m['geometry']) for m in indre])
        if not deler: continue
        if not any(innenfor(r) for r in deler): continue
        pts=None
    else:
        continue

    if 'highway' in tg and e['type']=='way':
        h=tg['highway']
        if h not in VEIBREDDE: continue
        veier.append({
            'n': tg.get('name'), 'k': h,
            'w': VEIBREDDE[h], 'art': h in ART,
            'bru': 'bridge' in tg, 'tunnel': 'tunnel' in tg,
            'p': pts,
        })
    elif 'building' in tg:
        b=tg['building']
        if tg.get('height'):
            try: hoy=float(str(tg['height']).split()[0])
            except: hoy=None
        else: hoy=None
        if hoy is None and tg.get('building:levels'):
            try: hoy=float(tg['building:levels'])*ETASJEHOYDE
            except: hoy=None
        if hoy is None: hoy=STD_HOYDE.get(b, 8)
        ringer = [pts] if pts else deler
        ytre = rens(ringer[0], True)
        if not ytre: continue
        A = abs(signert_areal(ytre))
        # Smabygg roter til bybildet uten a tilfore noe: 970 boder, garasjer og
        # navnlose skur under 25 m2. Ute.
        if A < 25: continue
        if b in ('garage','garages','shed','carport','roof','hut') and A < 45: continue
        hull = [r for r in (rens(x, False) for x in ringer[1:]) if r]
        bygg.append({'n':tg.get('name'),'k':b,'h':round(hoy,1),'a':round(A),
                     'p':ytre,'hull':hull or None})
    elif tg.get('natural')=='water' or 'waterway' in tg:
        art = tg.get('natural') or tg.get('waterway')
        ringer = [pts] if pts else deler
        for r in ringer:
            lukket = len(r)>=4 and abs(r[0][0]-r[-1][0])<0.5 and abs(r[0][1]-r[-1][1])<0.5
            if art in ('water','riverbank') or lukket:
                rr = rens(r, True)
                if rr and abs(signert_areal(rr)) > 40:
                    vann.append({'n':tg.get('name'),'k':art,'flate':True,'p':rr})
            elif art in ('river','stream','canal','ditch'):
                vann.append({'n':tg.get('name'),'k':art,'flate':False,
                             'w':{'river':28,'canal':14,'stream':5,'ditch':3}[art],'p':r})
    elif tg.get('leisure') in ('park','garden','pitch','playground') or \
         tg.get('landuse') in ('grass','forest','meadow','recreation_ground','cemetery','allotments') or \
         tg.get('natural') in ('wood','scrub','grassland'):
        ringer = [pts] if pts else deler
        for r in ringer:
            rr = rens(r, True)
            if rr and abs(signert_areal(rr)) > 60:
                gronn.append({'n':tg.get('name'),
                              'k':tg.get('leisure') or tg.get('landuse') or tg.get('natural'),'p':rr})

# ---- terreng: DTM -> uint16 binaerfil, 5 m/piksel, radvis fra nord-vest
px = list(im.getdata())
lo, hi = min(px), max(px)
with open('skien_terreng.bin','wb') as fh:
    fh.write(b''.join(struct.pack('<H', int(round((v-lo)/(hi-lo)*65535))) for v in px))

# ---- vannspeil: hver vannflate far sitt eget niva fra DTM langs kanten
import struct
_px=list(im.getdata()); _W,_H=im.size
def _dtm(x,z):
    c=int((x+HW)/5); r=int((z+HD)/5)
    c=max(0,min(_W-1,c)); r=max(0,min(_H-1,r))
    return _px[r*_W+c]
for v in vann:
    hs=sorted(_dtm(x,z) for x,z in v['p'])
    v['y']=round(hs[len(hs)//2],2) if hs else 0.0

meta = {
  'kilde': 'OpenStreetMap (ODbL) + Kartverket DTM1 (NLOD)',
  'crs': 'EPSG:25833', 'senter_utm': [E0, N0], 'senter_wgs84': [59.2085, 9.6090],
  'verden': {'bredde': 3000, 'dybde': 2000, 'x': [-HW, HW], 'z': [-HD, HD]},
  'akser': 'x = ost (+), z = sor (+), nord = -z. 1 enhet = 1 meter.',
  'terreng': {'fil':'skien_terreng.bin','format':'uint16 little-endian, radvis fra nord-vest',
              'bredde':im.size[0],'hoyde':im.size[1],
              'meter_per_piksel':5, 'min_m':round(lo,3), 'maks_m':round(hi,3),
              'formel':'h = min_m + (u16/65535)*(maks_m-min_m)'},
  'antall': {'veier':len(veier),'bygg':len(bygg),'vann':len(vann),'gronn':len(gronn)},
}
json.dump({'meta':meta,'veier':veier,'bygg':bygg,'vann':vann,'gronn':gronn},
          open('skien.json','w'), separators=(',',':'))
print(json.dumps(meta, indent=2, ensure_ascii=False))
