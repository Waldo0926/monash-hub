"""Bounded programme-link catalogue from the two official Malaysia fee indexes.

Links reviewed 2026-11-03. This is link/identity metadata, not confirmation that
programme pages were fetched or that any intake is open. No prices or page text.
"""

from __future__ import annotations

from app.knowledge.programme_sources import title_key

# (fee-table title, school key, official programme URL)
PROGRAMME_LINKS = (
    (
        "Bachelor of Arts and Social Sciences",
        "arts",
        "https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-arts-social-sciences",
    ),
    (
        "Bachelor of Digital Media and Communication",
        "arts",
        "https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-of-digital-media-and-communication",
    ),
    (
        "Bachelor of Arts (Honours)",
        "arts",
        "https://www.monash.edu.my/study/undergraduate/arts-social-sciences/bachelor-arts-honours",
    ),
    (
        "Bachelor of Business and Commerce",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce",
    ),
    (
        "Bachelor in Actuarial Analytics",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-in-actuarial-analytics",
    ),
    (
        "Bachelor of Digital Business",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-of-digital-business",
    ),
    (
        "Bachelor of Business and Commerce (Honours)",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-honours",
    ),
    (
        "Bachelor of Business and Commerce and Bachelor of Computer Science",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-communication",
    ),
    (
        "Bachelor of Business and Commerce and Bachelor of Digital Media and Communication",
        "business",
        "https://www.monash.edu.my/study/undergraduate/business/bachelor-business-commerce-bachelor-communication",
    ),
    (
        "Bachelor of Computer Science",
        "it",
        "https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-computer-science",
    ),
    (
        "Bachelor of Computer Science in Artificial Intelligence",
        "it",
        "https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-in-artificial-intelligence",
    ),
    (
        "Bachelor of Computer Science in Data Science",
        "it",
        "https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-in-data-science",
    ),
    (
        "Bachelor of Computer Science (Honours)",
        "it",
        "https://www.monash.edu.my/study/undergraduate/information-technology/bachelor-of-computer-science-honours",
    ),
    (
        "Bachelor of Medical Science and Doctor of Medicine",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-medical-science-doctor-medicine",
    ),
    (
        "Bachelor of Psychology",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-psychology",
    ),
    (
        "Bachelor of Psychology and Business",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychological-science-business",
    ),
    (
        "Bachelor of Human Nutrition",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-human-nutrition",
    ),
    (
        "Bachelor of Health Sciences (Honours)",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-of-health-sciences-honours",
    ),
    (
        "Bachelor of Medical Science (Honours)",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-medical-science-honours",
    ),
    (
        "Bachelor of Psychology (Honours)",
        "medicine",
        "https://www.monash.edu.my/study/undergraduate/jeffrey-cheah-school-medicine-health-sciences/bachelor-psychology-honours",
    ),
    (
        "Bachelor of Pharmacy (Honours)",
        "pharmacy",
        "https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-pharmacy",
    ),
    (
        "Bachelor of Pharmaceutical Science",
        "pharmacy",
        "https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-of-pharmaceutical-science",
    ),
    (
        "Bachelor of Pharmaceutical Science (Honours)",
        "pharmacy",
        "https://www.monash.edu.my/study/undergraduate/pharmacy/bachelor-of-pharmaceutical-science-honours",
    ),
    (
        "Bachelor of Science",
        "science",
        "https://www.monash.edu.my/study/undergraduate/science/bachelor-science",
    ),
    (
        "Bachelor of Applied Data Science",
        "science",
        "https://www.monash.edu.my/study/undergraduate/science/bachelor-of-applied-data-science",
    ),
    (
        "Bachelor of Food Science and Technology",
        "science",
        "https://www.monash.edu.my/study/undergraduate/science/bachelor-science-food-science-technology",
    ),
    (
        "Bachelor of Medical Bioscience",
        "science",
        "https://www.monash.edu.my/study/undergraduate/science/bachelor-science-medical-bioscience",
    ),
    (
        "Bachelor of Science (Honours)",
        "science",
        "https://www.monash.edu.my/study/undergraduate/science/bachelor-science-honours",
    ),
    (
        "Master of Communications and Media Studies",
        "arts",
        "https://www.monash.edu.my/study/postgraduate-and-research/arts-social-sciences/master-communications-media-studies",
    ),
    (
        "Doctor of Philosophy",
        "arts",
        "https://www.monash.edu.my/study/postgraduate-and-research/arts-social-sciences/phd",
    ),
    (
        "Postgraduate Diploma in Business and Commerce",
        "business",
        "https://www.monash.edu.my/study/postgraduate-and-research/business/diploma-business-commerce",
    ),
    (
        "Master of International Business",
        "business",
        "https://www.monash.edu.my/study/postgraduate-and-research/business/master-international-business",
    ),
    (
        "Master of Digital Business",
        "business",
        "https://www.monash.edu.my/study/postgraduate-and-research/business/master-of-digital-business",
    ),
    (
        "Master of Philosophy",
        "business",
        "https://www.monash.edu.my/study/postgraduate-and-research/business/master-philosophy",
    ),
    (
        "Doctor of Philosophy",
        "business",
        "https://www.monash.edu.my/study/postgraduate-and-research/business/phd",
    ),
    (
        "Postgraduate Certificate of Applied Engineering",
        "engineering",
        "https://www.monash.edu.my/study/postgraduate-and-research/engineering/postgraduate-certificate-of-applied-engineering",
    ),
    (
        "Master of Applied Engineering",
        "engineering",
        "https://www.monash.edu.my/study/postgraduate-and-research/engineering/master-of-applied-engineering",
    ),
    (
        "Master of Engineering Science (Research)",
        "engineering",
        "https://www.monash.edu.my/study/postgraduate-and-research/engineering/master-engineering-science-research",
    ),
    (
        "Doctor of Philosophy",
        "engineering",
        "https://www.monash.edu.my/study/postgraduate-and-research/engineering/phd",
    ),
    (
        "Master of Artificial Intelligence",
        "it",
        "https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-of-artificial-intelligence",
    ),
    (
        "Master of Business Information Systems",
        "it",
        "https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-business-information-systems",
    ),
    (
        "Master of Data Science",
        "it",
        "https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-of-data-science",
    ),
    (
        "Master of Philosophy",
        "it",
        "https://www.monash.edu.my/study/postgraduate-and-research/information-technology/master-philosophy",
    ),
    (
        "Doctor of Philosophy",
        "it",
        "https://www.monash.edu.my/study/postgraduate-and-research/information-technology/phd",
    ),
    (
        "Master of Biomedical Science",
        "medicine",
        "https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-biomedical-science",
    ),
    (
        "Master of Biotechnology",
        "medicine",
        "https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-biotechnology",
    ),
    (
        "Master of Clinical Psychology",
        "medicine",
        "https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/master-of-clinical-psychology",
    ),
    (
        "Doctor of Philosophy",
        "medicine",
        "https://www.monash.edu.my/study/postgraduate-and-research/medicine-health-sciences/phd",
    ),
    (
        "Master of Pharmaceutical Science",
        "pharmacy",
        "https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/master-of-pharmaceutical-science",
    ),
    (
        "Master of Philosophy",
        "pharmacy",
        "https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/master-of-philosophy",
    ),
    (
        "Doctor of Philosophy",
        "pharmacy",
        "https://www.monash.edu.my/study/postgraduate-and-research/pharmacy/doctor-of-philosophy-phd",
    ),
    (
        "Master of Science",
        "science",
        "https://www.monash.edu.my/study/postgraduate-and-research/science/master-science",
    ),
    (
        "Doctor of Philosophy",
        "science",
        "https://www.monash.edu.my/study/postgraduate-and-research/science/phd",
    ),
    # Eight named destinations linked by the official Engineering directory.
    (
        "Bachelor of Biomedical Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-biomedical-engineering-honours",
    ),
    (
        "Bachelor of Civil Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-civil-engineering",
    ),
    (
        "Bachelor of Chemical Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-chemical-engineering",
    ),
    (
        "Bachelor of Electrical and Computer Systems Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-electrical-and-computer-systems-engineering",
    ),
    (
        "Bachelor of Materials Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-materials-engineering-honours",
    ),
    (
        "Bachelor of Mechanical Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechanical-engineering",
    ),
    (
        "Bachelor of Robotics and Mechatronics Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-engineering-honours-in-mechatronics-engineering",
    ),
    (
        "Bachelor of Software Engineering (Honours)",
        "engineering",
        "https://www.monash.edu.my/study/undergraduate/engineering/bachelor-of-software-engineering-honours",
    ),
)


def source_for(title: str, school: str) -> str | None:
    candidates = {
        url
        for name, faculty, url in PROGRAMME_LINKS
        if title_key(name) == title_key(title) and faculty == school
    }
    return next(iter(candidates)) if len(candidates) == 1 else None
