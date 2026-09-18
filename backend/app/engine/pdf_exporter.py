import re
import os
from fpdf import FPDF


def _make_wrappable(text: str, max_word_length: int = 40) -> str:
    """Insert spaces into overly long unbroken tokens so fpdf2 can wrap them."""
    def break_long_word(match):
        word = match.group(0)
        return " ".join(word[i:i + max_word_length] for i in range(0, len(word), max_word_length))

    return re.sub(r'\S{' + str(max_word_length + 1) + r',}', break_long_word, text)


FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")


class QuestionPaperPDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, self.title_text, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def build_questions_pdf(subject_name: str, questions: list[dict]) -> bytes:
    pdf = QuestionPaperPDF()
    pdf.title_text = f"{subject_name} - Generated Question Bank"

    regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
    italic = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")

    if not (os.path.exists(regular) and os.path.exists(bold) and os.path.exists(italic)):
        raise RuntimeError(f"DejaVu font files not found in {FONT_DIR} — download them first")

    pdf.add_font("DejaVu", "", regular)
    pdf.add_font("DejaVu", "B", bold)
    pdf.add_font("DejaVu", "I", italic)

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_font("DejaVu", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(
        0, 5,
        _make_wrappable(
            "Note: These are newly generated practice questions based on historical exam patterns and "
            "syllabus content. They are not guaranteed to appear in any future examination. The evidence "
            "score reflects how strongly a topic has recurred historically, not a prediction for this "
            "specific question."
        ),
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.set_text_color(0, 0, 0)
    pdf.ln(4)

    for i, q in enumerate(questions, start=1):
        pdf.set_font("DejaVu", "B", 11)
        marks_str = f"[{q['marks']} marks]" if q.get("marks") else ""
        question_line = _make_wrappable(f"Q{i}. {q['question_text']} {marks_str}")
        pdf.multi_cell(0, 7, question_line, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("DejaVu", "I", 9)
        pdf.set_text_color(90, 90, 90)
        meta_line = _make_wrappable(f"Topic: {q['topic_name']}  |  Type: {q['question_type']}  |  Evidence Score: {q['evidence_score']}/100")
        pdf.multi_cell(0, 5, meta_line, new_x="LMARGIN", new_y="NEXT")

        reason_line = _make_wrappable(f"Note: {q['generation_reason']}")
        pdf.multi_cell(0, 5, reason_line, new_x="LMARGIN", new_y="NEXT")

        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

    return bytes(pdf.output())