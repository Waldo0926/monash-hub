"""An answer for both campuses puts Malaysia first (app/search/router.py)."""
from app.knowledge.faq_seed import FAQ_SEEDS
from app.search.router import malaysia_first


def test_malaysia_paragraph_goes_first_in_both_languages():
    assert malaysia_first("Australia: withdraw in WES. Malaysia: check Principal Dates.") == [
        "Malaysia: check Principal Dates.", "Australia: withdraw in WES."]
    assert malaysia_first("澳大利亚：通过 WES 退选。马来西亚：看 Principal Dates。") == [
        "马来西亚：看 Principal Dates。", "澳大利亚：通过 WES 退选。"]


def test_an_answer_for_one_campus_is_left_alone():
    text = "Apply through the online form within two working days."
    assert malaysia_first(text) == [text]
    assert malaysia_first("Malaysia: only this campus.") == ["Malaysia: only this campus."]


def test_a_sentence_before_the_two_campuses_stays_first():
    assert malaysia_first("It depends on the campus. Australia: a. Malaysia: b.") == [
        "It depends on the campus.", "Malaysia: b.", "Australia: a."]


def test_every_two_campus_faq_in_the_seed_is_reordered_without_losing_text():
    both = [item.answer for item in FAQ_SEEDS if "Australia: " in item.answer and "Malaysia: " in item.answer]
    assert len(both) >= 7
    for answer in both:
        parts = malaysia_first(answer)
        campuses = [part for part in parts if part.startswith(("Malaysia: ", "Australia: "))]
        assert [part.split(":")[0] for part in campuses] == ["Malaysia", "Australia"]
        assert sorted(" ".join(parts).split()) == sorted(answer.split())      # same words, new order
