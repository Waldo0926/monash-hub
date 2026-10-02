"""Turn discovered pages into ``seeds_coverage.py``.

    python -m crawler.official.coverage discover_my.json discover_fac.json \
        discover_ab.json discover.json extra.json \
        --texts texts.json --out crawler/official/seeds_coverage.py

The inputs are ``crawler.official.discover`` output. ``--texts`` is the page
text the crawler has stored (``python -m crawler.official.coverage --export-texts
texts.json``, run where the database is), which is what the campus of a
monash.edu page is decided from - see ``crawler/official/scope.py``. A page with
no stored text yet keeps the campus of the site it is on until the next run.

What is left out, and why:

* pages under ~450 characters - landing pages that only link elsewhere;
* the same text at two addresses, or the text of a page ``seeds.py`` already
  lists;
* contact, login and staff pages, application agents, surveys;
* individual exchange programs and partner lists - monash-abroad-tracker's data;
  the Hub points to Monash's program search (Monash's own Prato programs stay).

Order matters: the official translation pass runs in seed order, so Monash
Malaysia's pages come first, then the rest - the Hub is read mostly by Monash
Malaysia students.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.parse import urlparse

from crawler.official.scope import ALL, AUSTRALIA, MALAYSIA, scope

#: Pages found by searching rather than walking, with anything to override.
EXTRA: dict[str, dict] = {
    "https://www.monash.edu/admissions/study-options/internal-transfer": {},
    "https://www.monash.edu/admissions/study-options/internal-transfer/quick-reference-guide": {},
    "https://www.monash.edu.my/study/apply/internal-course-transfer": {},
    "https://www.monash.edu/engineering/current-students/enrolment-and-re-enrolment"
    "/course-information/malaysia-clayton-transfer": {},
    "https://www.monash.edu.my/business/current/frequently-asked-questions/faq-course-transfer": {},
    "https://www.monash.edu.my/sass/current/undergraduate/frequent-asked-questions"
    "/faq-campus-transfer-exchange": {},
    "https://www.monash.edu/business/current-students/course-transfers": {},
    "https://www.monash.edu/mada/current-students/planning-your-course/course-transfer": {},
    "https://www.monash.edu.my/student-services/student-admin/graduations/graduations-FAQ": {},
    "https://www.monash.edu.my/sass/current/undergraduate/frequent-asked-questions"
    "/faq-course-completion-graduation": {},
    "https://www.monash.edu.my/business/current/frequently-asked-questions"
    "/faq-course-completion-n-graduation": {},
    "https://www.monash.edu/business/current-students/global-study-experiences"
    "/global-summer-and-winter-programs": {},
    "https://www.monash.edu.my/science/current/undergraduate/exchange-program": {},
    "https://www.monash.edu.my/sass/current/undergraduate/monash-study-abroad-program": {},
}

#: Where reading the text gets it wrong, the decision and why. Most are pages
#: that name Malaysia as a *destination* - a semester there, an information
#: session held there - which says nothing about who the page is for.
SCOPE_OVERRIDES: dict[str, tuple[str, str]] = {
    "https://www.monash.edu/students/admin":
        ("australia", "the Australian student admin hub; Malaysia has its own"),
    "https://www.monash.edu/study-abroad/overseas/financial-information/monash-abroad-travel-grant/f":
        ("australia", "Malaysia appears as a destination"),
    "https://www.monash.edu/study-abroad/outbound/information-sessions":
        ("australia", "Malaysia appears as a destination"),
    "https://www.monash.edu/students/support/international/before-leaving/webinars":
        ("australia", "sessions held in Malaysia for students coming to Australia"),
    "https://www.monash.edu/students/support/international/before-leaving/home-country-sessions":
        ("australia", "sessions held in Malaysia for students coming to Australia"),
    "https://www.monash.edu/students/support/disability/services/testimonials":
        ("australia", "a student's exchange to Malaysia, not a Malaysian service"),
    "https://www.monash.edu/students/admin/graduations/after/documents/ahegs":
        ("australia", "an Australian statement; the page does not say Malaysia issues it"),
}

MIN_LENGTH = 450
LEAVE_OUT = re.compile(
    r"staff-resources|intranet|login|/contact|contact-us|/archive|/accordion|"
    r"first-semester/week|/media/|/publications/|faculty-contacts|m-pass/account|"
    r"monash-malaysia-agents|student-barometer|httpsisphelpdesk|/staff(?:[-/]|$)|"
    # Partner programs belong to monash-abroad-tracker; Prato is Monash's own.
    r"program-search/(?!.*prato)|program-search$",
    re.IGNORECASE,
)
CATEGORY_ORDER = ["assessment", "enrolment", "graduation", "fees-dates", "international",
                  "academic-rules", "exchange", "support", "malaysia"]
SCHOOL = re.compile(r"monash\.edu\.my/(business|it|science|engineering|pharmacy|sass|medicine)/",
                    re.IGNORECASE)

TOPIC_TAGS: list[tuple[str, list[str], list[str]]] = [
    # (pattern on the title and last path segment, Chinese tags, English tags)
    (r"(?<!under)(?<!post)graduat", ["毕业"], ["graduation"]),
    (r"apply.to.graduate|/graduations/apply", ["申请毕业"], ["apply to graduate"]),
    (r"ceremon|graduation day|graduations/guides", ["毕业典礼"], ["ceremony"]),
    (r"all.dates|graduation dates", ["毕业时间", "毕业典礼日期"], ["graduation dates"]),
    (r"course.completion|eligib", ["完成学业", "毕业资格"], ["course completion"]),
    (r"transfer", ["转专业", "转课程", "转校区", "转学"], ["transfer", "course transfer"]),
    (r"campus.transfer|clayton.transfer|intercampus|campus-transfer",
     ["转校区", "澳洲校区", "马来西亚校区"], ["campus transfer"]),
    (r"\bfees?\b|payment|\bpay\b", ["学费", "缴费"], ["fees"]),
    (r"refund", ["退款", "退费"], ["refund"]),
    (r"discount", ["学费折扣", "优惠"], ["discount"]),
    (r"loan|hecs|fee-help|sa-help", ["贷款"], ["loan"]),
    (r"scholarship|award", ["奖学金"], ["scholarship"]),
    (r"visa|student pass|emgs|immigration", ["签证", "学生准证"], ["visa"]),
    (r"insurance|oshc|health cover", ["保险"], ["insurance"]),
    (r"enrol", ["选课", "注册"], ["enrolment"]),
    (r"re-enrol", ["重新注册"], ["re-enrol"]),
    (r"census", ["截止日"], ["census"]),
    (r"intermission|leave", ["休学"], ["intermission"]),
    (r"discontinu|losing your place", ["退学"], ["discontinue"]),
    (r"\bexams?\b|eexam|final assessment", ["考试", "期末考试"], ["exam"]),
    (r"assessment", ["考核"], ["assessment"]),
    (r"\bresults?\b|\bgrades?\b|\bmarks?\b", ["成绩"], ["results"]),
    (r"special.consideration", ["特殊考虑"], ["special consideration"]),
    (r"timetable|allocate", ["课表"], ["timetable"]),
    (r"\bdates?\b|calendar|holiday", ["日期", "校历"], ["dates"]),
    (r"transcript|record|official document|letter", ["成绩单", "官方文件"], ["transcript"]),
    (r"personal.details|change of name", ["个人信息"], ["personal details"]),
    (r"misconduct|integrity|plagiari|cheat", ["学术不端", "作弊"], ["misconduct"]),
    (r"complain|grievance|appeal|review", ["投诉", "申诉"], ["complaint", "appeal"]),
    (r"progress|exclu", ["学业进度"], ["academic progress"]),
    (r"counsel|wellbeing|wellness|mental", ["心理咨询", "心理健康"], ["counselling"]),
    (r"disabilit", ["残障支持"], ["disability"]),
    (r"\bcareers?\b|\bjobs?\b|employ|working on|work rights", ["工作", "就业"], ["work"]),
    (r"housing|accommodation", ["住宿", "租房"], ["accommodation"]),
    (r"exchange|abroad|overseas|intercampus|global (summer|winter)|summer program|"
     r"winter program|short.term",
     ["交换", "海外学习"], ["exchange"]),
    (r"credit|exemption|advanced standing", ["学分减免"], ["credit"]),
    (r"policy|policies|procedure", ["政策", "规定"], ["policy"]),
    (r"global summer|summer program",
     ["暑期项目", "Global Summer Program"], ["global summer program"]),
    (r"global winter|winter program",
     ["寒期项目", "Global Winter Program"], ["global winter program"]),
    (r"intercampus|semester.in.australia",
     ["校区交换", "Global Intercampus Program"], ["intercampus"]),
    (r"\busi\b|\btfn\b|tax file|chessn|commonwealth|\bcsp\b",
     ["澳洲政府资助"], ["government support"]),
    (r"study load|overload|underload|full-time|part-time", ["学习负荷", "全日制"], ["study load"]),
    (r"summer|winter|november", ["夏季", "冬季"], ["summer", "winter"]),
    (r"cross-institutional|another institution|complementary",
     ["跨校修课"], ["cross-institutional"]),
    (r"honours", ["荣誉学位"], ["honours"]),
    (r"double degree", ["双学位"], ["double degree"]),
    (r"connect|enquir", ["学生服务中心"], ["monash connect"]),
    (r"id card|student id|idcard", ["学生证"], ["student id"]),
    (r"parking|transport", ["停车", "交通"], ["parking"]),
    (r"safety|security", ["安全"], ["safety"]),
    (r"library", ["图书馆"], ["library"]),
    (r"it services|wifi|email|account", ["校园网", "账号"], ["it"]),
]

BASE_TAGS = {"graduation": (["graduation"], ["毕业"]), "exchange": (["exchange"], ["交换"])}


def clean_title(title: str | None, url: str) -> str:
    title = re.sub(
        r"\s*[-|–]\s*(Current Students|Current students|Monash University( Malaysia)?|"
        r"Admissions|Study at Monash|Learning and Teaching.*|Malaysia|Monash Business School)"
        r"\b.*$", "", title or "").strip()
    title = re.sub(r"^(Current Students Home - new)$", "Student services", title)
    title = re.sub(r"^\d\.\s*", "", title)
    if _about_malaysia(url) and "Malaysia" not in title:
        title += " (Monash Malaysia)"
    return title


def _about_malaysia(url: str) -> bool:
    return "monash.edu.my" in url or "malaysia" in urlparse(url).path.lower()


def category(url: str) -> str:
    path = urlparse(url).path.lower()
    if "study-abroad" in path or "global-study" in path \
            or "exchange" in path.rsplit("/", 1)[-1] or "intercampus" in path:
        return "exchange"
    if re.search(r"(?<!under)(?<!post)graduat|course-completion|testamur", path):
        return "graduation"
    if ("transfer" in path or "/enrol" in path or "/timetables" in path or "monplan" in path
            or "credit" in path or "/admissions/" in path
            or ("/study/apply" in path and "fee" not in path)):
        return "enrolment"
    if "examinations-results" in path or "/assessments" in path:
        return "assessment"
    if any(k in path for k in ("/fees", "fee-payment", "financial-assistance", "scholarship",
                               "/government-support", "principal-dates", "/dates", "jompay")):
        return "fees-dates"
    if "international" in path or "student-pass" in path or "insurance" in path:
        return "international"
    if any(k in path for k in ("/admin/policies", "/academic-progress", "/unsatisfactory-progress",
                               "/misconduct", "/complaints", "/academic-integrity")):
        return "academic-rules"
    if SCHOOL.search(url):
        return "enrolment"
    if "/students/" in path or "student-services" in path or "monash.edu.my" in url:
        return "support"
    return "enrolment"


def tags(title: str, url: str, cat: str) -> tuple[str, ...]:
    words = (title + " " + urlparse(url).path.rstrip("/").rsplit("/", 1)[-1].replace("-", " "))
    words = words.lower()
    english: list[str] = []
    chinese: list[str] = []
    for pattern, zh, en in TOPIC_TAGS:
        if re.search(pattern, words):
            chinese += [t for t in zh if t not in chinese]
            english += [t for t in en if t not in english]
    for en, zh in zip(*BASE_TAGS.get(cat, ([], [])), strict=True):
        if en not in english:
            english.insert(0, en)
        if zh not in chinese:
            chinese.insert(0, zh)
    if _about_malaysia(url):
        english.insert(0, "malaysia")
        chinese.append("马来西亚")
    return tuple((english + chinese)[:10])


def slugify(url: str, taken: set[str], known: dict[str, str] | None = None) -> str:
    # A page already registered keeps its slug: it is the key its translations
    # and its links are stored under, and the seed list retires any slug it no
    # longer contains.
    if known and (slug := known.get(url)) and slug not in taken:
        taken.add(slug)
        return slug
    parts = [p for p in urlparse(url).path.strip("/").split("/")
             if p not in ("students", "admin", "support", "student-services", "student-admin",
                          "study-success", "current-students")]
    if not parts:  # a hub such as /students/admin
        parts = urlparse(url).path.strip("/").split("/")
    base = "-".join(parts[-2:]) if len(parts) > 1 else (parts[0] if parts else "home")
    base = re.sub(r"[^a-z0-9-]+", "-", base.lower()).strip("-")[:50].strip("-")
    if "monash.edu.my" in url and not base.startswith("malaysia"):
        base = "malaysia-" + base
    # Short enough that "hash-" + slug fits a 64-character column in the tests.
    base = base[:52].strip("-")
    slug, n = base, 2
    while slug in taken:
        slug, n = f"{base}-{n}", n + 1
    taken.add(slug)
    return slug


def tier(url: str) -> str:
    if re.search(r"dates|timetable", url):
        return "dynamic"
    return "stable" if re.search(r"polic|procedure|glossary|rules", url) else "medium"


def build(pages: list[dict], texts: dict[str, dict], existing: list,
          known: dict[str, str] | None = None) -> list[dict]:
    """Seed rows from discovered pages; ``existing`` is the hand-picked list,
    ``known`` maps the addresses already in seeds_coverage.py to their slugs."""
    listed_urls = {seed.url.rstrip("/") for seed in existing}
    listed_hashes = {t["hash"] for t in texts.values() if t.get("hand_picked") and t.get("hash")}
    taken = {seed.slug for seed in existing}
    kept: dict[str, dict] = {}
    by_hash: dict[str, str] = {}
    for page in pages:
        url = page["url"].rstrip("/")
        if page.get("status") != 200 or url in listed_urls or url in kept:
            continue
        if LEAVE_OUT.search(urlparse(url).path):
            continue
        if page.get("len", 0) < MIN_LENGTH and not page.get("keep"):
            continue
        digest = page.get("hash")
        if digest and digest in listed_hashes:
            continue
        if digest and digest in by_hash:
            # The same text at two addresses: keep the shorter one, and of the
            # study-abroad mirrors the /outbound address students are given.
            other = by_hash[digest]
            if (len(url), "/overseas" in url) >= (len(other), "/overseas" in other):
                continue
            del kept[other]
        if digest:
            by_hash[digest] = url
        kept[url] = page

    rows = []
    for url, page in kept.items():
        title = clean_title(page.get("title"), url)
        cat = category(url)
        stored = texts.get(url) or {}
        applies_to, reason = scope(url, title, stored.get("text"))
        if not stored.get("text") and applies_to == ALL:
            applies_to, reason = AUSTRALIA, "no stored text yet"
        if page.get("applies_to"):
            applies_to, reason = page["applies_to"], "set by hand"
        if url in SCOPE_OVERRIDES:
            applies_to, reason = SCOPE_OVERRIDES[url]
        rows.append({
            "slug": slugify(url, taken, known), "url": url, "title": title, "category": cat,
            "tags": tags(title, url, cat), "tier": tier(url), "applies_to": applies_to,
            "reason": reason, "depth": page.get("depth", 9), "prio": page.get("prio", 0),
        })

    def order(row: dict) -> tuple:
        return (0 if row["applies_to"] == MALAYSIA else 1, -row["prio"],
                1 if SCHOOL.search(row["url"]) else 0,
                CATEGORY_ORDER.index(row["category"]), row["depth"], row["url"])
    return sorted(rows, key=order)


HEADER = '''# ruff: noqa: E501
"""Coverage: the rest of Monash's student-facing pages.

Generated by ``python -m crawler.official.coverage`` from a link walk of the
student sites (``crawler.official.discover``) - edit the rules there, not the
rows here. ``seeds.py`` holds the hand-picked pages; this is the long tail
behind them, Monash Malaysia first because the translation pass runs in seed
order.

Each row: (slug, url, title, category, tags, tier, applies_to). ``applies_to``
comes from the page's own text - see crawler/official/scope.py.
"""

COVERAGE: tuple[tuple[str, str, str, str, tuple[str, ...], str, str], ...] = (
'''


def render(rows: list[dict]) -> str:
    def q(value: str) -> str:
        return json.dumps(value, ensure_ascii=False)
    lines = [HEADER.rstrip("\n")]
    for row in rows:
        tag_list = ", ".join(q(t) for t in row["tags"]) + ("," if len(row["tags"]) == 1 else "")
        lines.append(f"    ({q(row['slug'])},\n     {q(row['url'])},\n"
                     f"     {q(row['title'])}, {q(row['category'])},\n     ({tag_list}),\n"
                     f"     {q(row['tier'])}, {q(row['applies_to'])}),")
    lines.append(")")
    return "\n".join(lines) + "\n"


def export_texts(path: str) -> None:
    """Every stored official page's text, for ``--texts``. Run where the DB is."""
    from app.core.db import SessionLocal
    from app.models.knowledge import OfficialPage
    from sqlalchemy import select

    from crawler.official.seeds import SEEDS
    from crawler.official.seeds_coverage import COVERAGE

    generated = {row[0] for row in COVERAGE}
    hand_picked = {seed.slug for seed in SEEDS if seed.slug not in generated}
    with SessionLocal() as db:
        rows = db.execute(select(OfficialPage.slug, OfficialPage.canonical_url,
                                 OfficialPage.clean_text, OfficialPage.content_hash)).all()
    out = {url.rstrip("/"): {"text": text, "hash": digest, "hand_picked": slug in hand_picked}
           for slug, url, text, digest in rows}
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(out, handle, ensure_ascii=False)
    print(f"{len(out)} pages written to {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build seeds_coverage.py from discovered pages")
    parser.add_argument("inputs", nargs="*", help="discover.py output files")
    parser.add_argument("--texts", help="stored page text, from --export-texts")
    parser.add_argument("--out", default="crawler/official/seeds_coverage.py")
    parser.add_argument("--export-texts", metavar="PATH", help="write stored page text and stop")
    args = parser.parse_args()
    if args.export_texts:
        export_texts(args.export_texts)
        return

    from crawler.official.seeds import SEEDS
    from crawler.official.seeds_coverage import COVERAGE

    generated = {row[0] for row in COVERAGE}
    hand_picked = [seed for seed in SEEDS if seed.slug not in generated]
    pages: list[dict] = []
    for path in args.inputs:
        with open(path, encoding="utf-8") as handle:
            pages += json.load(handle)
    texts = {}
    if args.texts:
        with open(args.texts, encoding="utf-8") as handle:
            texts = json.load(handle)
    rows = build(pages, texts, hand_picked, {row[1]: row[0] for row in COVERAGE})
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(render(rows))
    for row in rows:
        print(f"{row['applies_to']:9} {row['category']:14} {row['slug']:52} {row['reason']}",
              file=sys.stderr)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["applies_to"]] = counts.get(row["applies_to"], 0) + 1
    print(f"{len(rows)} rows written to {args.out}: {counts}", file=sys.stderr)


if __name__ == "__main__":
    main()
