#!/usr/bin/env python3
"""Generate the project's original low-poly GLB models and SVG illustrations.

Uses only the Python standard library. Geometry is built from first principles;
no third-party meshes, textures, photographs, or icon packs are incorporated.
"""

import json, math, struct, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "dist" / "models"
ASSETS = ROOT / "dist" / "assets"

COLORS = {
    "wood": [0.42, 0.20, 0.07, 1], "wood2": [0.68, 0.39, 0.14, 1],
    "dark": [0.055, 0.075, 0.067, 1], "metal": [0.28, 0.32, 0.31, 1],
    "brass": [0.70, 0.46, 0.10, 1], "paper": [0.91, 0.86, 0.68, 1],
    "cloth": [0.76, 0.70, 0.52, 1], "green": [0.18, 0.45, 0.32, 1],
    "acid": [0.58, 0.90, 0.22, 1], "red": [0.62, 0.12, 0.08, 1],
    "screen": [0.22, 0.57, 0.58, 1], "black": [0.015, 0.02, 0.018, 1],
}


def cube_geometry():
    p, n, uv, idx = [], [], [], []
    faces = [
        ((1,0,0), [(1,-1,-1),(1,1,-1),(1,1,1),(1,-1,1)]),
        ((-1,0,0), [(-1,-1,1),(-1,1,1),(-1,1,-1),(-1,-1,-1)]),
        ((0,1,0), [(-1,1,-1),(-1,1,1),(1,1,1),(1,1,-1)]),
        ((0,-1,0), [(-1,-1,1),(-1,-1,-1),(1,-1,-1),(1,-1,1)]),
        ((0,0,1), [(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]),
        ((0,0,-1), [(1,-1,-1),(-1,-1,-1),(-1,1,-1),(1,1,-1)]),
    ]
    for normal, verts in faces:
        b=len(p); p.extend([(x/2,y/2,z/2) for x,y,z in verts]); n.extend([normal]*4)
        uv.extend([(0,0),(1,0),(1,1),(0,1)])
        idx.extend([b,b+1,b+2,b,b+2,b+3])
    return p,n,uv,idx


def cylinder_geometry(segments=48):
    p,n,uv,idx=[],[],[],[]
    for i in range(segments):
        a=2*math.pi*i/segments; b=2*math.pi*(i+1)/segments
        base=len(p)
        p += [(math.cos(a)/2,-.5,math.sin(a)/2),(math.cos(b)/2,-.5,math.sin(b)/2),
              (math.cos(b)/2,.5,math.sin(b)/2),(math.cos(a)/2,.5,math.sin(a)/2)]
        n += [(math.cos(a),0,math.sin(a)),(math.cos(b),0,math.sin(b)),
              (math.cos(b),0,math.sin(b)),(math.cos(a),0,math.sin(a))]
        uv += [(i/segments,0),((i+1)/segments,0),((i+1)/segments,1),(i/segments,1)]
        idx += [base,base+1,base+2,base,base+2,base+3]
    for y,ny,reverse in [(-.5,-1,True),(.5,1,False)]:
        c=len(p); p.append((0,y,0)); n.append((0,ny,0)); uv.append((.5,.5))
        for i in range(segments):
            a=2*math.pi*i/segments; p.append((math.cos(a)/2,y,math.sin(a)/2)); n.append((0,ny,0)); uv.append(((math.cos(a)+1)/2,(math.sin(a)+1)/2))
        for i in range(segments):
            a=c; b=c+1+i; d=c+1+(i+1)%segments
            idx += [a,d,b] if reverse else [a,b,d]
    return p,n,uv,idx


def wedge_geometry():
    p=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,-.5,.5),(-.5,-.5,.5),(-.5,.5,-.5),(.5,.5,-.5)]
    faces=[(0,3,2,1),(0,1,5,4),(0,4,3),(1,2,5),(3,4,5,2)]
    outp=[]; outn=[]; uv=[]; idx=[]
    for face in faces:
        a,b,c=[p[i] for i in face[:3]]
        u=[b[i]-a[i] for i in range(3)]; v=[c[i]-a[i] for i in range(3)]
        no=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        ln=math.sqrt(sum(x*x for x in no)); no=tuple(x/ln for x in no)
        base=len(outp); outp += [p[i] for i in face]; outn += [no]*len(face)
        uv += ([(0,0),(1,0),(1,1),(0,1)] if len(face)==4 else [(0,0),(1,0),(.5,1)])
        idx += [base,base+1,base+2] + ([base,base+2,base+3] if len(face)==4 else [])
    return outp,outn,uv,idx


GEOMETRY={"box":cube_geometry(),"cyl":cylinder_geometry(),"wedge":wedge_geometry()}
QX=(math.sin(math.pi/4),0,0,math.cos(math.pi/4))
QZ=(0,0,math.sin(math.pi/4),math.cos(math.pi/4))

def part(shape, pos, scale, color, rot=None): return (shape,pos,scale,color,rot)
def box(pos,scale,color="wood",rot=None): return part("box",pos,scale,color,rot)
def cyl(pos,scale,color="metal",axis="y"):
    return part("cyl",pos,scale,color, QX if axis=="z" else QZ if axis=="x" else None)
def wedge(pos,scale,color="wood",rot=None): return part("wedge",pos,scale,color,rot)


MODELSPEC={
"wheel":[cyl((0,0,-.05),(2.52,.24,2.52),"dark","z"),cyl((0,0,.02),(2.35,.38,2.35),"wood2","z"),cyl((0,0,.24),(.72,.58,.72),"wood","z"),cyl((0,0,.5),(.34,1.05,.34),"dark","z")],
"boat":[wedge((0,0,0),(3.8,.8,1.2),"wood2"),box((0,.15,0),(3.2,.18,1.0),"wood"),cyl((0,1.05,0),(.10,2.7,.10),"dark"),wedge((-.02,1.25,.02),(1.85,1.6,.06),"cloth")],
"press":[box((0,-.8,0),(2.8,.35,1.8),"wood"),box((-1.05,.45,0),(.34,2.7,.5),"wood2"),box((1.05,.45,0),(.34,2.7,.5),"wood2"),box((0,1.65,0),(2.5,.42,.7),"wood"),box((0,-.12,0),(2.0,.18,1.25),"paper"),box((0,.52,0),(1.7,.26,1.05),"wood2"),cyl((0,1.08,0),(.22,1.3,.22),"metal"),box((0,1.62,0),(2.0,.12,.12),"metal")],
"engine":[box((0,-.82,0),(3.4,.35,1.5),"dark"),cyl((0,.15,0),(1.15,2.5,1.15),"metal","x"),cyl((-.85,1.15,0),(.46,1.7,.46),"black"),cyl((1.05,-.15,.72),(1.45,.22,1.45),"brass","z"),cyl((1.05,-.15,.78),(.35,.32,.35),"dark","z"),box((0,-.2,0),(2.5,.18,1.15),"red")],
"telephone":[box((0,-.65,0),(2.2,.55,1.4),"wood"),box((0,.18,0),(1.25,1.25,.75),"wood2"),cyl((0,.22,.42),(.55,.18,.55),"brass","z"),box((0,1.08,0),(1.75,.22,.34),"dark"),cyl((-.85,1.08,0),(.48,.4,.48),"black","x"),cyl((.85,1.08,0),(.48,.4,.48),"black","x")],
"flyer":[box((0,.05,0),(4.8,.12,.72),"cloth"),box((0,.82,.12),(4.8,.12,.72),"cloth"),box((0,.42,0),(.18,.78,2.9),"wood2"),box((0,.43,-1.2),(1.7,.08,.45),"cloth"),box((0,.82,-1.2),(.08,.7,.5),"cloth"),cyl((0,.42,1.58),(.42,.28,.42),"metal","z"),box((0,.42,1.85),(2.0,.08,.12),"wood")],
"motorwagen":[box((0,.25,0),(2.8,.28,1.25),"wood"),box((-.35,.72,0),(1.45,.65,1.05),"dark"),box((.9,.68,0),(.65,.48,.8),"brass"),cyl((-1.0,-.35,-.72),(1.25,.2,1.25),"black","z"),cyl((-1.0,-.35,.72),(1.25,.2,1.25),"black","z"),cyl((1.0,-.35,-.72),(1.25,.2,1.25),"black","z"),cyl((1.0,-.35,.72),(1.25,.2,1.25),"black","z"),cyl((0,.9,-.66),(.8,.08,.8),"wood2","x")],
"wireless":[box((0,-.75,0),(2.8,.35,1.55),"wood"),cyl((0,.05,0),(.75,1.35,.75),"wood2"),cyl((0,.05,0),(.85,1.1,.85),"brass"),cyl((-.95,.55,0),(.12,2.25,.12),"metal"),cyl((.95,.55,0),(.12,2.25,.12),"metal"),box((0,1.55,0),(2.05,.12,.12),"metal"),cyl((0,-.38,.8),(.28,.18,.28),"black","z")],
"television":[box((0,0,0),(2.9,2.1,1.35),"wood"),box((-.35,.2,.71),(1.85,1.35,.08),"screen"),cyl((1.05,.42,.74),(.28,.12,.28),"brass","z"),cyl((1.05,-.18,.74),(.22,.12,.22),"brass","z"),cyl((-.45,1.3,0),(.08,1.5,.08),"metal"),cyl((.45,1.3,0),(.08,1.5,.08),"metal")],
"eniac":[box((-1.15,0,0),(1.0,2.7,.75),"dark"),box((0,0,0),(1.0,2.7,.75),"dark"),box((1.15,0,0),(1.0,2.7,.75),"dark"),box((0,-1.5,0),(3.5,.18,1.1),"metal")]
}

for x in [-1.38,-1.15,-.92,-.23,0,.23,.92,1.15,1.38]:
    for y,c in [(-.75,"acid"),(-.3,"red"),(.15,"brass"),(.6,"green")]:
        MODELSPEC["eniac"].append(cyl((x,y,.41),(.11,.08,.11),c,"z"))


def procedural_wood_png(size=256):
    """Create a deterministic, seamless-looking wood-grain PNG."""
    rows=[]
    for y in range(size):
        row=bytearray([0])
        for x in range(size):
            wave=math.sin(y*.23 + math.sin(x*.055)*3.2 + math.sin(y*.037)*2.1)
            fine=math.sin(y*1.37+x*.03)*.22
            knot=math.sin(math.sqrt((x-78)**2+(y-142)**2)*.22)*math.exp(-((x-78)**2+(y-142)**2)/2600)
            v=wave*.5+fine+knot*.8
            row += bytes((max(0,min(255,int(126+38*v))), max(0,min(255,int(77+25*v))), max(0,min(255,int(38+15*v))), 255))
        rows.append(bytes(row))
    raw=b"".join(rows)
    def chunk(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",size,size,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")


WOOD_PNG=procedural_wood_png()


def write_glb(name, parts):
    blob=bytearray(); views=[]; accessors=[]; meshes=[]; nodes=[]; materials=[]; mat_index={}
    def add_data(data, target=None):
        while len(blob)%4: blob.append(0)
        offset=len(blob); blob.extend(data); view={"buffer":0,"byteOffset":offset,"byteLength":len(data)}
        if target: view["target"]=target
        views.append(view); return len(views)-1
    wood_view=add_data(WOOD_PNG)
    for shape,pos,scale,color,rot in parts:
        if color not in mat_index:
            mat_index[color]=len(materials); rgba=COLORS[color]
            pbr={"baseColorFactor":rgba,"metallicFactor":.72 if color=="metal" else .45 if color=="brass" else 0,"roughnessFactor":.34 if color in ("metal","brass") else .72}
            if color in ("wood","wood2"): pbr["baseColorTexture"]={"index":0}
            materials.append({"name":color,"pbrMetallicRoughness":pbr})
        p,n,uv,ind=GEOMETRY[shape]
        pv=add_data(b"".join(struct.pack("<3f",*v) for v in p),34962)
        nv=add_data(b"".join(struct.pack("<3f",*v) for v in n),34962)
        tv=add_data(b"".join(struct.pack("<2f",*v) for v in uv),34962)
        iv=add_data(b"".join(struct.pack("<H",i) for i in ind),34963)
        pa=len(accessors); accessors += [
          {"bufferView":pv,"componentType":5126,"count":len(p),"type":"VEC3","min":[-.5,-.5,-.5],"max":[.5,.5,.5]},
          {"bufferView":nv,"componentType":5126,"count":len(n),"type":"VEC3"},
          {"bufferView":tv,"componentType":5126,"count":len(uv),"type":"VEC2"},
          {"bufferView":iv,"componentType":5123,"count":len(ind),"type":"SCALAR"}]
        meshes.append({"primitives":[{"attributes":{"POSITION":pa,"NORMAL":pa+1,"TEXCOORD_0":pa+2},"indices":pa+3,"material":mat_index[color]}]})
        node={"mesh":len(meshes)-1,"translation":list(pos),"scale":list(scale)}
        if rot: node["rotation"]=list(rot)
        nodes.append(node)
    doc={"asset":{"version":"2.0","generator":"iotfyedu original procedural model generator"},"scene":0,
         "scenes":[{"nodes":list(range(len(nodes)))}],"nodes":nodes,"meshes":meshes,"materials":materials,
         "accessors":accessors,"bufferViews":views,"buffers":[{"byteLength":len(blob)}],
         "samplers":[{"magFilter":9729,"minFilter":9987,"wrapS":10497,"wrapT":10497}],
         "images":[{"name":"Original procedural wood grain","mimeType":"image/png","bufferView":wood_view}],
         "textures":[{"sampler":0,"source":0}]}
    js=json.dumps(doc,separators=(",",":")).encode(); js+=b" "*((4-len(js)%4)%4); blob+=b"\0"*((4-len(blob)%4)%4)
    total=12+8+len(js)+8+len(blob)
    out=struct.pack("<4sII",b"glTF",2,total)+struct.pack("<I4s",len(js),b"JSON")+js+struct.pack("<I4s",len(blob),b"BIN\0")+blob
    (MODELS/f"{name}.glb").write_bytes(out)


def write_svg(name,label,kind):
    motifs={
      "wheel":'<circle cx="100" cy="85" r="52"/><circle cx="100" cy="85" r="12"/><path d="M48 85h104M100 33v104M63 48l74 74M137 48l-74 74"/>',
      "boat":'<path d="M35 105h130l-22 25H58z"/><path d="M100 28v78M102 35l48 55h-48z"/>',
      "press":'<path d="M50 125V40h100v85M42 125h116M62 58h76M72 102h56M100 20v82M82 20h36"/>',
      "engine":'<rect x="35" y="65" width="105" height="48" rx="22"/><path d="M60 65V35h25v30M25 122h150"/><circle cx="145" cy="108" r="32"/>',
      "telephone":'<rect x="55" y="60" width="90" height="62" rx="8"/><path d="M55 45q45-28 90 0l-15 18q-30-16-60 0z"/><circle cx="100" cy="87" r="18"/>',
      "flyer":'<path d="M20 75h160M35 105h130M100 45v90M68 55l32-10 32 10"/><circle cx="100" cy="44" r="9"/>',
      "motorwagen":'<path d="M35 104h130l-12-38H70L55 42H35"/><circle cx="62" cy="112" r="23"/><circle cx="145" cy="112" r="23"/>',
      "wireless":'<rect x="45" y="105" width="110" height="22"/><path d="M70 105V35M130 105V35M70 42h60"/><ellipse cx="100" cy="78" rx="24" ry="34"/><path d="M77 65h46M77 78h46M77 91h46"/>',
      "television":'<rect x="35" y="38" width="130" height="92" rx="10"/><rect x="50" y="52" width="83" height="62" rx="8"/><circle cx="149" cy="70" r="8"/><circle cx="149" cy="96" r="6"/><path d="M78 38L65 18M122 38l13-20"/>',
      "eniac":'<rect x="32" y="28" width="136" height="105"/><path d="M77 28v105M123 28v105"/><path d="M44 48h20M44 66h20M44 84h20M89 48h22M89 66h22M135 48h20M135 66h20M135 84h20"/>'}
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 170"><rect width="200" height="170" rx="18" fill="#f4f7f3"/><g fill="none" stroke="#173d2c" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">{motifs[kind]}</g><text x="100" y="158" text-anchor="middle" font-family="system-ui,sans-serif" font-size="12" font-weight="700" fill="#526159">{label}</text></svg>'''
    (ASSETS/f"{name}.svg").write_text(svg,encoding="utf-8")


LABELS={"wheel":"Ahşap Tekerlek","boat":"Kamış Tekne","press":"Matbaa","engine":"Buhar Makinesi","telephone":"Telefon","flyer":"Wright Uçağı","motorwagen":"Motorwagen","wireless":"Kablosuz Telgraf","television":"Televizyon","eniac":"ENIAC"}
MODELS.mkdir(parents=True,exist_ok=True); ASSETS.mkdir(parents=True,exist_ok=True)
for name,parts in MODELSPEC.items():
    write_glb(name,parts); write_svg(name,LABELS[name],name)
print(f"Generated {len(MODELSPEC)} original GLB models and SVG illustrations")
