#!/usr/bin/env python3
import argparse, csv, html, re, sys, time, logging
from urllib.parse import urljoin, urlparse, quote_plus
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# ---------- Config ----------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0 Safari/537.36 BioLabDevOpsCLI/1.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
SKIP_EXTS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip"}
DATA_KEYWORDS = [
    "high-throughput sequencing","high throughput sequencing","next-generation sequencing","ngs",
    "wgs","wes","rna-seq","single-cell","scrna-seq","metagenomics","variant calling",
    "illumina","pacbio","nanopore","10x genomics","chip-seq","atac-seq","long-read",
    "genomic surveillance","pathogen genomics","genomic epidemiology",
    "bam","fastq","vcf","cromwell","wdl","nextflow","snakemake",
    "slurm","hpc","kubernetes","aws batch","gcp pipelines","terra","bioinformatics core"
]
PEOPLE_HINTS = ("people","team","members","personnel","pi","faculty","staff","directory","contact")
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
# common obfuscations
OBF_RXES = [
    re.compile(r"([A-Za-z0-9._%+\-]+)\s*(?:\(|\[|\{)?at(?:\)|\]|\})\s*([A-Za-z0-9.\-]+)\s*(?:\(|\[|\{)?dot(?:\)|\]|\})\s*([A-Za-z]{2,})", re.I),
    re.compile(r"([A-Za-z0-9._%+\-]+)\s+at\s+([A-Za-z0-9.\-]+)\s+dot\s+([A-Za-z]{2,})", re.I),
]
CFEMAIL_RX = re.compile(r"data-cfemail=\"([0-9a-fA-F]+)\"")
MAILTO_RX = re.compile(r'href=["\']mailto:([^"\']+)["\']', re.I)

logging.basicConfig(format="%(message)s", level=logging.INFO)

def cf_decode(hexstr: str) -> str:
    data = bytes.fromhex(hexstr)
    key = data[0]
    return "".join(chr(b ^ key) for b in data[1:])

def build_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.6,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    return session

SESSION = build_session()

def fetch(url, timeout=12):
    try:
        r = SESSION.get(url, timeout=timeout)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
            logging.debug(f"[skip] Non-HTML content at {url} ({content_type})")
            return ""
        return r.text
    except Exception as exc:
        logging.debug(f"[warn] fetch failed for {url}: {exc}")
        return ""

def abs_url(base, href):
    return urljoin(base, href)

def is_binary_link(href: str) -> bool:
    low = href.lower()
    return any(low.endswith(ext) for ext in SKIP_EXTS) or low.startswith("mailto:")

def allowed_scheme(url: str) -> bool:
    return urlparse(url).scheme in ("http", "https", "")

def normalize_obfuscated(text: str):
    t = html.unescape(text)
    for pat, rep in [("[at]","@"),("(at)","@"),("{at}","@"),
                     ("[dot]","."),
                     ("(dot)","."),
                     ("{dot}",".")]:
        t = t.replace(pat, rep)
    return t

def extract_emails(html_text: str):
    results = set()
    if not html_text:
        return []
    # 1) mailto:
    for m in MAILTO_RX.findall(html_text):
        addr = m.split("?")[0].strip()
        if addr:
            results.add(addr)
    # 2) Cloudflare-protected
    for m in CFEMAIL_RX.findall(html_text):
        try: results.add(cf_decode(m))
        except Exception: pass
    # 3) obfuscated "user at domain dot tld"
    t = normalize_obfuscated(html_text)
    for rx in OBF_RXES:
        for u, d, tld in rx.findall(t):
            results.add(f"{u}@{d}.{tld}")
    # 4) normal addresses
    results |= set(EMAIL_RX.findall(t))
    # cleanup
    return sorted(e for e in results if not e.endswith(".png"))

def score_html(text: str):
    if not text: return 0, []
    low = text.lower()
    hits = [kw for kw in DATA_KEYWORDS if kw in low]
    return len(hits), hits

def find_links(soup: BeautifulSoup, base: str, filters):
    out = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]; text = (a.get_text(" ", strip=True) or "").lower()
        if is_binary_link(href):
            continue
        abs_href = abs_url(base, href)
        if not allowed_scheme(abs_href):
            continue
        if filters(abs_href.lower(), text):
            out.add(abs_href)
    return sorted(out)

def looks_like_lab_link(href_low, text_low):
    return any(k in text_low for k in ("lab","group","center","core","laboratory")) or "lab" in href_low

def looks_like_people_link(href_low, text_low):
    return any(h in href_low for h in PEOPLE_HINTS) or any(h in text_low for h in PEOPLE_HINTS)

def crawl_url(url, sleep=0.8):
    time.sleep(sleep)
    html_text = fetch(url)
    soup = BeautifulSoup(html_text, "html.parser") if html_text else None
    return html_text, soup

def crawl_lab_page(url, max_people_pages=6, sleep=0.8, nested_people=True):
    html_text, soup = crawl_url(url, sleep)
    score, matched = score_html(html_text)
    emails = set(extract_emails(html_text))
    pi_guess = ""

    if soup:
        # naive PI guess: look for lab header or explicit PI label
        for h in soup.find_all(["h1","h2","h3"]):
            t = h.get_text(" ", strip=True)
            if " lab" in t.lower():
                pi_guess = t; break
        if not pi_guess:
            for tag in soup.find_all(string=re.compile(r"principal investigator|pi:", re.I)):
                pi_guess = tag.parent.get_text(" ", strip=True)
                break

        if nested_people:
            plist = find_links(soup, url, looks_like_people_link)
            for purl in plist[:max_people_pages]:
                phtml, _ = crawl_url(purl, sleep)
                emails |= set(extract_emails(phtml))

    return score, matched, sorted(emails), pi_guess

def google_linkedin_query(lab, inst):
    q=f'{lab} {inst} principal investigator site:linkedin.com'
    return f"https://www.google.com/search?q={quote_plus(q)}"

def outreach(pi, lab, inst):
    pi = pi or "Dr. [Name]"
    inst = inst or "[Institution]"
    subj = f"DevOps support for {lab} – scalable, reproducible sequencing pipelines"
    body = f"""Hello {pi},

I’ve been reviewing the work of the {lab} at {inst}, especially the group’s use of high-throughput sequencing and large-scale genomic analysis.

I specialize in DevOps for data-intensive biology:
• Reproducible NGS workflows (Nextflow / Snakemake / Cromwell/WDL)
• Running pipelines on AWS/GCP/Kubernetes and/or HPC (SLURM)
• CI/CD, container registries (Docker/Singularity), versioned environments
• Secure data handling (PHI/IRB), storage optimization, cost-aware scaling

Would you be open to a short 12–15 minute chat this week?

Best regards,
Bharath Bhaskar
LinkedIn: https://www.linkedin.com/in/bharathbhaskar99/
Email: bhaskar.bh@northeastern.edu"""
    return subj, body

def main():
    ap = argparse.ArgumentParser(description="Find labs needing DevOps and extract contacts.")
    ap.add_argument("-i","--input", required=True, help="Text file with seed directory URLs (one per line).")
    ap.add_argument("-o","--out", default="leads.csv", help="Output CSV path")
    ap.add_argument("--min-score", type=int, default=2, help="Keep labs with data-signal score >= N")
    ap.add_argument("--people-pages", type=int, default=6, help="Max team/people pages to crawl per lab")
    ap.add_argument("--sleep", type=float, default=0.8, help="Delay between requests (seconds)")
    ap.add_argument("--max-labs", type=int, default=400, help="Safety cap on number of lab links")
    ap.add_argument("--depth", type=int, default=2, help="Crawl depth: 1=directory→lab, 2=+people pages")
    ap.add_argument("--allow-domains", help="Comma list of hostnames to keep (e.g. broadinstitute.org,harvard.edu)")
    ap.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    allow = set([d.strip().lower() for d in (args.allow_domains or "").split(",") if d.strip()])

    # read seed directory/listing pages
    with open(args.input, encoding="utf-8") as f:
        seeds=[ln.strip() for ln in f if ln.strip()]

    seen=set()
    labs=[]
    for seed in seeds:
        logging.info(f"[seed] {seed}")
        html_text = fetch(seed)
        soup = BeautifulSoup(html_text, "html.parser") if html_text else None
        if not soup: 
            continue
        # find linked labs/groups/centers/cores
        for a in soup.find_all("a", href=True):
            name=a.get_text(" ", strip=True)
            if not name or len(name)<3: 
                continue
            if is_binary_link(a["href"]):
                continue
            low=name.lower()
            href_low = a["href"].lower()
            if looks_like_lab_link(href_low, low):
                url = abs_url(seed, a["href"])
                if not allowed_scheme(url):
                    continue
                host = (urlparse(url).hostname or "").lower()
                if allow and not any(host.endswith(h) for h in allow):
                    continue
                if url not in seen:
                    seen.add(url)
                    labs.append((name,url))
                    if len(labs) >= args.max_labs:
                        break
        if len(labs) >= args.max_labs:
            break

    logging.info(f"[info] harvested {len(labs)} candidate lab links")

    # analyze each lab page (+ nested people pages if depth>=2)
    rows=[]
    for name,url in labs:
        score, matched, emails, pi_guess = crawl_lab_page(
            url,
            max_people_pages=args.people_pages,
            sleep=args.sleep,
            nested_people=(args.depth >= 2)
        )
        if score >= args.min_score:
            host=urlparse(url).hostname or ""
            inst=host.split(".")[1].upper() if "." in (host or "") else host
            subj, body = outreach(pi_guess, name, inst)
            rows.append({
                "Lab Name": name,
                "Institution Host": host,
                "Institution (guess)": inst,
                "Lab URL": url,
                "Data-Signal Score": score,
                "Matched Keywords": "; ".join(sorted(set(matched))),
                "PI (guess)": pi_guess,
                "Emails": "; ".join(emails[:20]),
                "PI LinkedIn Search": google_linkedin_query(name, inst),
                "Email Subject": subj,
                "Email Body": body
            })

    # write CSV
    with open(args.out,"w",newline="",encoding="utf-8") as f:
        fieldnames = ["Lab Name","Institution Host","Institution (guess)","Lab URL","Data-Signal Score",
                      "Matched Keywords","PI (guess)","Emails","PI LinkedIn Search","Email Subject","Email Body"]
        w=csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows: w.writerow(r)

    logging.info(f"[done] Wrote {len(rows)} leads → {args.out}")
    if rows:
        logging.info("\nSample outreach:\n-----------------")
        logging.info(rows[0]["Email Subject"])
        logging.info(rows[0]["Email Body"])

if __name__=="__main__":
    sys.exit(main())
