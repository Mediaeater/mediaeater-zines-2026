"""gen_print_html.py — regenerate the showcase site's print.html from the staged
per-issue specs (specs/NN.txt). Run AFTER stage_site.py.

    python .claude/skills/zine/scripts/gen_print_html.py   (no repo-relative paths;
    reads/writes ~/Projects/mediaeater-zines-2026 directly, so cwd doesn't matter)

Builds a black-theme page: one <section> per issue with a links row (full layout ·
poster · press-proof · SPEC) and the SPEC.txt inline in a <pre>. Edit the ISSUES list
below when issues are added/renamed. Preserved 2026-06-28 from a session scratchpad
(see [[mediaeater-zines-site]]).
"""
import os, html
SITE = os.path.expanduser("~/Projects/mediaeater-zines-2026")
ISSUES = [
    ("01", "I", "Bloc Party"), ("02", "II", "Not Yours"), ("03", "III", "Rubber"),
    ("04", "IV", "People in Cars"), ("05", "V", "Camera Optics"), ("06", "VI", "IFC Marquee"),
    ("07", "VII", "Jackie 60 — Part I"), ("08", "VIII", "Jackie 60 — Part II"),
    ("09", "IX", "Collage — The Cut"), ("10", "X", "Broken Social Scene"),
    ("11", "XI", "Clinic"), ("12", "XII", "Depeche Mode"),
]
HEAD = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mediaeater Zines 2026 — Print Instructions</title>
<style>  :root{--red:#e01a24;--ink:#f1efe9;--bg:#000;--mute:#8a8a8a}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:Baskerville,"Baskerville Old Face",Georgia,"Times New Roman",serif}
  header{max-width:1100px;margin:0 auto;padding:60px 32px 10px}
  h1{font-size:40px;letter-spacing:.06em;margin:0;font-weight:600}
  h1 .bar{display:block;width:120px;height:6px;background:var(--red);margin-top:16px}
  .nav{margin:18px 0 0;font-size:15px}
  .nav a,.note a{color:var(--mute);text-decoration:none;border-bottom:1px solid #333}
  .nav a:hover,.note a:hover{color:var(--red);border-color:var(--red)}
  main{max-width:1100px;margin:0 auto;padding:30px 32px 80px}
  .note{color:var(--mute);font-size:15px;line-height:1.5;max-width:820px}
  section{border-top:1px solid #222;padding-top:26px;margin-top:38px}
  h2{font-size:24px;margin:0 0 6px;font-weight:600}
  h2 .iss{color:var(--red);font-size:13px;letter-spacing:.14em;margin-right:10px}
  pre{background:#0c0c0c;border:1px solid #222;border-radius:4px;padding:18px 20px;overflow:auto;
    font:13px/1.5 "SF Mono",Menlo,Consolas,monospace;color:#d7d5cd;white-space:pre-wrap}
</style></head><body>
  <header><h1>Print Instructions<span class="bar"></span></h1>
    <p class="note">Each issue is a mini <strong>quarter-fold</strong> edition: one sheet folds out to a
    full-bleed poster and folds down to the cover, wrapping a saddle-stitched <strong>full-bleed plate
    booklet</strong> (cover &middot; 12 plates &middot; four coloured spreads &middot; colophon, 24pp).
    Colour issues print <strong>coated</strong> (100&nbsp;lb matte); Jackie&nbsp;60 Part&nbsp;I (xerox)
    prints on warm uncoated stock. The spec below is the interior booklet; each issue also links its
    full layout and poster. Confirm exact trim and the CMYK profile with Linco prepress
    (prepress@lincoprinting.com) before final files. Press TIFFs (CMYK, 200&nbsp;ppi, with bleed) are the
    true press files &mdash; available on request.</p>
    <p class="nav"><a href="index.html">&larr; Back to covers</a></p></header>
  <main>
"""
SEC = """    <section id="issue-{nn}">
      <h2><span class="iss">ISSUE {rom}</span> {title}</h2>
      <p class="note"><a href="layouts/{nn}.pdf" target="_blank" rel="noopener">full layout &rarr;</a> &nbsp;&middot;&nbsp; <a href="posters/{nn}.jpg" target="_blank" rel="noopener">poster &rarr;</a> &nbsp;&middot;&nbsp; <a href="press/{nn}_press.pdf" target="_blank" rel="noopener">press-proof PDF &rarr;</a> &nbsp;&middot;&nbsp; <a href="specs/{nn}.txt" target="_blank" rel="noopener">SPEC.txt &rarr;</a></p>
      <pre>{spec}</pre>
    </section>
"""
parts = [HEAD]
for nn, rom, title in ISSUES:
    spec = html.escape(open(f"{SITE}/specs/{nn}.txt").read())
    parts.append(SEC.format(nn=nn, rom=rom, title=html.escape(title), spec=spec))
parts.append("  </main></body></html>\n")
open(f"{SITE}/print.html", "w").write("".join(parts))
print("print.html regenerated from new specs:", len(ISSUES), "issues")
