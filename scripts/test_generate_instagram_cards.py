# -*- coding: utf-8 -*-
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import generate_instagram_cards as gic


def test_all_fonts_load():
    for name in gic.FONTS:
        font = gic.load_font(name, 40)
        assert font is not None


def test_missing_font_raises_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(gic, "FONT_DIR", str(tmp_path))
    try:
        gic.load_font("black_han_sans", 40)
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "BlackHanSans-Regular.ttf" in str(e)


def test_find_word_returns_known_word():
    word = gic.find_word("컴백")
    assert word["kr"] == "컴백"
    assert word["rom"] == "keom-baek"
    assert word["en_short"] == "Comeback"
    assert word["cat_en"] == "Idol Essentials"
    assert "comeback" in word["meaning_en"].lower()


def test_find_word_raises_with_suggestions_for_typo():
    try:
        gic.find_word("컴벡")  # typo of 컴백
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError as e:
        assert "컴벡" in str(e)


def test_find_word_raises_for_nonsense_input():
    try:
        gic.find_word("zzz-not-a-real-word-zzz")
        assert False, "expected WordNotFoundError"
    except gic.WordNotFoundError as e:
        assert "not found" in str(e).lower()
