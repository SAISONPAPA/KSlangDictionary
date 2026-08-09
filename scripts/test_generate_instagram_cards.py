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
