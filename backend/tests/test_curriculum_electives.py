"""Synthetic coverage for elective rules and rich-text list references."""
import json

import pytest
from app.handbook.course_parser import parse_course_page, reference_links
from app.handbook.electives import elective_browse


def test_mixed_compulsory_and_elective_part_keeps_links_out_of_mandatory_items():
    content = {
        "course_code": "C3702", "implementation_year": 2026,
        "student_special_notes": '<p>See <a href="https://www.monash.edu/it/electives">approved electives</a></p>',
        "curriculumStructure": {"container": [{
            "title": "Part A. Coursework studies", "credit_points": 24,
            "description": 'Complete this unit and 18 points of electives from Level 4 or Level 5 units. See <a href="/2026/units/FIT4008">reading unit</a>.',
            "relationship": [{"academic_item_code": "FIT5125", "academic_item_type": "subject"}],
        }]},
    }
    html = '<script id="__NEXT_DATA__">' + json.dumps({"props": {"pageProps": {"pageContent": content}}}) + '</script>'
    result = parse_course_page(html, "https://handbook.monash.edu/2026/courses/C3702")
    part = result["containers"][0]
    assert [i["item_code"] for i in part["items"]] == ["FIT5125"]
    assert part["reference_links"][0]["url"] == 'https://handbook.monash.edu/2026/units/FIT4008'
    assert len(result["reference_links"]) == 2
    assert elective_browse(part["title"], part["description"])["levels"] == ["Level 4", "Level 5"]


@pytest.mark.parametrize(('description', 'levels'), [
    ('Electives from levels 4 or 5', ['Level 4', 'Level 5']),
    ('18 points of electives at Level 4 or Level 5', ['Level 4', 'Level 5']),
    ('Electives from Levels 2-4', ['Level 2', 'Level 3', 'Level 4']),
    ('Choose 6 credit points of electives in year 3', []),
])
def test_level_filters_do_not_read_credit_points_as_levels(description, levels):
    assert elective_browse(None, description)["levels"] == levels


def test_free_electives_without_a_fixed_list_are_browsable():
    assert elective_browse('Part E. Free elective studies', None) == {"levels": [], "free": True}
    assert elective_browse('Core studies', 'Complete the units below') is None


def test_unsafe_links_are_discarded_and_references_deduplicate():
    links = reference_links('<a href="javascript:alert(1)">bad</a><a href="data:text/html,bad">bad</a>'
                            '<a href="https://user:pass@example.com">bad</a>'
                            '<a href="//www.monash.edu/list">List &amp; rules</a>'
                            '<a href="https://www.monash.edu/list">Again</a>')
    assert links == [{"url": 'https://www.monash.edu/list', "label": 'List & rules'}]


@pytest.mark.parametrize('href', ['http://[http//example.com/list', 'https://example.com：443/list'])
def test_malformed_reference_urls_do_not_discard_valid_references(href):
    links = reference_links(
        f'<a href="{href}">Malformed upstream link</a>'
        '<a href="https://www.monash.edu/approved">Approved electives</a>'
    )
    assert links == [{'url': 'https://www.monash.edu/approved', 'label': 'Approved electives'}]


def test_reference_links_survive_storage_and_api_serialization(db):
    from app.api.v1.courses import get_course
    from app.handbook.course_repository import upsert_course

    links = [{'url': 'https://www.monash.edu/approved', 'label': 'Approved electives'}]
    record = {
        'course_code': 'C3702', 'academic_year': 2026, 'title': 'Synthetic honours',
        'campuses': [], 'content_hash': 'a' * 64,
        'source_url': 'https://handbook.monash.edu/2026/courses/C3702',
        'reference_links': links,
        'containers': [{'title': 'Coursework studies',
                        'description': '18 points of elective units from Level 4 or Level 5',
                        'reference_links': links}],
    }
    upsert_course(db, record)
    db.commit()
    payload = get_course('C3702', year=2026, db=db, locale=None)
    assert payload['reference_links'] == links
    part = payload['containers'][0]
    assert part['reference_links'] == links
    assert part['elective_browse']['levels'] == ['Level 4', 'Level 5']
    assert part['items'] == []  # browsing must not create mandatory units
