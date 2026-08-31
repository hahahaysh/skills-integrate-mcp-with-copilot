from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_school_theme_colors_are_used():
    css = (ROOT / "src" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "lime" in css.lower() or "#d9f99d" in css.lower() or "#a3e635" in css.lower()
    assert "#f8fff6" in css.lower() or "#f5fdf3" in css.lower() or "#ffffff" in css.lower()


def test_school_mascot_images_are_included():
    html = (ROOT / "src" / "static" / "index.html").read_text(encoding="utf-8")
    assert "octodex" in html.lower()
    assert "mascot" in html.lower() or "octocat" in html.lower()


def test_background_has_branch_like_pattern():
    css = (ROOT / "src" / "static" / "styles.css").read_text(encoding="utf-8")
    assert "linear-gradient" in css.lower() or "repeating-linear-gradient" in css.lower()
