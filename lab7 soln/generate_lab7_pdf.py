import os
import sys
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Omit header and footer on cover page (page 1)
        if self._pageNumber > 1:
            # Running Header
            self.drawString(
                54, 11 * inch - 36,
                "LAB 7: FUZZ TESTING FOR INPUT VALIDATION BUGS - EVIDENCE REPORT"
            )
            self.drawRightString(
                8.5 * inch - 54, 11 * inch - 36,
                "PES UNIVERSITY - SE LAB"
            )
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 40, 8.5 * inch - 54, 11 * inch - 40)
            
            # Running Footer
            self.line(54, 42, 8.5 * inch - 54, 42)
            self.drawString(
                54, 30,
                "Student: Anish A Kunder | SRN: PES1UG24AM343"
            )
            self.drawRightString(
                8.5 * inch - 54, 30,
                f"Page {self._pageNumber} of {page_count}"
            )
        self.restoreState()


def get_scaled_image(img_path, max_width=490, max_height=185):
    """Calculates scaling to preserve aspect ratio within designated bounds."""
    with PILImage.open(img_path) as im:
        orig_w, orig_h = im.size
    
    scale_w = max_width / orig_w
    scale_h = max_height / orig_h
    scale = min(scale_w, scale_h, 1.0)
    
    return Image(img_path, width=orig_w * scale, height=orig_h * scale)


def build_pdf():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(script_dir, "Lab7_FuzzTesting_Evidence.pdf")
    evidence_dir = os.path.join(script_dir, "evidence")

    # Document margins: 54pt (0.75 in) left/right, 48pt top/bottom
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=48,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    # Typography & Styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=28,
        textColor=colors.HexColor("#0F172A"),
        alignment=1,  # Center
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        alignment=1,
        spaceAfter=18,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F2942"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4,
    )

    table_header_style = ParagraphStyle(
        "TableHeader_Custom",
        parent=body_style,
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=2,
    )

    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#0F172A"),
    )

    caption_style = ParagraphStyle(
        "Caption_Custom",
        parent=styles["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#475569"),
        alignment=1,  # Center
        spaceBefore=3,
        spaceAfter=8,
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 30))
    
    # Institution Banner
    inst_table = Table(
        [[Paragraph("<b>PES UNIVERSITY</b> &nbsp;|&nbsp; DEPARTMENT OF COMPUTER SCIENCE &amp; ENGINEERING", ParagraphStyle("SubHeader", parent=subtitle_style, fontSize=8.5, textColor=colors.HexColor("#0284C7")))]],
        colWidths=[504]
    )
    inst_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(inst_table)
    story.append(Spacer(1, 10))

    story.append(HRFlowable(width="100%", thickness=2.5, color=colors.HexColor("#0284C7"), spaceAfter=20, spaceBefore=0))

    # Title & Subtitle
    story.append(Paragraph("LAB 7 - FUZZ TESTING FOR INPUT VALIDATION BUGS", title_style))
    story.append(Paragraph("Automated Defect Discovery, Minimization &amp; Defensive Hardening Using Hypothesis", subtitle_style))
    story.append(HRFlowable(width="50%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=25, spaceBefore=0))

    # Student Identification Card
    student_info = [
        [Paragraph("<b>Course:</b>", body_style), Paragraph("Software Engineering Laboratory (UE23CS352AA)", body_style)],
        [Paragraph("<b>Lab Title:</b>", body_style), Paragraph("Lab 7: Fuzz Testing for Input Validation Bugs", body_style)],
        [Paragraph("<b>Assigned System:</b>", body_style), Paragraph("Elevator Dispatch System (Module #38)", body_style)],
        [Paragraph("<b>Student Name:</b>", body_style), Paragraph("<b>Anish A Kunder</b>", body_style)],
        [Paragraph("<b>SRN:</b>", body_style), Paragraph("<b>PES1UG24AM343</b>", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("https://github.com/planetai05/L6_L7_38_elevator_dispatch", body_style)],
        [Paragraph("<b>Branch:</b>", body_style), Paragraph("<code>lab6-lab7-solutions</code>", body_style)],
        [Paragraph("<b>Date of Submission:</b>", body_style), Paragraph("November 2026", body_style)],
    ]
    info_table = Table(student_info, colWidths=[130, 374])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)

    story.append(Spacer(1, 25))

    # Executive Summary Card
    exec_summary = [
        [Paragraph("<b>Executive Summary:</b>", body_style)],
        [Paragraph(
            "This report documents the property-based fuzz testing analysis and defensive remediation of the assigned "
            "Elevator Dispatch module. Using Python's <b>Hypothesis</b> testing framework, randomized and malformed data "
            "streams were synthesized across type spaces, boundaries, and encodings. Hypothesis discovered and minimized "
            "<b>10 genuine defects and crashes</b> (AttributeError, ValueError, ZeroDivisionError, and negative telemetry) in "
            "the original code. The application was then defensively refactored with deterministic input validation and bounds "
            "guards without blanket exception handling, achieving a <b>flawless 100% pass rate (14/14 tests)</b>.",
            body_style
        )]
    ]
    summary_table = Table(exec_summary, colWidths=[504])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CONCEPTS, FUNCTIONS, METHODOLOGY & STRATEGIES
    # =========================================================================
    story.append(Paragraph("1. Introduction &amp; Lab Objective", h1_style))
    story.append(Paragraph(
        "Fuzz testing (fuzzing) is an automated software quality assurance and vulnerability discovery methodology where "
        "programs are bombarded with semi-random, malformed, or unexpected inputs to observe failure states. In contrast to "
        "traditional unit tests that only validate scenarios envisioned by the developer, fuzz testing explores unanticipated "
        "combinations, boundary values, and malicious payloads.",
        body_style
    ))
    story.append(Paragraph("<b>Lab Learning Objectives:</b>", body_style))
    story.append(Paragraph("&bull; Apply property-based fuzz testing using Python's <b>Hypothesis</b> library with <code>@given</code> decorators.", bullet_style))
    story.append(Paragraph("&bull; Uncover edge-case crashes, boundary exceptions, and type errors in the unhardened application.", bullet_style))
    story.append(Paragraph("&bull; Analyze test failure minimization and automatic input shrinking performed by Hypothesis.", bullet_style))
    story.append(Paragraph("&bull; Defensively harden all application routines using explicit input validation without blanket exception handling.", bullet_style))

    story.append(Paragraph("2. Description of the Original Application", h1_style))
    story.append(Paragraph(
        "The target application (<code>processor.py</code> / <code>elevator_dispatch.py</code>) processes elevator requests, "
        "floor travel calculations, and passenger load telemetry. The original code assumed ideal inputs without type checks or guards.",
        body_style
    ))

    story.append(Paragraph("3. Explanation of the Three Functions", h1_style))
    fn_data = [
        [Paragraph("Function", table_header_style), Paragraph("Signature &amp; Expected Input", table_header_style), Paragraph("Expected Behavior &amp; Formula", table_header_style)],
        [
            Paragraph("<code>parse_request</code>", code_style),
            Paragraph("<code>text: str</code><br/>Format: <code>'START-&gt;END'</code> (e.g. <code>'5-&gt;9'</code>)", body_style),
            Paragraph("Parses origin and destination floors into an integer tuple <code>(start, end)</code>. Must reject malformed strings.", body_style),
        ],
        [
            Paragraph("<code>total_travel</code>", code_style),
            Paragraph("<code>floors_csv: str</code><br/>Format: <code>'1,5,3,9'</code>", body_style),
            Paragraph("Calculates cumulative vertical travel: &sum; |floor<sub>i+1</sub> - floor<sub>i</sub>|. Returns integer &ge; 0.", body_style),
        ],
        [
            Paragraph("<code>load_percent</code>", code_style),
            Paragraph("<code>text: str</code><br/>Format: <code>'LOAD of CAPACITY'</code> (e.g. <code>'450 of 630'</code>)", body_style),
            Paragraph("Evaluates integer load percentage: <code>(load * 100) // capacity</code>. Requires non-negative load and capacity &gt; 0.", body_style),
        ],
    ]
    fn_table = Table(fn_data, colWidths=[120, 155, 229])
    fn_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2942")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(fn_table)

    story.append(Paragraph("4. Fuzz Testing &amp; Hypothesis Methodology", h1_style))
    story.append(Paragraph(
        "<b>Hypothesis</b> verifies that high-level specifications (properties) hold across an input space. When an exception or "
        "assertion failure occurs, Hypothesis performs <b>counterexample shrinking</b>, iteratively pruning characters or reducing integer "
        "magnitudes until the smallest possible failing input is identified (e.g. shrinking an arbitrary string crash down to <code>''</code> or <code>None</code>).",
        body_style
    ))

    story.append(Paragraph("5. Hypothesis Strategies Used", h1_style))
    story.append(Paragraph("&bull; <code>st.text() | st.none()</code>: Generates arbitrary Unicode strings, empty strings, emojis, and null references.", bullet_style))
    story.append(Paragraph("&bull; <code>st.integers()</code>: Generates negative numbers, zero, large integers (&plusmn;10<sup>5</sup>), and boundary values.", bullet_style))
    story.append(Paragraph("&bull; <code>st.lists(st.integers())</code>: Generates floor sequences from empty lists up to 30 elements.", bullet_style))
    story.append(Paragraph("&bull; <code>st.one_of(...)</code>: Tests foreign types (booleans, floats, lists) to enforce strict type verification.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: INITIAL EXECUTION & INITIAL FAILING TESTS
    # =========================================================================
    story.append(Paragraph("6. Initial Application Execution", h1_style))
    story.append(Paragraph(
        "The original, unhardened elevator dispatch script was initially executed using valid sample inputs "
        "(<code>'5-&gt;9'</code>, <code>'1,5,3,9'</code>, <code>'450 of 630'</code>). Under standard conditions, the script "
        "produced expected outputs as captured in Figure 1 below:",
        body_style
    ))

    img_initial = os.path.join(evidence_dir, "initial_processor_output.png")
    if os.path.exists(img_initial):
        story.append(get_scaled_image(img_initial, max_width=490, max_height=180))
        story.append(Paragraph(
            "<b>Figure 1:</b> Initial execution of the original elevator dispatch application with nominal interactive inputs.",
            caption_style
        ))

    story.append(Spacer(1, 4))

    story.append(Paragraph("7. Initial Failing Test Results", h1_style))
    story.append(Paragraph(
        "Running the comprehensive Hypothesis property test suite against the unhardened code resulted in immediate failure. "
        "Hypothesis detected <b>10 failing tests and 4 passing tests</b> (<b>10 failed, 4 passed in 0.99s</b>), exposing "
        "fatal crashes across every unvalidated function, as shown in the terminal capture in Figure 2:",
        body_style
    ))

    img_failing = os.path.join(evidence_dir, "hypothesis_failing_tests.png")
    if os.path.exists(img_failing):
        story.append(get_scaled_image(img_failing, max_width=490, max_height=180))
        story.append(Paragraph(
            "<b>Figure 2:</b> Terminal evidence displaying Hypothesis discovering and shrinking 10 test failures on unhardened code.",
            caption_style
        ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: BUGS DISCOVERED & DEFENSIVE FIXES
    # =========================================================================
    story.append(Paragraph("8. Bugs Discovered and Their Explanations", h1_style))
    story.append(Paragraph(
        "Hypothesis automatically shrunk counterexamples to identify 10 distinct failure modes in the original implementation:",
        body_style
    ))

    bug_data = [
        [Paragraph("#", table_header_style), Paragraph("Function", table_header_style), Paragraph("Shrunk Input", table_header_style), Paragraph("Observed Exception", table_header_style), Paragraph("Root Cause &amp; Analysis", table_header_style)],
        [
            Paragraph("1", body_style), Paragraph("<code>parse_request</code>", code_style), Paragraph("<code>None</code>, <code>0</code>", code_style),
            Paragraph("<code>AttributeError</code>", body_style), Paragraph("Calling <code>.split()</code> on non-string types raises unhandled attribute error.", body_style)
        ],
        [
            Paragraph("2", body_style), Paragraph("<code>parse_request</code>", code_style), Paragraph("<code>''</code>", code_style),
            Paragraph("<code>ValueError</code>", body_style), Paragraph("Unpacking string without delimiter fails (expected 2 values, got 1).", body_style)
        ],
        [
            Paragraph("3", body_style), Paragraph("<code>parse_request</code>", code_style), Paragraph("<code>'-&gt;'</code>", code_style),
            Paragraph("<code>ValueError</code>", body_style), Paragraph("Splitting yields empty tokens; <code>int('')</code> fails with invalid literal.", body_style)
        ],
        [
            Paragraph("4", body_style), Paragraph("<code>total_travel</code>", code_style), Paragraph("<code>None</code>, <code>0</code>", code_style),
            Paragraph("<code>AttributeError</code>", body_style), Paragraph("Non-string parameter lacks <code>.split()</code> method.", body_style)
        ],
        [
            Paragraph("5", body_style), Paragraph("<code>total_travel</code>", code_style), Paragraph("<code>''</code>", code_style),
            Paragraph("<code>ValueError</code>", body_style), Paragraph("Splitting empty string yields <code>['']</code>, crashing on <code>int('')</code>.", body_style)
        ],
        [
            Paragraph("6", body_style), Paragraph("<code>total_travel</code>", code_style), Paragraph("<code>','</code>, <code>'1,,3'</code>", code_style),
            Paragraph("<code>ValueError</code>", body_style), Paragraph("Consecutive or trailing commas generate empty tokens that cannot parse as integers.", body_style)
        ],
        [
            Paragraph("7", body_style), Paragraph("<code>load_percent</code>", code_style), Paragraph("<code>None</code>, <code>[1]</code>", code_style),
            Paragraph("<code>AttributeError</code>", body_style), Paragraph("Non-string parameter crashes immediately on <code>.split()</code>.", body_style)
        ],
        [
            Paragraph("8", body_style), Paragraph("<code>load_percent</code>", code_style), Paragraph("<code>''</code>", code_style),
            Paragraph("<code>ValueError</code>", body_style), Paragraph("Missing <code>' of '</code> delimiter triggers unpacking error.", body_style)
        ],
        [
            Paragraph("9", body_style), Paragraph("<code>load_percent</code>", code_style), Paragraph("<code>'10 of 0'</code>", code_style),
            Paragraph("<code>ZeroDivisionError</code>", body_style), Paragraph("Car capacity of 0 kg causes integer division by zero.", body_style)
        ],
        [
            Paragraph("10", body_style), Paragraph("<code>load_percent</code>", code_style), Paragraph("<code>'-10 of 100'</code>", code_style),
            Paragraph("<b>Logic Violation</b>", body_style), Paragraph("Negative passenger weight yields invalid negative percentage (<code>-10%</code>).", body_style)
        ],
    ]
    bug_table = Table(bug_data, colWidths=[18, 100, 68, 88, 230])
    bug_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F2942")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(bug_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("9. Fixes Implemented", h1_style))
    story.append(Paragraph(
        "All 10 defects were remediated in <code>processor.py</code> via defensive programming without blanket exception handling:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Explicit Integer Validator:</b> Implemented <code>_is_integer(s)</code> to deterministically verify whether a string is non-empty, contains an optional leading <code>+</code> or <code>-</code> sign, and consists strictly of digits.", bullet_style))
    story.append(Paragraph("&bull; <b>Type &amp; Null Guards:</b> Added <code>isinstance(..., str)</code> at the entry of each function, safely returning <code>None</code> (or <code>0</code>) on foreign types.", bullet_style))
    story.append(Paragraph("&bull; <b>Delimiter Verification:</b> Validated that delimiters occur exactly once, guaranteeing valid binary unpacking.", bullet_style))
    story.append(Paragraph("&bull; <b>Physical Domain Safeguards:</b> Checked that <code>capacity &gt; 0</code> (eliminating <code>ZeroDivisionError</code>) and <code>load &ge; 0</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Deterministic Return Protocol:</b> Invalid inputs return <code>None</code> for parsing/percentage routines and <code>0</code> for travel distance.", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: FIXED EXECUTION, FINAL TESTS & CONCLUSION
    # =========================================================================
    story.append(Paragraph("10. Fixed Application Execution", h1_style))
    story.append(Paragraph(
        "The hardened application was re-run with valid interactive inputs. Intended business logic was completely preserved:",
        body_style
    ))

    img_fixed = os.path.join(evidence_dir, "fixed_processor_output.png")
    if os.path.exists(img_fixed):
        story.append(get_scaled_image(img_fixed, max_width=490, max_height=170))
        story.append(Paragraph(
            "<b>Figure 3:</b> Execution of the fixed elevator dispatch application verifying preserved functionality.",
            caption_style
        ))

    story.append(Spacer(1, 4))

    story.append(Paragraph("11. Final Successful Hypothesis Tests", h1_style))
    story.append(Paragraph(
        "The complete Hypothesis test suite was executed against the hardened code. All <b>14 property-based tests passed "
        "flawlessly (14 passed in 1.28s)</b> across thousands of synthesized inputs, confirming crash resilience and mathematical correctness:",
        body_style
    ))

    img_passing = os.path.join(evidence_dir, "hypothesis_passing_tests.png")
    if os.path.exists(img_passing):
        story.append(get_scaled_image(img_passing, max_width=490, max_height=175))
        story.append(Paragraph(
            "<b>Figure 4:</b> Terminal evidence demonstrating 100% passing rate (14 passed) on the hardened application.",
            caption_style
        ))

    story.append(Spacer(1, 4))

    story.append(Paragraph("12. Conclusion", h1_style))
    story.append(Paragraph(
        "Fuzz testing with Hypothesis demonstrated its power in finding vulnerabilities that manual test cases easily miss, "
        "such as zero-capacity division, non-string injections, and delimiter misconfigurations. By combining automated counterexample "
        "shrinking with disciplined defensive programming, all edge cases were safely guarded, transforming fragile scripts into "
        "robust, fault-tolerant elevator control software.",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated 5-page PDF: {output_pdf}")


if __name__ == "__main__":
    build_pdf()
