"""stage_site.py — build/refresh the public showcase site (mediaeater-zines-2026)
from the issues built in images-work.

RUN FROM the images-work repo root, with its venv:
    .venv/bin/python .claude/skills/zine/scripts/stage_site.py            # all issues
    .venv/bin/python .claude/skills/zine/scripts/stage_site.py 03         # only issue 03

Prereq: each issue is built + printed under mashups/<band>/issue<NN>/ with its
print/ package (cover.png, page_*.png, colophon.png, print/cover/COVER_SIDE_B.tif,
print/<iss>_press.pdf, print/SPEC.txt, print/FULL_LAYOUT.pdf — i.e. zine.py build
+ zine_print.py + zine_coverposter.py have been run).

Writes per-issue assets into ~/Projects/mediaeater-zines-2026:
  covers/NN.jpg           web jpg of cover.png (maxw 1600)
  posters/NN.jpg          web jpg of print/cover/COVER_SIDE_B.tif (the poster, maxw 2000)
  pdfs/<TITLE>_issueNN.pdf  the 24pp BOOKLET reader: zine_print.booklet_plan ordered
                          (cover · 12 plates · 4 dispersed COLOUR_LEAVES spreads ·
                          colophon + white blanks), each page rendered NO-BLEED at the
                          7.875x10.5 trim @150ppi, THEN the whole-object FULL_LAYOUT
                          (cover panels + poster + booklet grid, 3pp) appended via
                          ghostscript so the poster + full layout are visible in the
                          reader itself (27pp total). **This is NOT the plain 14pp
                          cover+12+colophon reader (mashups/.../<BAND>_issueNN.pdf) —
                          do not substitute it or you strip the coloured spreads.**
  press/NN_press.pdf      direct copy of print/<iss>_press.pdf (press proof, with bleed)
  specs/NN.txt            direct copy of print/SPEC.txt
  layouts/NN.pdf          direct copy of print/FULL_LAYOUT.pdf (whole-object: poster + cover panels)

To fix ONE issue, run just its entry (loop over a single key). After staging,
regenerate print.html with gen_print_html.py, update index.html cards + README,
then: git -C ~/Projects/mediaeater-zines-2026 add -A && commit && push origin main.

Provenance: recovered 2026-06-28 from a session scratchpad and preserved here (and in
the site repo's scripts/) so the pipeline survives. Issue 11 (Clinic) added to ISSUES
below — it was originally staged by a separate stage_clinic.py.
"""
import sys, os, shutil, re, subprocess
_a = sys.argv; sys.argv = ["x"]
sys.path.insert(0, ".claude/skills/zine/scripts")
import zine_print as zp
sys.argv = _a
from PIL import Image

GS = shutil.which("gs")     # ghostscript: append the full layout to the reader PDF
SITE = os.path.expanduser("~/Projects/mediaeater-zines-2026")
PANEL = (7.875, 10.5); PPI = 150
ISSUES = {
    "01": ("zine_bloc_party", "issue01", "Bloc_Party_issue01.pdf"),
    "02": ("zine_auction", "issue02", "NOT_YOURS_issue02.pdf"),
    "03": ("zine_rubber", "issue03", "RUBBER_issue03.pdf"),
    "04": ("zine_people-in-cars", "issue04", "PEOPLE_IN_CARS_issue04.pdf"),
    "05": ("zine_camera", "issue05", "CAMERA_OPTICS_issue05.pdf"),
    "06": ("zine_marquee-ifc", "issue06", "IFC_MARQUEE_issue06.pdf"),
    "07": ("zine_jackie60", "issue07", "JACKIE_60_PART_I_issue07.pdf"),
    "08": ("zine_jackie60", "issue08", "JACKIE_60_PART_II_issue08.pdf"),
    "09": ("zine_stezaker", "issue09", "COLLAGE_THE_CUT_issue09.pdf"),
    "10": ("zine_broken_social_scene", "issue10", "BROKEN_SOCIAL_SCENE_issue10.pdf"),
    "11": ("zine_clinic", "issue11", "CLINIC_issue11.pdf"),
}
os.makedirs(f"{SITE}/posters", exist_ok=True)
os.makedirs(f"{SITE}/layouts", exist_ok=True)
pw, ph = int(PANEL[0]*PPI), int(PANEL[1]*PPI)

# optional positional arg(s) = issue key(s) to (re)stage; default = all
ONLY = [k for k in sys.argv[1:] if not k.startswith("-")]


def save_reader(pages, reader, layout_src):
    """Reader PDF = the booklet, with the whole-object FULL_LAYOUT (cover panels +
    poster + booklet grid) appended so the poster + layout are visible in the reader
    itself. Falls back to booklet-only if ghostscript or the layout is unavailable."""
    if GS and os.path.exists(layout_src):
        tmp = os.path.join(os.path.dirname(reader), f".{os.path.basename(reader)}.booklet.pdf")
        pages[0].save(tmp, "PDF", resolution=float(PPI), save_all=True, append_images=pages[1:])
        subprocess.run([GS, "-q", "-dNOPAUSE", "-dBATCH", "-dAutoRotatePages=/None",
                        "-sDEVICE=pdfwrite", f"-sOutputFile={reader}", tmp, layout_src], check=True)
        os.remove(tmp)
        return True
    pages[0].save(reader, "PDF", resolution=float(PPI), save_all=True, append_images=pages[1:])
    return False


def web_jpg(src, dst, maxw=1600, q=86):
    im = Image.open(src).convert("RGB")
    if im.width > maxw:
        im = im.resize((maxw, int(im.height*maxw/im.width)))
    im.save(dst, "JPEG", quality=q, optimize=True)


def render_page(nm, idir):
    if nm == "cover":
        return zp.place_fill(Image.open(f"{idir}/cover.png"), PANEL, bleed=0).resize((pw, ph))
    if nm == "colophon":
        c = Image.open(f"{idir}/colophon.png").convert("RGB")
        s = min(pw/c.width, ph/c.height); c = c.resize((int(c.width*s), int(c.height*s)))
        bg = Image.new("RGB", (pw, ph), (252, 252, 252)); bg.paste(c, ((pw-c.width)//2, (ph-c.height)//2))
        return bg
    if nm.startswith("CBLANK"):
        ci = int(nm.split("_")[1]) - 1
        return Image.new("RGB", (pw, ph), zp.COLOUR_LEAVES[ci % len(zp.COLOUR_LEAVES)])
    if nm.startswith("BLANK"):
        return Image.new("RGB", (pw, ph), (252, 252, 252))
    return zp.place_fill(Image.open(f"{idir}/{nm}.png"), PANEL, bleed=0).resize((pw, ph))


for nn, (band, iss, pdfname) in ISSUES.items():
    if ONLY and nn not in ONLY:
        continue
    idir = f"mashups/{band}/{iss}"
    web_jpg(f"{idir}/cover.png", f"{SITE}/covers/{nn}.jpg")
    web_jpg(f"{idir}/print/cover/COVER_SIDE_B.tif", f"{SITE}/posters/{nn}.jpg", maxw=2000)
    plates = sorted(p[:-4] for p in os.listdir(idir) if re.match(r"page_\d+\.png$", p))
    plan = zp.booklet_plan(plates, int(nn))
    pages = [render_page(nm, idir) for nm in plan]
    shutil.copy(f"{idir}/print/FULL_LAYOUT.pdf", f"{SITE}/layouts/{nn}.pdf")
    appended = save_reader(pages, f"{SITE}/pdfs/{pdfname}", f"{idir}/print/FULL_LAYOUT.pdf")
    shutil.copy(f"{idir}/print/{iss}_press.pdf", f"{SITE}/press/{nn}_press.pdf")
    shutil.copy(f"{idir}/print/SPEC.txt", f"{SITE}/specs/{nn}.txt")
    tail = "+fulllayout" if appended else ""
    print(f"issue {nn} ({iss}): cover+poster+readerPDF({len(pages)}pp{tail})+press+spec+layout staged")
print("STAGED" + (f" (only {','.join(ONLY)})" if ONLY else ""))
