# ============================================
# FILE DI TEST/DEBUG - NON PER PRODUZIONE
# Creato da: Claude Code
# Data: 2026-10-15
# Scopo: verificare la conversione PDF -> MediaWiki di indice (link interni)
#        e tabelle (tabelle zcsTable con intestazione)
# ============================================
"""Tests for table-of-contents and table handling in the PDF extractor."""

from pathlib import Path

import fitz
import pytest

from app.models.dto import ExtractedData
from app.services.convert_wikitext import to_wikitext
from app.services.extract_pdf import _match_toc_entry, extract_pdf

TOC_LINES = [
    "1. Panoramica" + "." * 60 + "3",
    "3.2 Configurazione generale (31500)" + "." * 40 + "5",
    "5.3 Messaggi più frequenti e cosa fare" + "." * 30 + "22",
]

TABLE_ROWS = [
    ["Codice", "Titolo finestra", "Uso"],
    ["31500", "Configurazione generale", "Impostazione una tantum"],
    ["31504", "Portatili", "Anagrafica"],
]


def _draw_table(page: fitz.Page, top: float) -> None:
    """Draw a bordered 3x3 table with text starting at the given y."""
    col_x = [72, 152, 342, 522]
    row_h = 20
    bottom = top + row_h * len(TABLE_ROWS)
    for i in range(len(TABLE_ROWS) + 1):
        y = top + i * row_h
        page.draw_line((col_x[0], y), (col_x[-1], y))
    for x in col_x:
        page.draw_line((x, top), (x, bottom))
    for r, row in enumerate(TABLE_ROWS):
        for c, cell in enumerate(row):
            page.insert_text((col_x[c] + 4, top + r * row_h + 14), cell, fontsize=10)


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Build a two-page PDF: a TOC page and a page with a heading and a table."""
    doc = fitz.open()

    toc_page = doc.new_page()
    toc_page.insert_text((72, 100), "Indice", fontsize=16)
    for i, line in enumerate(TOC_LINES):
        # Slightly larger than body text, as in the real manual
        toc_page.insert_text((72, 130 + i * 18), line, fontsize=11)

    body = doc.new_page()
    body.insert_text((72, 100), "1. Panoramica", fontsize=16)
    for i in range(6):
        body.insert_text((72, 130 + i * 14), f"Testo normale riga {i}", fontsize=10)
    _draw_table(body, top=250)
    body.insert_text((72, 340), "Testo dopo la tabella", fontsize=10)

    path = tmp_path / "sample.pdf"
    doc.save(str(path))
    doc.close()
    return path


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("1. Panoramica ....... 3", (1, "1. Panoramica")),
        ("3.10 Listini e prezzi......14", (2, "3.10 Listini e prezzi")),
        ("5.3 Cosa fare. . . . . 22", (2, "5.3 Cosa fare")),
        ("Appendice ........ 30", (1, "Appendice")),
        ("Vedi capitolo 3... 4", None),
        ("Testo normale con numero 12", None),
    ],
)
def test_match_toc_entry(line: str, expected: tuple[int, str] | None) -> None:
    assert _match_toc_entry(line) == expected


def test_toc_becomes_entries(sample_pdf: Path) -> None:
    text = extract_pdf(sample_pdf, job_id="test").text

    assert "TOC_ENTRY1:1. Panoramica" in text
    assert "TOC_ENTRY2:3.2 Configurazione generale (31500)" in text
    assert "TOC_ENTRY2:5.3 Messaggi più frequenti e cosa fare" in text
    # No dot leaders or merged TOC headings survive
    assert "....." not in text
    assert not any(
        line.startswith("HEADING") and "Panoramica" in line and "3.2" in line
        for line in text.splitlines()
    )


def test_table_markers_in_place(sample_pdf: Path) -> None:
    lines = extract_pdf(sample_pdf, job_id="test").text.splitlines()

    start = lines.index("TABLE_START")
    end = lines.index("TABLE_END")
    assert lines[start + 1] == "HEADER_ROW:Codice | Titolo finestra | Uso"
    assert (
        lines[start + 2]
        == "ROW:31500 | Configurazione generale | Impostazione una tantum"
    )
    assert lines[start + 3] == "ROW:31504 | Portatili | Anagrafica"
    assert end == start + 4

    # The table sits between the body text and the text that follows it
    body = next(i for i, line in enumerate(lines) if "Testo normale riga 5" in line)
    after = next(i for i, line in enumerate(lines) if "Testo dopo la tabella" in line)
    assert body < start
    assert after > end
    # Cell text is not duplicated outside the table
    assert sum("Portatili" in line for line in lines) == 1


def test_wikitext_output(sample_pdf: Path) -> None:
    wikitext, _ = to_wikitext(extract_pdf(sample_pdf, job_id="test"))

    assert "* [[#1. Panoramica|1. Panoramica]]" in wikitext
    assert (
        "** [[#3.2 Configurazione generale (31500)|3.2 Configurazione generale (31500)]]"
        in wikitext
    )
    assert '{| class="zcsTable"' in wikitext
    assert "! Titolo finestra" in wikitext
    assert "| Configurazione generale" in wikitext


@pytest.fixture
def layout_pdf(tmp_path: Path) -> Path:
    """Build a PDF with a shaded table header, smaller table text, a repeated
    footer and a real heading low on the page (cases from the ATON manual)."""
    doc = fitz.open()
    for page_no in range(3):
        page = doc.new_page()  # A4-like 595x842
        page.insert_text(
            (72, 100), f"Paragrafo normale pagina {page_no}", fontsize=10.6
        )
        page.insert_text((72, 830), f"Manuale ATON - pagina {page_no + 1}", fontsize=8)

    page = doc[0]
    # Shaded header row: its fill rectangle must not split the columns
    page.draw_rect(fitz.Rect(72, 150, 522, 170), color=None, fill=(0.1, 0.2, 0.4))
    _draw_table(page, top=150)
    # Long body paragraph: same size as the dominant body text
    page.insert_text((72, 300), "Testo lungo del corpo " * 4, fontsize=10.6)
    # Real heading starting inside the bottom 70pt band
    page.insert_text((72, 785), "6.2 Elenco ad albero", fontsize=13)

    path = tmp_path / "layout.pdf"
    doc.save(str(path))
    doc.close()
    return path


def test_layout_edge_cases(layout_pdf: Path) -> None:
    lines = extract_pdf(layout_pdf, job_id="test").text.splitlines()

    # No spurious empty columns from the shaded header
    assert "HEADER_ROW:Codice | Titolo finestra | Uso" in lines
    # Table text is smaller, but body text must not become a heading
    assert not any(
        line.startswith("HEADING") and "Testo lungo" in line for line in lines
    )
    # Heading near the bottom is kept, the repeated footer is dropped
    assert any(
        line.startswith("HEADING") and "6.2 Elenco ad albero" in line for line in lines
    )
    assert not any("Manuale ATON - pagina" in line for line in lines)


def _write(page: fitz.Page, x: float, y: float, text: str, **kwargs) -> None:
    """Write one line with Helvetica ("hebo" for bold) at 10.6pt by default."""
    kwargs.setdefault("fontsize", 10.6)
    kwargs.setdefault("fontname", "helv")
    page.insert_text((x, y), text, **kwargs)


@pytest.fixture
def prose_pdf(tmp_path: Path) -> Path:
    """Build a PDF with a cover, wrapped paragraphs, bold words and lists."""
    doc = fitz.open()

    cover = doc.new_page()
    _write(cover, 72, 300, "Guida operativa", fontsize=28)
    _write(cover, 72, 340, "Versione 05/10/2026", fontsize=13)

    page = doc.new_page()
    _write(page, 72, 100, "1. Panoramica", fontsize=16)
    # Paragraph wrapped on two rows, with a bold word followed by a comma
    _write(page, 72, 130, "La procedura collega Teseo con ")
    _write(page, 231, 130, "ATON", fontname="hebo")
    _write(page, 258, 130, ", che gli agenti usano")
    _write(page, 72, 143, "durante il giro.")
    # Numbered list
    _write(page, 72, 214, "1. Configurazione generale")
    _write(page, 72, 228, "2. Portatili")
    # Bullets, the second one nested
    _write(page, 72, 260, "• primo punto")
    _write(page, 90, 274, "– sotto punto")
    _write(page, 72, 300, "3.1 Ordine consigliato", fontsize=13)
    for i in range(3):
        _write(page, 72, 330 + i * 14, f"Riga di testo normale numero {i}.")

    path = tmp_path / "prose.pdf"
    doc.save(str(path))
    doc.close()
    return path


def test_prose_layout(prose_pdf: Path) -> None:
    extracted = extract_pdf(prose_pdf, job_id="test")
    lines = extracted.text.splitlines()
    wikitext, _ = to_wikitext(extracted)

    # Cover lines are emphasized text, not headings
    assert "'''Guida operativa'''" in lines
    assert not any(
        line.startswith("HEADING") and "Guida operativa" in line for line in lines
    )
    # The largest real heading becomes the top wiki level
    assert "== 1. Panoramica ==" in wikitext
    assert "=== 3.1 Ordine consigliato ===" in wikitext
    # Wrapped rows are one paragraph; bold kept; no space before the comma
    assert (
        "La procedura collega Teseo con '''ATON''', che gli agenti usano "
        "durante il giro." in wikitext
    )
    # Lists, with nesting from the indentation
    assert "# Configurazione generale\n# Portatili" in wikitext
    assert "* primo punto\n** sotto punto" in wikitext


@pytest.mark.parametrize(
    ("markers", "expected"),
    [
        # A list continuing on the next page keeps wiki numbering
        (
            ["LIST_ITEM:n:1:1:uno", "", "# Page 2", "LIST_ITEM:n:1:2:due"],
            "# uno\n# due",
        ),
        # A list resumed at 3 needs explicit HTML numbers
        (
            [
                "LIST_ITEM:n:1:3:tre",
                "LIST_ITEM:b:2::sotto",
                "LIST_ITEM:n:1:4:quattro",
            ],
            '<ol>\n<li value="3">tre\n<ul>\n<li>sotto\n</li></ul>\n</li>\n'
            '<li value="4">quattro\n</li></ol>',
        ),
    ],
)
def test_list_rendering(markers: list[str], expected: str) -> None:
    wikitext, _ = to_wikitext(ExtractedData(text="\n".join(markers)))
    assert expected in wikitext


def test_table_cell_styles(tmp_path: Path) -> None:
    """Bold/italic inside body cells is kept; header cells stay plain."""
    doc = fitz.open()
    page = doc.new_page()
    col_x, top, row_h = [72, 200, 522], 150, 20
    for i in range(3):
        page.draw_line((col_x[0], top + i * row_h), (col_x[-1], top + i * row_h))
    for x in col_x:
        page.draw_line((x, top), (x, top + 2 * row_h))
    _write(page, 76, top + 14, "Campo", fontname="hebo")
    _write(page, 204, top + 14, "Effetto", fontname="hebo")
    _write(page, 76, top + 34, "Tipo", fontname="hebo")
    _write(page, 204, top + 34, "Solo i clienti ")
    _write(page, 270, top + 34, "con classificazione", fontname="hebo")
    path = tmp_path / "styled_table.pdf"
    doc.save(str(path))
    doc.close()

    lines = extract_pdf(path, job_id="test").text.splitlines()
    assert "HEADER_ROW:Campo | Effetto" in lines
    assert "ROW:'''Tipo''' | Solo i clienti '''con classificazione'''" in lines
