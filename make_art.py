"""Draws the product art used on cards until real product photos arrive from affiliate feeds.
One SVG per category in /art. Run once; re-run only to change the drawings."""
import pathlib
OUT = pathlib.Path(__file__).parent / "art"
OUT.mkdir(exist_ok=True)

DEFS = """<defs>
<linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a4a50"/><stop offset=".5" stop-color="#2a2a2f"/><stop offset="1" stop-color="#151518"/></linearGradient>
<linearGradient id="mh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1a1a1d"/><stop offset=".45" stop-color="#5b5b62"/><stop offset="1" stop-color="#1a1a1d"/></linearGradient>
<linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9e9ee"/><stop offset="1" stop-color="#a7a7ae"/></linearGradient>
<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9d9da4"/><stop offset=".5" stop-color="#f4f4f7"/><stop offset="1" stop-color="#9d9da4"/></linearGradient>
<linearGradient id="a" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="ACC1"/><stop offset="1" stop-color="ACC2"/></linearGradient>
<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity=".35"/><stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
<radialGradient id="f" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>
</defs>"""

SHADOW = '<ellipse cx="120" cy="160" rx="78" ry="9" fill="url(#f)"/>'

ART = {
 "tvs-home-theatre": ("#5e5ce6", "#bf5af2", """
<rect x="60" y="148" width="120" height="6" rx="3" fill="url(#mh)"/><path d="M112 132h16l6 16h-28z" fill="url(#m)"/>
<rect x="24" y="30" width="192" height="108" rx="6" fill="#0d0d10" stroke="#3a3a40" stroke-width="2"/>
<rect x="30" y="36" width="180" height="96" rx="3" fill="url(#a)"/>
<path d="M30 110c40-30 80 10 120-20s50-20 60-25v67H30z" fill="#000" opacity=".25"/>
<path d="M30 36h180L120 132H30z" fill="url(#g)" opacity=".5"/>"""),
 "headphones-audio": ("#ff9f0a", "#ff375f", """
<path d="M62 112V96a58 58 0 0 1 116 0v16" fill="none" stroke="url(#m)" stroke-width="12" stroke-linecap="round"/>
<path d="M62 96a58 58 0 0 1 116 0" fill="none" stroke="#6a6a72" stroke-width="2" opacity=".6"/>
<rect x="44" y="96" width="38" height="58" rx="16" fill="url(#m)"/><rect x="50" y="104" width="26" height="42" rx="11" fill="url(#a)"/>
<rect x="158" y="96" width="38" height="58" rx="16" fill="url(#m)"/><rect x="164" y="104" width="26" height="42" rx="11" fill="url(#a)"/>
<rect x="52" y="104" width="10" height="30" rx="5" fill="url(#g)"/><rect x="166" y="104" width="10" height="30" rx="5" fill="url(#g)"/>"""),
 "computing-gaming": ("#0a84ff", "#64d2ff", """
<path d="M28 146h184l-10 10H38z" fill="url(#sh)"/><rect x="104" y="146" width="32" height="3" rx="1.5" fill="#7c7c84"/>
<rect x="44" y="40" width="152" height="104" rx="8" fill="url(#s)"/><rect x="52" y="48" width="136" height="88" rx="3" fill="#0b0b0e"/>
<rect x="56" y="52" width="128" height="80" rx="2" fill="url(#a)"/>
<path d="M56 52h128L96 132H56z" fill="url(#g)" opacity=".45"/>"""),
 "tablets-ereaders": ("#30d158", "#64d2ff", """
<rect x="66" y="22" width="108" height="140" rx="12" fill="url(#m)" transform="rotate(-8 120 92)"/>
<rect x="74" y="30" width="92" height="124" rx="5" fill="url(#a)" transform="rotate(-8 120 92)"/>
<path d="M74 30h92l-60 124H74z" fill="url(#g)" opacity=".45" transform="rotate(-8 120 92)"/>
<g transform="rotate(-8 120 92)" fill="#fff" opacity=".7"><rect x="84" y="44" width="50" height="5" rx="2.5"/><rect x="84" y="56" width="70" height="4" rx="2"/><rect x="84" y="66" width="62" height="4" rx="2"/><rect x="84" y="76" width="68" height="4" rx="2"/></g>"""),
 "phones-wearables": ("#ff375f", "#ff9f0a", """
<rect x="70" y="20" width="70" height="140" rx="14" fill="url(#m)"/><rect x="75" y="25" width="60" height="130" rx="10" fill="url(#a)"/>
<rect x="95" y="29" width="20" height="6" rx="3" fill="#0b0b0e"/><path d="M75 25h60l-30 130H75z" fill="url(#g)" opacity=".45"/>
<rect x="160" y="70" width="22" height="90" rx="8" fill="#2b2b30"/>
<rect x="148" y="90" width="46" height="54" rx="13" fill="url(#mh)"/><rect x="153" y="95" width="36" height="44" rx="9" fill="#0b0b0e"/>
<circle cx="171" cy="117" r="13" fill="none" stroke="url(#a)" stroke-width="5"/><rect x="194" y="108" width="4" height="12" rx="2" fill="#6a6a72"/>"""),
 "smart-home": ("#64d2ff", "#5e5ce6", """
<ellipse cx="96" cy="140" rx="54" ry="14" fill="#1c1c20"/>
<path d="M42 140V96a54 54 0 0 1 108 0v44a54 14 0 0 1-108 0z" fill="url(#m)"/>
<path d="M42 100a54 54 0 0 1 108 0" fill="none" stroke="#fff" stroke-opacity=".08" stroke-width="18"/>
<ellipse cx="96" cy="74" rx="34" ry="8" fill="url(#a)" opacity=".85"/><path d="M52 92c6-26 24-40 44-42" stroke="url(#g)" stroke-width="6" fill="none" stroke-linecap="round"/>
<rect x="164" y="88" width="40" height="56" rx="12" fill="url(#s)"/><circle cx="184" cy="108" r="11" fill="#0b0b0e"/><circle cx="184" cy="108" r="5" fill="url(#a)"/><circle cx="187" cy="105" r="1.6" fill="#fff"/>"""),
 "coffee-machines": ("#ff9f0a", "#bf5af2", """
<rect x="56" y="24" width="128" height="34" rx="8" fill="url(#m)"/><rect x="56" y="54" width="34" height="96" fill="url(#m)"/><rect x="150" y="54" width="34" height="96" fill="url(#m)"/>
<rect x="52" y="146" width="136" height="10" rx="4" fill="url(#mh)"/><rect x="90" y="58" width="60" height="8" fill="#141417"/>
<rect x="96" y="66" width="48" height="10" rx="3" fill="url(#sh)"/><rect x="144" y="68" width="26" height="6" rx="3" fill="#1b1b1e"/>
<path d="M98 108h44l-4 34h-36z" fill="#f2f2f5"/><path d="M142 114h6a6 6 0 0 1 0 14h-8" fill="none" stroke="#f2f2f5" stroke-width="4"/>
<ellipse cx="120" cy="108" rx="22" ry="4" fill="#6b3d1e"/><path d="M114 80v22M126 80v22" stroke="url(#a)" stroke-width="3" stroke-linecap="round"/>
<circle cx="72" cy="40" r="6" fill="url(#a)"/><rect x="60" y="28" width="120" height="6" rx="3" fill="url(#g)"/>"""),
 "kitchen-appliances": ("#ff453a", "#ff9f0a", """
<rect x="58" y="34" width="124" height="116" rx="30" fill="url(#m)"/><rect x="58" y="34" width="124" height="40" rx="20" fill="#1a1a1e"/>
<rect x="88" y="48" width="64" height="12" rx="6" fill="#0b0b0e"/><text x="120" y="58" font-family="Arial" font-size="10" fill="url(#a)" text-anchor="middle" font-weight="700">200°</text>
<rect x="70" y="84" width="100" height="56" rx="14" fill="#232327" stroke="#3a3a40"/><rect x="106" y="104" width="28" height="8" rx="4" fill="url(#sh)"/>
<rect x="64" y="38" width="20" height="100" rx="10" fill="url(#g)" opacity=".5"/><rect x="58" y="146" width="124" height="6" rx="3" fill="url(#a)" opacity=".6"/>"""),
 "vacuums-floorcare": ("#bf5af2", "#0a84ff", """
<path d="M150 22l-40 112" stroke="url(#sh)" stroke-width="8" stroke-linecap="round"/>
<rect x="132" y="16" width="30" height="16" rx="8" fill="url(#m)" transform="rotate(20 147 24)"/>
<rect x="128" y="34" width="34" height="56" rx="14" fill="url(#a)" transform="rotate(20 145 62)"/><rect x="134" y="40" width="10" height="42" rx="5" fill="url(#g)" transform="rotate(20 145 62)"/>
<path d="M62 136h70a12 12 0 0 1 12 12v4H62a8 8 0 0 1 0-16z" fill="url(#m)"/><rect x="66" y="148" width="74" height="4" rx="2" fill="url(#a)"/>"""),
 "hair-beauty-tools": ("#ff375f", "#bf5af2", """
<circle cx="96" cy="72" r="44" fill="url(#a)"/><circle cx="96" cy="72" r="26" fill="#141417"/><circle cx="96" cy="72" r="18" fill="none" stroke="#fff" stroke-opacity=".2" stroke-width="6"/>
<path d="M60 52a44 44 0 0 1 40-24" stroke="url(#g)" stroke-width="10" fill="none" stroke-linecap="round"/>
<rect x="132" y="60" width="62" height="26" rx="13" fill="url(#mh)"/><rect x="190" y="62" width="10" height="22" rx="4" fill="#2a2a2f"/>
<path d="M88 112h20l-6 44h-12z" fill="url(#m)"/><rect x="92" y="122" width="12" height="4" rx="2" fill="url(#a)"/>"""),
 "personal-care": ("#64d2ff", "#30d158", """
<rect x="98" y="122" width="44" height="34" rx="10" fill="url(#s)"/><ellipse cx="120" cy="124" rx="18" ry="4" fill="#8e8e95"/>
<rect x="110" y="40" width="20" height="88" rx="10" fill="url(#sh)"/><rect x="113" y="20" width="14" height="24" rx="6" fill="url(#s)"/>
<rect x="114" y="22" width="12" height="10" rx="3" fill="url(#a)"/><circle cx="120" cy="78" r="5" fill="url(#a)"/><rect x="117" y="92" width="6" height="16" rx="3" fill="#bdbdc4"/>"""),
 "air-climate": ("#64d2ff", "#0a84ff", """
<rect x="92" y="20" width="56" height="134" rx="28" fill="url(#s)"/><rect x="100" y="34" width="40" height="96" rx="20" fill="#1b1b1f"/>
<g stroke="url(#a)" stroke-width="3" stroke-linecap="round" opacity=".9"><path d="M108 50h24M106 62h28M106 74h28M106 86h28M106 98h28M106 110h28M108 122h24"/></g>
<rect x="96" y="24" width="14" height="120" rx="7" fill="url(#g)" opacity=".7"/><circle cx="120" cy="142" r="4" fill="url(#a)"/>"""),
 "cameras": ("#ff9f0a", "#ff453a", """
<rect x="40" y="60" width="160" height="92" rx="14" fill="url(#m)"/><path d="M84 60l10-18h52l10 18z" fill="url(#m)"/>
<rect x="40" y="60" width="160" height="16" rx="8" fill="#fff" opacity=".06"/>
<circle cx="120" cy="106" r="38" fill="#0e0e11" stroke="url(#mh)" stroke-width="6"/><circle cx="120" cy="106" r="24" fill="url(#a)"/><circle cx="120" cy="106" r="12" fill="#0b0b0e"/>
<circle cx="110" cy="96" r="6" fill="#fff" opacity=".45"/><rect x="156" y="70" width="28" height="12" rx="4" fill="url(#sh)"/><circle cx="62" cy="72" r="5" fill="url(#a)"/>"""),
 "furniture-bedding": ("#30d158", "#ffd60a", """
<rect x="34" y="86" width="172" height="50" rx="16" fill="url(#a)"/><rect x="48" y="58" width="144" height="44" rx="14" fill="url(#a)" opacity=".85"/>
<rect x="24" y="88" width="30" height="54" rx="12" fill="url(#a)"/><rect x="186" y="88" width="30" height="54" rx="12" fill="url(#a)"/>
<rect x="58" y="96" width="56" height="26" rx="10" fill="#fff" opacity=".18"/><rect x="126" y="96" width="56" height="26" rx="10" fill="#fff" opacity=".18"/>
<rect x="40" y="140" width="8" height="14" rx="2" fill="#3a3a40"/><rect x="192" y="140" width="8" height="14" rx="2" fill="#3a3a40"/><rect x="48" y="60" width="144" height="12" rx="6" fill="url(#g)"/>"""),
 "fashion-footwear": ("#ff375f", "#ff9f0a", """
<path d="M28 142c0-14 8-20 20-22 20-3 40-18 52-40 6-8 16-8 22-2 10 10 22 16 40 18 26 3 50 14 50 40v6H28z" fill="url(#s)"/>
<path d="M28 142h184v8a6 6 0 0 1-6 6H34a6 6 0 0 1-6-6z" fill="url(#a)"/>
<path d="M92 92c14 6 26 8 40 6M98 82c12 6 24 8 36 6" stroke="#6e6e75" stroke-width="3" fill="none" stroke-linecap="round"/>
<path d="M140 100c16 10 40 14 58 18" stroke="url(#a)" stroke-width="6" fill="none" stroke-linecap="round"/>"""),
 "toys-lego": ("#ffd60a", "#ff453a", """
<g><rect x="50" y="100" width="80" height="48" rx="4" fill="#ff453a"/><rect x="58" y="90" width="18" height="12" rx="3" fill="#ff6961"/><rect x="82" y="90" width="18" height="12" rx="3" fill="#ff6961"/><rect x="106" y="90" width="18" height="12" rx="3" fill="#ff6961"/></g>
<g><rect x="110" y="62" width="80" height="48" rx="4" fill="#0a84ff"/><rect x="118" y="52" width="18" height="12" rx="3" fill="#409cff"/><rect x="142" y="52" width="18" height="12" rx="3" fill="#409cff"/><rect x="166" y="52" width="18" height="12" rx="3" fill="#409cff"/></g>
<g><rect x="132" y="112" width="56" height="36" rx="4" fill="#ffd60a"/><rect x="140" y="102" width="16" height="12" rx="3" fill="#ffe55c"/><rect x="164" y="102" width="16" height="12" rx="3" fill="#ffe55c"/></g>
<rect x="50" y="100" width="80" height="8" fill="url(#g)"/><rect x="110" y="62" width="80" height="8" fill="url(#g)"/>"""),
 "large-appliances": ("#64d2ff", "#5e5ce6", """
<rect x="72" y="14" width="96" height="144" rx="10" fill="url(#sh)"/><rect x="72" y="62" width="96" height="3" fill="#7c7c84"/>
<rect x="152" y="26" width="5" height="28" rx="2.5" fill="url(#m)"/><rect x="152" y="74" width="5" height="40" rx="2.5" fill="url(#m)"/>
<rect x="84" y="28" width="26" height="16" rx="3" fill="#0b0b0e"/><rect x="87" y="31" width="20" height="10" rx="2" fill="url(#a)"/>
<rect x="76" y="18" width="16" height="136" rx="8" fill="url(#g)" opacity=".6"/>"""),
}

for slug, (c1, c2, body) in ART.items():
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 180" role="img" aria-label="">{DEFS.replace("ACC1", c1).replace("ACC2", c2)}{SHADOW}{body}</svg>'
    (OUT / f"{slug}.svg").write_text(svg)
print(len(ART), "drawings")
