"""2026 Monash Malaysia tuition fees, the baseline for the 2027 change.

The index first read /ugfees and /pgfees on 2026-10-27, when both already showed
2027 fees, so it holds no 2026 version to compare with. Monash no longer hosts
its 2026 fee pages either. The 2026 amounts below were typed in from Monash
Malaysia's own printed 2026 materials, which agents still host:

* ``profile``: University Profile (English), whose last pages are a fee table
  for every course headed "2026 fees". Most rows come from here.
* ``ug``: the 2026 Undergraduate Prospectus (Malaysia), one fee box per course.
* ``pg``: the 2026 Postgraduate Prospectus (Malaysia), the same for postgraduate.

Every row was read on 2026-10-28 and appears in at least one of them. Where two
of them print the same course they agree. A course none of them prices has no
row, and its change is left blank rather than worked out from a guess: the
Bachelor of Computer Science in Artificial Intelligence is one.

From 2028 this file is not needed. Each fee page change is kept in
``official_page_versions``, so the 2027 tables will still be there to compare
with when Monash publishes 2028 fees.
"""
from __future__ import annotations

from dataclasses import dataclass

YEAR = 2026
READ_ON = "2026-10-28"

SOURCES: dict[str, dict[str, str]] = {
    "profile": {
        "title": "Monash University Malaysia University Profile, 2026 fees",
        "url": "https://virtual.sgp1.digitaloceanspaces.com/files/brochures/886/"
               "Monash%20-%20University%20Profile%20(English).pdf",
    },
    "ug": {
        "title": "Monash University Malaysia Undergraduate Prospectus 2026",
        "url": "https://gostralia-gomerica.de/fileadmin/user_upload/gostralia-gozealand/"
               "Universitaeten/Malaysia/monash_malaysia/broschueren/"
               "2026-Monash-University-Malaysia-Bachelor-Brochure.pdf",
    },
    "pg": {
        "title": "Monash University Malaysia Postgraduate Prospectus 2026",
        "url": "https://gostralia-gomerica.de/fileadmin/user_upload/gostralia-gozealand/"
               "Universitaeten/Malaysia/monash_malaysia/broschueren/"
               "2026-Monash-University-Malaysia-Master-Brochure.pdf",
    },
}


@dataclass(frozen=True)
class Previous:
    title: str
    domestic: tuple[int, ...]
    international: tuple[int, ...]
    basis: str
    source: str
    # Only for a title more than one school prices, or a row split by length.
    school: str | None = None
    variant: str | None = None


Y, C = "per_year", "full_course"

ROWS: tuple[Previous, ...] = (
    # Ways in
    Previous("Diploma of Higher Education Studies", (39840, 45120), (46080, 51840), Y, "profile"),
    Previous("Diploma of Business", (35040,), (40320,), Y, "profile"),
    Previous("Monash English", (11600,), (12000,), C, "profile", variant="20 weeks"),
    Previous("Monash English", (6900,), (7600,), C, "profile", variant="10 weeks"),

    # Arts and Social Sciences
    Previous("Bachelor of Arts and Social Sciences", (43200,), (49920,), Y, "profile"),
    Previous("Bachelor of Digital Media and Communication", (43200,), (49920,), Y, "profile"),
    Previous("Bachelor of Arts (Honours)", (43200,), (49920,), Y, "profile"),
    Previous("Master of Communications and Media Studies", (57600,), (66240,), C, "profile"),

    # Business
    Previous("Bachelor of Business and Commerce", (44160,), (51840,), Y, "profile"),
    Previous("Bachelor of Digital Business", (44160,), (51840,), Y, "profile"),
    Previous("Bachelor of Actuarial Analytics", (47040,), (54720,), Y, "profile"),
    Previous("Bachelor of Business and Commerce (Honours)", (44160,), (51840,), Y, "profile"),
    Previous("Bachelor of Business and Commerce and Bachelor of Computer Science",
             (47040,), (54720,), Y, "profile"),
    Previous("Bachelor of Business and Commerce and Bachelor of Digital Media and Communication",
             (44160,), (51840,), Y, "profile"),
    Previous("Master of International Business", (64800,), (74160,), C, "profile"),
    Previous("Master of Digital Business", (64800,), (74160,), C, "profile"),
    Previous("Postgraduate Diploma of Business and Commerce", (42240,), (48000,), Y, "profile"),

    # Engineering. One 2026 fee covers every honours degree, the same as 2027.
    *(Previous(f"Bachelor of {name} Engineering (Honours)", (54720,), (64800,), Y, "profile")
      for name in ("Biomedical", "Chemical", "Civil", "Electrical and Computer Systems",
                   "Materials", "Mechanical", "Robotics and Mechatronics", "Software")),
    Previous("Bachelor of Engineering", (54720,), (64800,), Y, "profile"),
    Previous("Master of Applied Engineering", (57120,), (65280,), C, "profile"),
    Previous("Postgraduate Certificate of Applied Engineering", (28560,), (32640,), C, "pg"),
    Previous("Master of Engineering Science (Research)", (48480,), (54720,), Y, "profile"),

    # Information Technology
    Previous("Bachelor of Computer Science", (47040,), (54720,), Y, "profile"),
    Previous("Bachelor of Computer Science in Data Science", (47040,), (54720,), Y, "ug"),
    Previous("Bachelor of Computer Science (Honours)", (46560,), (54240,), Y, "profile"),
    Previous("Master of Artificial Intelligence", (64080,), (74160,), C, "profile"),
    Previous("Master of Business Information Systems", (64080,), (74160,), C, "profile"),
    Previous("Master of Data Science", (64080,), (74160,), C, "profile"),

    # Medicine and Health Sciences
    Previous("Bachelor of Medical Science and Doctor of Medicine",
             (117600,), (138720,), Y, "profile"),
    Previous("Bachelor of Medical Science (Honours)", (50400,), (60000,), Y, "profile"),
    Previous("Bachelor of Human Nutrition", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Psychology", (43200,), (49920,), Y, "profile"),
    Previous("Bachelor of Psychology and Business", (44160,), (51840,), Y, "profile"),
    Previous("Bachelor of Psychology (Honours)", (44160,), (51360,), Y, "profile"),
    Previous("Bachelor of Health Sciences (Honours)", (44160,), (51360,), Y, "profile"),
    Previous("Master of Biomedical Science", (48480,), (54720,), Y, "profile"),
    Previous("Master of Biotechnology", (48480,), (54720,), Y, "profile"),
    Previous("Master of Clinical Psychology", (79000,), (89000,), C, "profile"),
    Previous("Master of Professional Counselling", (72960,), (83520,), C, "profile"),

    # Pharmacy
    Previous("Bachelor of Pharmacy (Honours)", (60480,), (71040,), Y, "profile"),
    Previous("Bachelor of Pharmaceutical Science", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Pharmaceutical Science (Honours)", (49440,), (58080,), Y, "profile"),
    Previous("Master of Pharmaceutical Science", (48480,), (54720,), Y, "profile"),

    # Science
    Previous("Bachelor of Science", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Applied Data Science", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Food Science and Technology", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Medical Bioscience", (51360,), (60480,), Y, "profile"),
    Previous("Bachelor of Science (Honours)", (51360,), (60480,), Y, "profile"),
    Previous("Master of Science (Research)", (48480,), (54720,), Y, "profile"),
    # The fee page calls it "Master of Science" under the School of Science.
    Previous("Master of Science", (48480,), (54720,), Y, "profile", school="science"),

    # Research degrees every school prices the same.
    Previous("Master of Philosophy", (48480,), (54720,), Y, "profile"),
    Previous("Doctor of Philosophy", (48480,), (54720,), Y, "profile"),
)
