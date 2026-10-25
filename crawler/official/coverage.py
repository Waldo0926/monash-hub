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
import difflib
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
    # Printing on campus and in the library: short pages that fell under
    # MIN_LENGTH in the walk, and a question students ask every semester.
    "https://www.monash.edu.my/its/our-services/students/printing-services": {"keep": True},
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

#: A 200 whose title says it is not there.
NOT_FOUND = re.compile(r"^\s*(?:404\b|page not found\b|page cannot be found\b)", re.IGNORECASE)

#: A near-empty page read before the cleaner stopped falling back to the
#: whole body: its "text" is the cookie banner.
COOKIE_ONLY = re.compile(r"^\s*(?:this (?:web)?site |we )uses? cookies\b", re.IGNORECASE)

#: Shorter than this and a page is a menu or a landing tile. 450 also dropped
#: real short answers (printing, opening hours); the crawl itself stops at 200.
MIN_LENGTH = 250
LEAVE_OUT = re.compile(
    r"staff-resources|intranet|login|/contact|contact-us|/archive|/accordion|"
    r"first-semester/week|/media/|/publications/|faculty-contacts|m-pass/account|"
    r"monash-malaysia-agents|student-barometer|httpsisphelpdesk|/staff(?:[-/]|$)|"
    # Redirects to online.monash.edu, which sits behind a Cloudflare bot
    # challenge: every fetch is refused, and getting past it is not ours to do.
    r"/support/monash-online|"
    # One page per research supervisor, and single career events: people and
    # dates, not guidance. The project and events overviews stay.
    r"third-year-research-project/|/career-events/|"
    # Partner programs belong to monash-abroad-tracker; Prato is Monash's own.
    r"program-search/(?!.*prato)|program-search$|"
    # Not guidance: the site search, the 404 page, feedback forms, tracking
    # and verification files the sitemaps list.
    # A feedback form sits at the top of a section; ".../results/feedback" is
    # how to get feedback on a mark and stays.
    r"(?:^|/)(?:search|page-not-found|analytics)(?:/|$)|^/(?:[^/]+/)?feedback$|google-tag-manager|"
    r"/google[0-9a-f]*\.html$|\.txt$|\.xml$|"
    # The rest of a whole-site sitemap that is not for students or parents:
    # research groups, news and seminars, staff lists and profiles, alumni
    # and student testimonials, job ads, conference and campaign microsites,
    # and the CMS's own fragments and drafts. The 2026-10-25 build added about
    # 890 of these, filed under enrolment or support by default.
    # A school's research section, not a page about research rules deeper in
    # (students/support/disability/services/research).
    # Research scholarships are for applicants and stay.
    r"^/(?:[^/]+/)?research(?:/(?!support-and-scholarships)|$)|"
    r"(?:^|/)(?:researchers-say|our-research|research-areas|research-centres?|"
    r"research-facilities|monashrise|all-staff|our-people|our-staff|staff-directory|"
    r"our-alumni|testimonials|what-they-say|gallery|mockup|for-review|"
    r"nested-content|right-hand-side-bar|rhs-modules|engage-with-us)(?:/|$)|"
    r"^/(?:rhs2|paced|mipo|net-zero-future-centre|optical-imaging|future-conversations|"
    r"life-capsule|education-excellence)(?:/|$)|^/about/career(?:/|$)|"
    # Conferences and expos. Not every segment with a year in it: "fees-2027"
    # is exactly what a parent is looking for.
    r"(?:^|/)(?:[a-z-]*-)?(?:expo|icamr|tbcg|eepm)[a-z0-9-]*(?:/|$)|"
    r"(?:^|/)[^/]*(?:symposium|colloquium|mockup|spotlight|staff-only)[^/]*(?:/|$)|"
    # Research platforms and centres with sites of their own, a staging copy,
    # and sidebar fragments ("rhs" is the right-hand side bar).
    r"^/(?:mdp|jcsmhs/gph|ohse/information-test)(?:/|$)|(?:^|/)rhs(?:-[^/]*)?(?:/|$)|-custom/|"
    # Event sign-ups and their thank-you pages, recruitment events for agents
    # and applicants, and the COVID-19 notices of 2020-22.
    r"(?:^|/)thank(?:-[^/]*)?(?:/|$)|^/(?:application-day|agent-familiarisation-visit|"
    r"infoday[^/]*|sir-john-monash-lecture|event-attendance|covid19-updates|mena)(?:/|$)|"
    # Single research projects and PhD positions, employer and staff pages.
    r"undergraduate-research-opportunity/|phd-studentship|(?:^|/)employers(?:/|$)|"
    r"welcome-new-staff|organisational-chart|library-exhibitions|"
    r"[^/]*testimonial[^/]*(?:/|$)",
    re.IGNORECASE,
)

#: Discovery answers that say an address is gone or has moved. Any other
#: failure - a 403, a timeout - says nothing about the page, and a page the
#: coverage list already has stays on it: the 2026-10-25 build dropped five
#: Malaysia eExam pages because the walk was refused on them that night.
GONE = re.compile(r"\b(?:404|410)\b|soft 404|redirect", re.IGNORECASE)
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
    # A credit transfer moves credit, not the student.
    (r"(?<!credit )(?<!credit-)transfer", ["转专业", "转课程", "转校区", "转学"],
     ["transfer", "course transfer"]),
    (r"campus.transfer|clayton.transfer|intercampus|campus-transfer",
     ["转校区", "澳洲校区", "马来西亚校区"], ["campus transfer"]),
    (r"\bfees?\b|payment|\bpay\b", ["学费", "缴费"], ["fees"]),
    (r"refund", ["退款", "退费"], ["refund"]),
    (r"discount", ["学费折扣", "优惠"], ["discount"]),
    (r"instal+ment", ["分期付款", "分期"], ["instalment"]),
    (r"\bepf\b", ["公积金", "EPF 提取"], ["epf"]),
    (r"\bsst\b", ["服务税", "SST"], ["sst"]),
    (r"e-invoic", ["电子发票"], ["e-invoice"]),
    (r"encumbrance", ["欠费限制", "欠费"], ["encumbrance"]),
    (r"fee statement", ["学费账单", "账单"], ["fee statement"]),
    (r"loan|hecs|fee-help|sa-help", ["贷款"], ["loan"]),
    (r"scholarship|award", ["奖学金"], ["scholarship"]),
    (r"visa|student pass|emgs|immigration", ["签证", "学生签证", "学生准证"], ["visa"]),
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
    # "12 credit points" is a unit's size, not credit for earlier study.
    (r"credit(?![- ]?points?)|exemption|advanced standing", ["学分减免", "学分转换"], ["credit"]),
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


# Titles that say nothing on their own. A list of guides with five pages called
# "Eligibility" - for a travel grant, three New Colombo Plan programs and a loan -
# cannot be read, so these, and any title two pages share, get their section.
GENERIC_TITLES = {
    "eligibility", "assessment criteria", "faq", "faqs", "frequently asked questions",
    "important", "what you should know", "overview", "introduction", "testimonials",
    "bursaries", "information session", "how to apply", "contact", "resources", "forms",
}
SCHOOLS = {
    "business": "School of Business", "it": "School of IT", "science": "School of Science",
    "engineering": "School of Engineering", "pharmacy": "School of Pharmacy",
    "sass": "School of Arts and Social Sciences",
    "medicine": "Jeffrey Cheah School of Medicine and Health Sciences",
}
_ACRONYMS = {"os", "help", "it", "faq", "faqs", "pg", "ug", "uhs", "isp", "emgs", "mum", "csds",
             "murpa", "gip", "aas", "ssaf", "usi", "tfn", "csp", "wam", "gpa", "mai"}


_SMALL = {"and", "of", "for", "to", "in", "the", "re"}


def _humanise(segment: str) -> str:
    # "course-maps2" is Monash's second page of that name, not "Maps2".
    words = re.sub(r"[-_,]+", " ", re.sub(r"\d+$", "", segment)).split()
    out = " ".join(
        w.upper() if w.lower() in _ACRONYMS
        else w.lower() if i and w.lower() in _SMALL
        else w.capitalize()
        for i, w in enumerate(words)
    )
    return out.replace("OS HELP", "OS-HELP").replace("re Enrol", "re-enrol")


def section(url: str) -> str:
    """What part of the site a page sits in: the school, or its parent page."""
    path = [p for p in urlparse(url).path.strip("/").split("/") if p]
    if (found := SCHOOLS.get(path[0].lower() if path else "")) and "monash.edu.my" in url:
        return found
    return _humanise(path[-2]) if len(path) >= 2 else ""


def _sentence_case(title: str) -> str:
    """'WHAT YOU SHOULD KNOW' -> 'What you should know'; mixed case is left alone."""
    letters = [c for c in title if c.isalpha()]
    if len(letters) > 4 and all(c.isupper() for c in letters):
        return title[:1] + title[1:].lower()
    return title


def disambiguate(rows: list[dict], others: list[str]) -> None:
    """Give a generic or shared title its section, in place."""
    suffix = " (Monash Malaysia)"
    def base(title: str) -> str:
        return title[: -len(suffix)] if title.endswith(suffix) else title
    # Shared means the whole title: "Timetables (Monash Malaysia)" is already
    # told apart from "Timetables" by its campus.
    counts: dict[str, int] = {}
    for title in [*(r["title"] for r in rows), *others]:
        counts[title.lower()] = counts.get(title.lower(), 0) + 1
    for row in rows:
        plain = base(row["title"])
        tail = row["title"][len(plain):]
        generic = plain.lower() in GENERIC_TITLES
        if generic or counts.get(row["title"].lower(), 0) > 1:
            # Only a generic heading is shouted; names and acronyms keep their case.
            plain = _sentence_case(plain) if generic else plain
            where = section(row["url"])
            if where and where.lower() not in plain.lower():
                plain = f"{plain} - {where}"
        row["title"] = plain + tail

    # Still shared - one school, several programs with a page each: name the
    # program, and the level where the address gives it.
    counts = {}
    for row in rows:
        counts[row["title"].lower()] = counts.get(row["title"].lower(), 0) + 1
    for row in rows:
        if counts[row["title"].lower()] < 2:
            continue
        plain = base(row["title"])
        tail = row["title"][len(plain):]
        path = [p for p in urlparse(row["url"]).path.strip("/").split("/") if p]
        own = _humanise(path[-1])
        if own.lower() in plain.lower() and len(path) >= 2:
            own = _humanise(path[-2])
        lowered = "/".join(path).lower()
        level = ("postgraduate" if "postgrad" in lowered
                 else "undergraduate" if "undergrad" in lowered else "")
        if level and level not in own.lower():
            own = f"{own}, {level}"
        row["title"] = f"{plain} ({own}){tail}"


def _about_malaysia(url: str) -> bool:
    return "monash.edu.my" in url or "malaysia" in urlparse(url).path.lower()


def category(url: str) -> str:
    path = urlparse(url).path.lower()
    if "/policy-bank/" in path:
        return "academic-rules"
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
    if any(k in path for k in ("/fees", "/finance", "fee-payment", "financial-assistance",
                               "scholarship", "/government-support", "principal-dates",
                               "/dates", "jompay")):
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


#: The pages that change with the semester: admin, fees, applying, visas.
SEMESTERLY = re.compile(
    r"/students/admin|student-services/(student-admin|international|financial)|"
    r"/finance|/fees|/study/apply|/admissions/|/student-pass",
    re.IGNORECASE,
)


def tier(url: str) -> str:
    if re.search(r"dates|timetable", url):
        return "dynamic"
    if re.search(r"polic|procedure|glossary|rules", url):
        return "stable"
    # With every page of both sites listed, re-reading the faculty, library
    # and support pages every two days would keep the crawler busy all day
    # for text that changes a few times a year.
    return "medium" if SEMESTERLY.search(url) else "stable"


def _same_text_kept(text: str, kept: dict[str, dict]) -> str | None:
    """The kept page with this text, if any: length within 3 per cent and the
    opening (discovery keeps the first 300 characters) nearly the same."""
    head = re.sub(r"\s+", " ", text[:300]).strip()
    for url, page in kept.items():
        size = page.get("len") or 0
        if not size or abs(size - len(text)) > 0.03 * size:
            continue
        other = re.sub(r"\s+", " ", page.get("head") or "").strip()
        if other and difflib.SequenceMatcher(None, head, other).ratio() >= 0.85:
            return url
    return None


def build(pages: list[dict], texts: dict[str, dict], existing: list,
          known: dict[str, str] | None = None, previous: tuple = ()) -> list[dict]:
    """Seed rows from discovered pages; ``existing`` is the hand-picked list,
    ``known`` maps the addresses already in seeds_coverage.py to their slugs;
    ``previous`` is that file's rows, kept when discovery could not read them."""
    listed_urls = {seed.url.rstrip("/").lower() for seed in existing}
    listed_hashes = {t["hash"] for t in texts.values() if t.get("hand_picked") and t.get("hash")}
    taken = {seed.slug for seed in existing}
    kept: dict[str, dict] = {}
    by_hash: dict[str, str] = {}

    known = known or {}
    known_urls = {u.rstrip("/").lower() for u in known}

    def rank(url: str) -> tuple:
        # The same text at two addresses: keep the shorter one, and of the
        # study-abroad mirrors the /outbound address students are given. An
        # address already in seeds_coverage.py wins, so a page keeps its slug
        # and its translations from one build to the next; then a student
        # services page over the same text in the prospective-student section
        # (Malaysia's sibling discount is at both).
        path = urlparse(url).path.lower()
        services = path.startswith(("/student-services/", "/students/"))
        return (url.lower() not in known_urls, not services, len(url), "/overseas" in url)

    spelled: dict[str, str] = {}  # lower-cased address -> the spelling kept
    for page in pages:
        url = page["url"].rstrip("/")
        # Monash serves an address in any capitalisation, and the sitemaps
        # list some twice; it is one page.
        if page.get("status") != 200 or url.lower() in listed_urls or url.lower() in spelled:
            continue
        if LEAVE_OUT.search(urlparse(url).path) or NOT_FOUND.match(page.get("title") or ""):
            continue
        if page.get("len", 0) < MIN_LENGTH and not page.get("keep"):
            continue
        if page.get("len", 0) < 450 and COOKIE_ONLY.match(page.get("head") or ""):
            continue
        digest = page.get("hash")
        if digest and digest in listed_hashes:
            continue
        if digest and digest in by_hash:
            other = by_hash[digest]
            if rank(url) >= rank(other):
                continue
            del kept[other]
            del spelled[other.lower()]
        if digest:
            by_hash[digest] = url
        kept[url] = page
        spelled[url.lower()] = url

    rows = []
    moved: dict[str, str] = {}  # live address -> the slug it had at its old one
    failed = {page["url"].rstrip("/").lower(): page for page in pages
              if page.get("status") != 200 or page.get("error")}
    seen = {page["url"].rstrip("/").lower() for page in pages}
    for slug, url, title, cat, tag_list, refresh, applies_to in previous:
        key = url.rstrip("/").lower()
        page = failed.get(key)
        if url.lower() in spelled or url.lower() in listed_urls \
                or LEAVE_OUT.search(urlparse(url).path):
            continue
        if page is None:
            # Not in any sitemap and linked from nowhere discovery walked - the
            # five Malaysia eExam pages - but production holds its text, so
            # it is still there; a 404 on the next crawl takes it down.
            stored = texts.get(url.rstrip("/")) or {}
            if key in seen or len(stored.get("text") or "") < MIN_LENGTH:
                continue
            # The same page at the address the sitemap gives now: IT's
            # Course-Offered/postgraduates pages moved under current-students.
            # Hashes cannot tell: the stored one was made by an older
            # extractor and covers the title too. The text can.
            # The live address is kept, under the old slug so the page keeps
            # its translations: Monash lists the old one nowhere and may drop
            # its redirect. Unless the live one is a school's copy of a central
            # page - Malaysia's student-admin re-enrol page, not the School of
            # Science's.
            twin = _same_text_kept(stored.get("text") or "", kept)
            if twin and SCHOOL.search(twin) and not SCHOOL.search(url):
                del kept[twin]
                del spelled[twin.lower()]
            elif twin:
                if twin not in moved and twin.lower() not in known_urls:
                    moved[twin] = slug
                continue
        elif GONE.search(f"{page.get('status')} {page.get('error') or ''}"):
            continue
        spelled[url.lower()] = url
        rows.append({
            "slug": slug, "url": url, "title": title, "category": cat, "tags": tuple(tag_list),
            "tier": refresh, "applies_to": applies_to, "depth": 9, "prio": 0,
            "reason": "kept: listed before, not read this time",
        })
        taken.add(slug)
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
        slug = moved.get(url)
        if slug and slug not in taken:
            taken.add(slug)
        else:
            slug = slugify(url, taken, known)
        rows.append({
            "slug": slug, "url": url, "title": title, "category": cat,
            "tags": tags(title, url, cat), "tier": tier(url), "applies_to": applies_to,
            "reason": reason, "depth": page.get("depth", 9), "prio": page.get("prio", 0),
        })

    disambiguate(rows, [seed.title for seed in existing])

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
    parser.add_argument("--previous", metavar="PATH",
                        help="the seeds_coverage.py that production runs (default: this "
                             "checkout's). Its slugs are kept, and its rows that discovery "
                             "could not read stay listed - pass main's copy when rebuilding "
                             "on a branch that already holds a rebuild")
    args = parser.parse_args()
    if args.export_texts:
        export_texts(args.export_texts)
        return

    from crawler.official.seeds import SEEDS
    from crawler.official.seeds_coverage import COVERAGE

    current = COVERAGE
    if args.previous:
        import runpy

        COVERAGE = runpy.run_path(args.previous)["COVERAGE"]

    generated = {row[0] for row in current}
    hand_picked = [seed for seed in SEEDS if seed.slug not in generated]
    pages: list[dict] = []
    for path in args.inputs:
        with open(path, encoding="utf-8") as handle:
            pages += json.load(handle)
    texts = {}
    if args.texts:
        with open(args.texts, encoding="utf-8") as handle:
            texts = json.load(handle)
    rows = build(pages, texts, hand_picked, {row[1]: row[0] for row in COVERAGE}, COVERAGE)
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
