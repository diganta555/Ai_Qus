import re
import os
from fpdf import FPDF


def _make_wrappable(text: str, max_word_length: int = 40) -> str:
    def break_long_word(match):
        word = match.group(0)
        return " ".join(word[i:i + max_word_length] for i in range(0, len(word), max_word_length))
    return re.sub(r'\S{' + str(max_word_length + 1) + r',}', break_long_word, text)


def _clean_for_pdf(text: str) -> str:
    text = re.sub(r'\$\$(.*?)\$\$', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\$(.*?)\$', r'\1', text)
    text = re.sub(r'\\frac\{([^}]*)\}\{([^}]*)\}', r'(\1)/(\2)', text)
    text = text.replace('\\lor', ' OR ').replace('\\land', ' AND ').replace('\\neg', 'NOT ')
    text = text.replace('\\times', 'x').replace('\\cdot', '.').replace('\\leq', '<=').replace('\\geq', '>=')
    text = text.replace('\\infty', 'infinity').replace('\\sum', 'sum').replace('\\in', 'in')
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[-*]\s+', '- ', text, flags=re.MULTILINE)
    return text.strip()


FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")

PRIMARY = (124, 58, 237)     # brand purple
TEXT_DARK = (30, 30, 30)
TEXT_GRAY = (110, 110, 110)
LINE_GRAY = (225, 225, 230)
BADGE_BG = (243, 238, 255)


class QuestionPaperPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return  # title block is drawn manually on page 1 instead
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*TEXT_GRAY)
        self.cell(0, 8, self.title_text, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_draw_color(*LINE_GRAY)
        self.line(15, 18, self.w - 15, 18)
        self.ln(6)
        self.set_text_color(*TEXT_DARK)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*TEXT_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_text_color(*TEXT_DARK)


def build_questions_pdf(subject_name: str, questions: list[dict]) -> bytes:
    pdf = QuestionPaperPDF()
    pdf.title_text = f"{subject_name} - Question Bank"

    regular = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
    italic = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")

    if not (os.path.exists(regular) and os.path.exists(bold) and os.path.exists(italic)):
        raise RuntimeError(f"DejaVu font files not found in {FONT_DIR} — download them first")

    pdf.add_font("DejaVu", "", regular)
    pdf.add_font("DejaVu", "B", bold)
    pdf.add_font("DejaVu", "I", italic)

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=22)

    # --- Title block (page 1 only) ---
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(*TEXT_DARK)
    pdf.cell(0, 14, subject_name, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(*TEXT_GRAY)
    pdf.cell(0, 8, "Generated Question Bank", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_text_color(*TEXT_DARK)
    pdf.ln(4)

    pdf.set_draw_color(*PRIMARY)
    pdf.set_line_width(0.6)
    pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
    pdf.set_line_width(0.2)
    pdf.ln(10)

    # --- Questions ---
    for i, q in enumerate(questions, start=1):
        start_y = pdf.get_y()

        # Question number badge
        pdf.set_fill_color(*BADGE_BG)
        pdf.set_text_color(*PRIMARY)
        pdf.set_font("DejaVu", "B", 10)
        badge_w = 12
        pdf.cell(badge_w, 8, f"Q{i}", fill=True, align="C")

        # Meta line (topic / marks) to the right of the badge
        pdf.set_text_color(*TEXT_GRAY)
        pdf.set_font("DejaVu", "", 9)
        meta_parts = []
        if q.get("topic_name"):
            meta_parts.append(q["topic_name"])
        if q.get("marks"):
            meta_parts.append(f"{q['marks']} marks")
        meta_line = "  •  ".join(meta_parts)
        pdf.cell(0, 8, meta_line, new_x="LMARGIN", new_y="NEXT")

        # Question text, indented to align under the badge
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_font("DejaVu", "", 11.5)
        pdf.set_x(15 + badge_w + 3)
        question_text = _clean_for_pdf(q["question_text"])
        question_line = _make_wrappable(question_text)
        pdf.multi_cell(pdf.w - 15 - (15 + badge_w + 3), 6.5, question_line)

        pdf.ln(3)
        pdf.set_draw_color(*LINE_GRAY)
        pdf.line(15, pdf.get_y(), pdf.w - 15, pdf.get_y())
        pdf.ln(6)

    return bytes(pdf.output())
