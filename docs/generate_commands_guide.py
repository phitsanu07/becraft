"""
Generate becraft Commands Guide (Thai) as PDF.

Covers:
- Decision tree (เลือก command อะไร?)
- Each command: use cases, anti-cases, examples, common mistakes
- Real-world scenarios
- Cheat sheet

Run:
    python3 generate_commands_guide.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, NextPageTemplate,
)

# ============================================================
# Setup
# ============================================================

BASE = Path(__file__).parent
FONTS = BASE / "fonts"
OUTPUT = BASE / "becraft-commands-guide.pdf"

pdfmetrics.registerFont(TTFont('Sarabun', str(FONTS / 'Sarabun-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Bold', str(FONTS / 'Sarabun-Bold.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Italic', str(FONTS / 'Sarabun-Italic.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Light', str(FONTS / 'Sarabun-Light.ttf')))

# Colors — guide theme: green (commands) + amber (use cases)
PRIMARY = HexColor('#0D9488')      # Teal
SECONDARY = HexColor('#0F766E')
ACCENT = HexColor('#F59E0B')
DARK = HexColor('#0F172A')
GRAY_DARK = HexColor('#475569')
GRAY = HexColor('#64748B')
GRAY_LIGHT = HexColor('#E2E8F0')
GRAY_BG = HexColor('#F8FAFC')
RED = HexColor('#DC2626')
GREEN = HexColor('#059669')
BLUE = HexColor('#2563EB')
PURPLE = HexColor('#7C3AED')
CODE_BG = HexColor('#1E293B')
CODE_FG = HexColor('#F1F5F9')


def get_styles():
    s = {}
    s['Title'] = ParagraphStyle(
        name='Title', fontName='Sarabun-Bold', fontSize=30, leading=38,
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=12,
    )
    s['Subtitle'] = ParagraphStyle(
        name='Subtitle', fontName='Sarabun-Light', fontSize=15, leading=20,
        textColor=GRAY_DARK, alignment=TA_CENTER, spaceAfter=8,
    )
    s['CoverInfo'] = ParagraphStyle(
        name='CoverInfo', fontName='Sarabun', fontSize=11, leading=16,
        textColor=GRAY, alignment=TA_CENTER,
    )
    s['Chapter'] = ParagraphStyle(
        name='Chapter', fontName='Sarabun-Bold', fontSize=22, leading=28,
        textColor=PRIMARY, spaceAfter=12, spaceBefore=18, keepWithNext=True,
    )
    s['Section'] = ParagraphStyle(
        name='Section', fontName='Sarabun-Bold', fontSize=15, leading=20,
        textColor=DARK, spaceAfter=8, spaceBefore=14, keepWithNext=True,
    )
    s['SubSection'] = ParagraphStyle(
        name='SubSection', fontName='Sarabun-Bold', fontSize=12, leading=16,
        textColor=SECONDARY, spaceAfter=4, spaceBefore=10, keepWithNext=True,
    )
    s['CommandHeader'] = ParagraphStyle(
        name='CommandHeader', fontName='Sarabun-Bold', fontSize=18, leading=24,
        textColor=PRIMARY, spaceAfter=10, spaceBefore=18, keepWithNext=True,
    )
    s['Body'] = ParagraphStyle(
        name='Body', fontName='Sarabun', fontSize=10.5, leading=16,
        textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=6,
    )
    s['BodyCenter'] = ParagraphStyle(
        name='BodyCenter', fontName='Sarabun', fontSize=10.5, leading=16,
        textColor=DARK, alignment=TA_CENTER, spaceAfter=6,
    )
    s['Bullet'] = ParagraphStyle(
        name='Bullet', fontName='Sarabun', fontSize=10.5, leading=16,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=2,
        leftIndent=18, bulletIndent=4,
    )
    s['Code'] = ParagraphStyle(
        name='Code', fontName='Courier', fontSize=8.5, leading=12,
        textColor=CODE_FG, backColor=CODE_BG,
        leftIndent=10, rightIndent=10, spaceAfter=8, spaceBefore=4,
        borderPadding=(8, 8, 8, 8),
    )
    s['UseCase'] = ParagraphStyle(
        name='UseCase', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#D1FAE5'),
    )
    s['AntiCase'] = ParagraphStyle(
        name='AntiCase', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#FEE2E2'),
    )
    s['Mistake'] = ParagraphStyle(
        name='Mistake', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#FEF3C7'),
    )
    s['Tip'] = ParagraphStyle(
        name='Tip', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=6, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#DBEAFE'),
    )
    s['TOC1'] = ParagraphStyle(
        name='TOC1', fontName='Sarabun-Bold', fontSize=12, leading=18,
        textColor=DARK, spaceAfter=2,
    )
    s['TOC2'] = ParagraphStyle(
        name='TOC2', fontName='Sarabun', fontSize=10.5, leading=15,
        textColor=GRAY_DARK, leftIndent=16,
    )
    return s


def code_block(text):
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('\n', '<br/>')
    text = text.replace(' ', '&nbsp;')
    return Paragraph(text, get_styles()['Code'])


def make_table(data, col_widths=None, header=True, align='LEFT', font_size=9.5):
    t = Table(data, colWidths=col_widths, hAlign=align)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Sarabun'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.4, GRAY_LIGHT),
    ]
    if header:
        style.extend([
            ('FONTNAME', (0, 0), (-1, 0), 'Sarabun-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTSIZE', (0, 0), (-1, 0), font_size + 0.5),
        ])
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), GRAY_BG))
    t.setStyle(TableStyle(style))
    return t


def page_header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Sarabun', 8)
    canvas.setFillColor(GRAY)

    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.0 * cm, 'becraft — Commands Guide')
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f'หน้า {doc.page}')

    canvas.setFont('Sarabun-Light', 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, 'becraft v0.4.1')
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm,
                            'คู่มือการใช้งาน 10 Commands')
    canvas.line(2 * cm, A4[1] - 1.5 * cm, A4[0] - 2 * cm, A4[1] - 1.5 * cm)

    canvas.restoreState()


def cover_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, A4[1] - 4 * cm, A4[0], 4 * cm, fill=1, stroke=0)
    canvas.setFillColor(SECONDARY)
    canvas.rect(0, 0, A4[0], 1.5 * cm, fill=1, stroke=0)
    canvas.restoreState()


def H(text, style='Body', styles=None):
    if styles is None:
        styles = get_styles()
    return Paragraph(text, styles[style])


# ============================================================
# Cover
# ============================================================

def build_cover(styles):
    elems = []
    elems.append(Spacer(1, 4 * cm))
    elems.append(Paragraph('becraft', styles['Title']))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph('Commands Guide', styles['Subtitle']))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph('คู่มือการใช้งาน Commands พร้อม Use Cases',
                            styles['Subtitle']))
    elems.append(Spacer(1, 4 * cm))

    elems.append(Paragraph('"ใช้ command อะไร เมื่อไหร่ ทำไม?"',
                            ParagraphStyle('Cover', fontName='Sarabun-Bold',
                                            fontSize=22, leading=28,
                                            textColor=DARK, alignment=TA_CENTER)))
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(Paragraph('ฉบับสำหรับผู้เริ่มต้น — เน้น Decision Tree',
                            styles['CoverInfo']))
    elems.append(Spacer(1, 5 * cm))

    elems.append(Paragraph('สำหรับ Claude Code & Google Antigravity',
                            styles['CoverInfo']))
    elems.append(Spacer(1, 0.2 * cm))
    elems.append(Paragraph('10 Commands • 4 Real-world Scenarios • Cheat Sheet',
                            styles['CoverInfo']))
    elems.append(Spacer(1, 0.2 * cm))
    elems.append(Paragraph('Version 0.4.1 • 2026', styles['CoverInfo']))
    return elems


def build_toc(styles):
    elems = [
        H('สารบัญ', 'Chapter', styles),
        Spacer(1, 6),
    ]
    chapters = [
        ('คำนำ — ทำไมเอกสารฉบับนี้', 1),
        ('บทที่ 1: ภาพรวม Commands ทั้งหมด', 2),
        ('  1.1 ตาราง 10 Commands', 1),
        ('  1.2 หลักการเลือก Command', 1),
        ('บทที่ 2: Decision Tree (เลือก Command อะไร?)', 2),
        ('  2.1 เริ่มจากสภาพโปรเจกต์', 1),
        ('  2.2 เริ่มจากความต้องการ', 1),
        ('  2.3 Quick decision matrix', 1),
        ('บทที่ 3: /be — Smart Router', 2),
        ('บทที่ 4: /be-help', 2),
        ('บทที่ 5: /be-plan', 2),
        ('บทที่ 6: /be-bootstrap', 2),
        ('บทที่ 7: /be-schema', 2),
        ('บทที่ 8: /be-api', 2),
        ('บทที่ 9: /be-auth', 2),
        ('บทที่ 10: /be-observe', 2),
        ('บทที่ 11: /be-test', 2),
        ('บทที่ 12: /be-fix', 2),
        ('บทที่ 13: Real-world Scenarios', 2),
        ('  13.1 สร้าง User Management API ตั้งแต่ต้น', 1),
        ('  13.2 เพิ่ม Products feature ในโปรเจกต์ที่มีอยู่', 1),
        ('  13.3 เพิ่ม Google OAuth ในระบบที่มี', 1),
        ('  13.4 Fix failing tests + debug', 1),
        ('  13.5 เตรียม deploy production', 1),
        ('บทที่ 14: Common Mistakes', 2),
        ('บทที่ 15: Cheat Sheet — สรุป 1 หน้า', 2),
    ]
    for title, level in chapters:
        st = 'TOC1' if level == 2 else 'TOC2'
        elems.append(Paragraph(title, styles[st]))
    return elems


# ============================================================
# Chapter 1: Overview
# ============================================================

def chapter_intro(styles):
    elems = []
    elems.append(H('คำนำ — ทำไมเอกสารฉบับนี้', 'Chapter', styles))
    elems.append(H('''becraft มี 10 commands ที่ดูคล้ายกัน — หลายคนสับสนว่า
"ตอนไหนใช้ <font face="Courier">/be-bootstrap</font>?
ตอนไหนใช้ <font face="Courier">/be-api</font>?
ตอนไหนใช้ <font face="Courier">/be</font>?"''', 'Body', styles))

    elems.append(H('''<b>เอกสารฉบับนี้</b> จะแก้ความสับสนนั้นด้วย:''', 'Body', styles))
    bullets = [
        '🎯 <b>Decision Tree</b> — เห็นภาพรวมเลือก command ได้ใน 10 วินาที',
        '📋 <b>Use cases ของแต่ละ command</b> — รู้ว่าตอนไหนใช้, ตอนไหนไม่ใช้',
        '⚠️ <b>Common mistakes</b> — เลี่ยง pattern ที่หลายคนทำผิด',
        '🎬 <b>Real-world scenarios</b> — ลำดับการใช้ commands ใน workflow จริง',
        '📝 <b>Cheat Sheet</b> — สรุป 1 หน้าเอาไว้แปะข้างจอ',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(Paragraph('''<b>Tip:</b> ถ้าอ่านครั้งเดียวไม่จำ — หาบทที่ 15
(Cheat Sheet) ปริ้นท์เก็บไว้ก่อน''', styles['Tip']))

    return elems


def chapter_overview(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 1: ภาพรวม Commands ทั้งหมด', 'Chapter', styles))

    elems.append(H('1.1 ตาราง 10 Commands', 'Section', styles))

    cmd_overview = [
        ['Command', 'ทำอะไร', 'ใช้บ่อยแค่ไหน', 'ต้องมี skeleton?'],
        ['/be', 'Smart router — บอก AI ทำอะไรก็ได้', '⭐⭐⭐⭐⭐ บ่อยสุด', 'แล้วแต่งาน'],
        ['/be-help', 'แสดงคำสั่งทั้งหมด', '⭐ บางครั้ง', 'ไม่ต้อง'],
        ['/be-plan', 'วางแผนก่อนทำ (มี planning step)', '⭐⭐ ก่อนงานใหญ่', 'ไม่ต้อง'],
        ['/be-bootstrap', 'สร้าง project ใหม่ตั้งแต่ต้น', '⭐⭐ ครั้งเดียวต่อ project', '❌ ไม่ต้องมี'],
        ['/be-schema', 'ออกแบบ DB schema + migration', '⭐⭐⭐ ทุก entity ใหม่', '✅ ต้องมี'],
        ['/be-api', 'สร้าง endpoints + DTOs', '⭐⭐⭐⭐ ทุก resource', '✅ ต้องมี'],
        ['/be-auth', 'JWT auth + RBAC + rate-limit', '⭐⭐ ครั้งเดียว/feature', '✅ ต้องมี'],
        ['/be-observe', 'Logs + metrics + health', '⭐ ครั้งเดียวต่อ project', '✅ ต้องมี'],
        ['/be-test', 'สร้าง + รัน tests', '⭐⭐⭐⭐ ทุกครั้งหลัง implement', '✅ ต้องมี'],
        ['/be-fix', 'Debug + แก้ bug', '⭐⭐⭐ เมื่อมี bug', '✅ ต้องมี'],
    ]
    elems.append(make_table(cmd_overview, col_widths=[3 * cm, 5.5 * cm, 4 * cm, 3.5 * cm], font_size=8.5))

    elems.append(H('1.2 หลักการเลือก Command (3 คำถาม)', 'Section', styles))

    elems.append(H('<b>คำถาม 1: โปรเจกต์อยู่ในสถานะไหน?</b>', 'SubSection', styles))
    bullets = [
        '🌱 <b>Greenfield</b> (folder ว่าง / ไม่มี <font face="Courier">package.json</font>) → <font face="Courier">/be-bootstrap</font>',
        '🌿 <b>Existing</b> (มี skeleton แล้ว) → ใช้ command อื่นๆ ได้',
        '🐛 <b>Broken</b> (มี bug, build fail) → <font face="Courier">/be-fix</font>',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('<b>คำถาม 2: งานชัดเจนแค่ไหน?</b>', 'SubSection', styles))
    bullets = [
        '✅ <b>ชัด 100%</b> ("เพิ่ม CRUD products") → ใช้ command เฉพาะ <font face="Courier">/be-api</font>',
        '🤔 <b>ไม่แน่ใจ</b> หรือ <b>ใหญ่หลาย step</b> ("สร้างระบบจองห้อง") → <font face="Courier">/be</font> หรือ <font face="Courier">/be-plan</font>',
        '❓ <b>ไม่รู้จัก commands</b> → <font face="Courier">/be-help</font>',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('<b>คำถาม 3: Output ที่อยากได้คืออะไร?</b>', 'SubSection', styles))

    output_data = [
        ['Output ที่ต้องการ', 'Command'],
        ['Project ใหม่ทั้ง skeleton', '/be-bootstrap'],
        ['Database schema + migration', '/be-schema'],
        ['REST endpoints + Swagger docs', '/be-api'],
        ['Login/register/JWT', '/be-auth'],
        ['Health checks + Prometheus metrics', '/be-observe'],
        ['Tests ที่ pass', '/be-test'],
        ['Bug ที่หาย', '/be-fix'],
        ['ไม่แน่ใจ — AI ตัดสินให้', '/be (smart)'],
    ]
    elems.append(make_table(output_data, col_widths=[10 * cm, 6 * cm]))

    return elems


# ============================================================
# Chapter 2: Decision Tree
# ============================================================

def chapter_decision_tree(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 2: Decision Tree (เลือก Command อะไร?)', 'Chapter', styles))

    elems.append(H('2.1 เริ่มจากสภาพโปรเจกต์', 'Section', styles))
    elems.append(code_block('''            ┌───────────────────────┐
            │  คุณกำลังจะทำอะไร?    │
            └──────────┬────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Greenfield     Existing        Broken
    (folder        (มี skeleton)   (มี bug)
    ว่าง)
        │              │              │
        ▼              ▼              ▼
  /be-bootstrap   ใช้ command      /be-fix
                  เฉพาะตาม need        │
                       │              ▼
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
    Schema?         Endpoints?      Auth?
        │              │              │
        ▼              ▼              ▼
   /be-schema     /be-api        /be-auth
'''))

    elems.append(H('2.2 เริ่มจากความต้องการ', 'Section', styles))
    elems.append(code_block('''            ┌─────────────────────────┐
            │ ต้องการ output แบบไหน? │
            └────────────┬────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   Code ใหม่        Tests ผ่าน         Production-
                                       ready
       │                 │                 │
       ▼                 ▼                 ▼
   ┌───────┐         /be-test         /be-observe
   │ skeleton?│                       (logs/metrics)
   └───┬───┘                              +
       │                                /be-test
   ┌───┴───┐
   YES    NO
   │      │
   ▼      ▼
   /be-api  /be-bootstrap'''))

    elems.append(H('2.3 Quick Decision Matrix', 'Section', styles))

    matrix = [
        ['สถานการณ์', 'Command', 'หมายเหตุ'],
        ['ไม่รู้จะใช้อะไร', '/be', 'AI วิเคราะห์ + เลือกให้'],
        ['ลืม commands', '/be-help', 'แสดงรายการทั้งหมด'],
        ['งานใหญ่ ไม่แน่ใจ scope', '/be-plan', 'AI แสดง plan ก่อน'],
        ['Folder ว่าง — สร้างใหม่', '/be-bootstrap', '~5 sec ผ่าน template'],
        ['เพิ่ม entity ใหม่ใน DB', '/be-schema', 'Prisma migration safe'],
        ['เพิ่ม CRUD endpoints', '/be-api', 'Need schema first'],
        ['User ต้อง login', '/be-auth', 'JWT + bcrypt + rate limit'],
        ['Deploy production', '/be-observe + /be-test', '+ verify หลังทำ'],
        ['Test fail / build fail', '/be-fix', 'Auto-fix loop'],
        ['ทำต่อจากค้างไว้', '/be ทำต่อ', 'อ่าน memory แล้ว resume'],
    ]
    elems.append(make_table(matrix, col_widths=[5 * cm, 4 * cm, 7 * cm], font_size=9))

    elems.append(Paragraph('''<b>Tip:</b> ถ้ายังไม่แน่ใจ → ใช้ <font face="Courier">/be</font>
ก่อนเสมอ AI จะถาม + แนะนำ command ที่ถูก ไม่ต้องเสียเวลาเดา''', styles['Tip']))

    return elems


# ============================================================
# Per-Command Chapters (template)
# ============================================================

def make_command_chapter(num: int, cmd_data: dict, styles):
    """Generate a chapter for one command."""
    elems = []
    elems.append(PageBreak())
    elems.append(H(f"บทที่ {num}: {cmd_data['title']}", 'Chapter', styles))

    # Quick summary
    elems.append(Paragraph(f"<b>📌 สรุปสั้น:</b> {cmd_data['summary']}", styles['Body']))
    elems.append(Spacer(1, 6))

    # Quick info table
    info_data = [
        ['ทำอะไร', cmd_data['summary']],
        ['Shortcut', cmd_data.get('shortcut', '-')],
        ['Agent ที่ delegate ไป', cmd_data.get('agent', '-')],
        ['ต้องมี skeleton?', cmd_data.get('needs_skeleton', '-')],
        ['ใช้บ่อยแค่ไหน', cmd_data.get('frequency', '-')],
        ['ใช้เวลา', cmd_data.get('duration', '-')],
    ]
    elems.append(make_table(info_data, col_widths=[5 * cm, 11 * cm], header=False, font_size=9.5))

    # Use cases
    elems.append(H('✅ ใช้เมื่อไหร่ (Use Cases)', 'Section', styles))
    for uc in cmd_data['use_cases']:
        elems.append(Paragraph(uc, styles['UseCase']))

    # Anti-cases
    elems.append(H('❌ ห้ามใช้เมื่อไหร่', 'Section', styles))
    for ac in cmd_data['anti_cases']:
        elems.append(Paragraph(ac, styles['AntiCase']))

    # Examples
    elems.append(H('📖 ตัวอย่างการใช้งาน', 'Section', styles))
    for ex in cmd_data['examples']:
        elems.append(H(f"<b>{ex['title']}</b>", 'SubSection', styles))
        elems.append(code_block(ex['command']))
        if ex.get('explanation'):
            elems.append(H(ex['explanation'], 'Body', styles))

    # What you get
    elems.append(H('🎁 สิ่งที่ AI สร้าง/ทำให้', 'Section', styles))
    for w in cmd_data['outputs']:
        elems.append(H(f"• {w}", 'Bullet', styles))

    # Common mistakes
    if 'mistakes' in cmd_data:
        elems.append(H('⚠️ Common Mistakes', 'Section', styles))
        for m in cmd_data['mistakes']:
            elems.append(Paragraph(m, styles['Mistake']))

    # Often used with
    if 'pairs_with' in cmd_data:
        elems.append(H('🔗 มักใช้คู่กับ command', 'Section', styles))
        elems.append(make_table(
            [['Command', 'เมื่อไหร่']] + cmd_data['pairs_with'],
            col_widths=[4 * cm, 12 * cm],
            font_size=9.5,
        ))

    return elems


# ============================================================
# Command data definitions
# ============================================================

def cmd_be():
    return {
        'title': '/be — Smart Router',
        'summary': 'พิมพ์อะไรก็ได้ในภาษาธรรมชาติ AI วิเคราะห์ + เลือก agent ให้',
        'shortcut': '/b',
        'agent': 'varies (ขึ้นกับ intent)',
        'needs_skeleton': '⚠️ ขึ้นกับงาน',
        'frequency': '⭐⭐⭐⭐⭐ บ่อยสุด — เริ่มต้นที่ command นี้',
        'duration': 'ขึ้นกับงาน (3 sec - หลายนาที)',
        'use_cases': [
            '✅ ไม่แน่ใจว่าจะใช้ command ไหน → ใช้ <font face="Courier">/be</font> ปลอดภัยสุด',
            '✅ งานใหญ่ที่ใช้หลาย agent (เช่น "สร้างระบบ inventory") — AI orchestrate ให้',
            '✅ ต้องการ "ทำต่อ" จากที่ค้างไว้ — AI อ่าน memory + resume',
            '✅ คำสั่งเป็นภาษาธรรมชาติ (เช่น "เพิ่ม endpoint POST /products") — AI parse + ตัดสิน',
            '✅ ต้องการให้ AI ทำหลายขั้นตอนในรอบเดียว (schema + api + tests)',
        ],
        'anti_cases': [
            '❌ งานเล็กๆ ชัดเจนมาก (เช่น "สร้าง CRUD products") → ใช้ <font face="Courier">/be-api</font> ตรงๆ เร็วกว่า',
            '❌ ต้องการ control 100% ว่า agent ไหนทำอะไร → ใช้ command เฉพาะ',
        ],
        'examples': [
            {
                'title': 'งานง่ายๆ',
                'command': '/be สร้าง endpoint POST /products รับ name, price, stock',
                'explanation': 'AI จะ detect ว่าเป็นงาน api → delegate to api-builder',
            },
            {
                'title': 'งานใหญ่ multi-agent',
                'command': '/be add inventory tracking with audit log + notifications',
                'explanation': 'AI plan → schema + api + auth + observability + test',
            },
            {
                'title': 'ทำต่อ',
                'command': '/be ทำต่อ',
                'explanation': 'AI อ่าน .be/memory/active.md → resume จาก next steps',
            },
            {
                'title': 'ขอคำแนะนำ',
                'command': '/be ควรเริ่มยังไงสำหรับโปรเจกต์ booking ห้อง?',
                'explanation': 'AI วิเคราะห์ → แนะนำ /be-bootstrap หรือ /be-plan',
            },
        ],
        'outputs': [
            'Workflow plan ก่อน execute (โปร่งใส)',
            'Agent ที่เหมาะกับงาน + เหตุผล',
            'Multi-agent orchestration ตาม pattern (sequential/parallel)',
            'Progress reporting ตลอดทาง',
            'Memory updated หลังเสร็จ',
        ],
        'mistakes': [
            '❌ <b>คาดหวัง output ตายตัว</b> — /be ปรับวิธีทำตาม intent ทุกครั้ง ไม่เหมือน /be-api ที่ output คงที่',
            '❌ <b>ไม่อ่าน plan ที่ AI แสดง</b> — /be แสดง workflow plan ก่อน ลอง read ก่อนพิมพ์ "Go"',
            '❌ <b>คาดหวังผลทันที</b> — งานใหญ่ /be อาจใช้หลาย agent ต้องอดทน',
        ],
        'pairs_with': [
            ['/be-help', 'ถ้า /be ตอบไม่ตรง → ดู commands ที่มีก่อน'],
            ['/be-fix', 'ถ้า /be ทำแล้วมี bug → ใช้ /be-fix แก้'],
        ],
    }


def cmd_be_help():
    return {
        'title': '/be-help — แสดงคำสั่งทั้งหมด',
        'summary': 'แสดง 10 commands พร้อม shortcut + ตัวอย่าง',
        'shortcut': '/be-h',
        'agent': '(ไม่มี — แค่แสดงข้อมูล)',
        'needs_skeleton': '❌ ไม่ต้อง',
        'frequency': '⭐ บางครั้ง — ตอนลืม',
        'duration': '< 1 sec',
        'use_cases': [
            '✅ ลืมว่ามี commands อะไรบ้าง',
            '✅ อยากเห็น shortcuts',
            '✅ Onboarding ทีมใหม่',
            '✅ เปรียบเทียบ commands ที่คล้ายกัน',
        ],
        'anti_cases': [
            '❌ ต้องการรายละเอียดลึก → อ่านเอกสารฉบับนี้แทน',
            '❌ งานต้องทำจริง → ไม่ใช่ command นี้',
        ],
        'examples': [
            {
                'title': 'ดูรายการคำสั่ง',
                'command': '/be-help',
                'explanation': 'แสดงตาราง commands + descriptions',
            },
        ],
        'outputs': [
            'ตาราง 10 commands พร้อม shortcuts',
            'Quick start examples',
            'Tech stack summary',
            'Memory system overview',
        ],
        'pairs_with': [
            ['/be', 'ถ้ายังไม่แน่ใจหลัง /be-help → /be ช่วยตัดสินใจ'],
        ],
    }


def cmd_be_plan():
    return {
        'title': '/be-plan — วางแผนก่อนทำ',
        'summary': 'AI วิเคราะห์ requirements + แสดง phased plan ให้ดูก่อน execute',
        'shortcut': '/be-p',
        'agent': '📋 plan-orchestrator',
        'needs_skeleton': '⚠️ ทั้งคู่ได้',
        'frequency': '⭐⭐ ก่อนงานใหญ่',
        'duration': '~30 sec วิเคราะห์, แล้วรอ user "Go"',
        'use_cases': [
            '✅ งานใหญ่ที่ต้องใช้หลาย agent (5+ phases)',
            '✅ อยากเห็น plan ก่อนตัดสินใจว่าจะทำหรือไม่',
            '✅ ต้องการประมาณเวลา + scope ก่อน commit',
            '✅ Project ที่มี dependency ซับซ้อน',
            '✅ ต้องอนุมัติจากทีมก่อนเริ่มทำ',
        ],
        'anti_cases': [
            '❌ งานเล็ก 1-3 ไฟล์ → /be-api หรือ command เฉพาะเลย',
            '❌ Bug fix → /be-fix ตรงๆ',
            '❌ มั่นใจ scope แล้ว → /be-bootstrap หรือ command เฉพาะ',
        ],
        'examples': [
            {
                'title': 'ระบบใหญ่',
                'command': '/be-plan สร้างระบบ booking ห้องประชุม + notification email + admin dashboard',
                'explanation': 'AI แสดง 6-8 phases ให้ดู รอ "Go" ก่อนเริ่ม',
            },
            {
                'title': 'Refactor',
                'command': '/be-plan refactor user module to use new auth strategy',
                'explanation': 'แสดงไฟล์ที่กระทบ + risk analysis ก่อนทำ',
            },
        ],
        'outputs': [
            'Phased plan (Phase 1: ..., Phase 2: ..., etc.)',
            'Agents ที่จะใช้ในแต่ละ phase',
            'Estimated time per phase',
            'File count estimate',
            'Decision points + risks',
            'รอ user confirm "Go" ก่อนเริ่ม',
        ],
        'mistakes': [
            '❌ <b>ใช้กับงานเล็ก</b> — เสียเวลาเพราะต้องรอ plan แล้ว confirm',
            '❌ <b>ไม่อ่าน plan ก่อน Go</b> — เสีย point ของการ plan',
            '❌ <b>คาดหวังการแก้ที่ทันที</b> — /be-plan แค่แสดง plan ไม่ได้สร้างไฟล์',
        ],
        'pairs_with': [
            ['/be-bootstrap', 'หลัง plan ของ project ใหม่ → bootstrap'],
            ['/be', 'หรือใช้ /be แทน — มันเรียก plan-orchestrator ให้อยู่แล้ว'],
        ],
    }


def cmd_be_bootstrap():
    return {
        'title': '/be-bootstrap — สร้างโปรเจกต์ใหม่',
        'summary': 'สร้าง NestJS project skeleton ทั้งหมดใน ~5 วินาที (template-based)',
        'shortcut': '/be-b',
        'agent': '🏗️ bootstrap-agent (+ orchestrator + อื่นๆ)',
        'needs_skeleton': '❌ ไม่ต้อง — สร้างให้',
        'frequency': '⭐⭐ ครั้งเดียวต่อ project',
        'duration': '~5 sec (template) - 1 min (full Vibe Mode)',
        'use_cases': [
            '✅ Folder ว่าง / ไม่มี <font face="Courier">package.json</font> → สร้าง skeleton',
            '✅ เริ่ม project ใหม่จากศูนย์',
            '✅ ต้องการ NestJS + Postgres+Prisma หรือ NestJS + Supabase JS',
            '✅ Vibe Mode — สร้างทั้ง skeleton + features + auth + tests รอบเดียว',
        ],
        'anti_cases': [
            '❌ มี <font face="Courier">package.json</font> แล้ว → ใช้ /be-api, /be-schema แทน',
            '❌ ต้องการ Express, Fastify, Hono, etc. — becraft รองรับแค่ NestJS',
            '❌ ใช้ MongoDB, MySQL, Oracle — รองรับแค่ Postgres (Prisma หรือ Supabase JS)',
        ],
        'examples': [
            {
                'title': 'Bootstrap แบบ minimal (skeleton เท่านั้น)',
                'command': '/be-bootstrap NestJS API project',
                'explanation': 'สร้าง skeleton + health endpoint + Swagger',
            },
            {
                'title': 'Bootstrap แบบ Vibe Mode (full feature)',
                'command': '/be-bootstrap user management API with JWT auth',
                'explanation': 'สร้าง skeleton + Users CRUD + JWT + tests + observability',
            },
            {
                'title': 'Bootstrap with Supabase',
                'command': '/be-bootstrap products API using Supabase JS',
                'explanation': 'AI detect Supabase → ใช้ template nestjs-supabase',
            },
            {
                'title': 'Bootstrap แบบ shell ตรงๆ (ไม่ผ่าน AI)',
                'command': 'APP_NAME=my-api bash .be/scripts/bootstrap.sh nestjs-supabase .',
                'explanation': '~5 sec ไม่ใช้ AI เลย',
            },
        ],
        'outputs': [
            'package.json + tsconfig + nest-cli + ESLint + Prettier',
            'src/main.ts + src/app.module.ts',
            'src/config/ (Zod env validation)',
            'src/modules/health/ (live + ready)',
            'src/modules/{prisma|supabase}/ (DI service)',
            'src/common/{filters, decorators, dto, middleware}',
            'Dockerfile + docker-compose.yml',
            '.env.example (ทุก vars จำเป็น)',
            'Pino structured logging configured',
            'Helmet + CORS + rate limit ready',
            'Swagger UI ที่ /docs',
        ],
        'mistakes': [
            '❌ <b>Run บน folder ที่มีโค้ดอยู่แล้ว</b> — อาจ overwrite ไฟล์เก่า ถ้า bootstrap.sh ใช้ rsync แบบไม่ระวัง',
            '❌ <b>ลืมตั้ง .env</b> — ต้อง <font face="Courier">cp .env.example .env</font> + ใส่ secrets',
            '❌ <b>คาดหวัง MongoDB/MySQL</b> — รองรับแค่ Postgres ตอนนี้',
            '❌ <b>คาดหวัง Express</b> — เป็น NestJS เท่านั้น',
        ],
        'pairs_with': [
            ['/be-test', 'หลัง bootstrap → generate tests + verify build'],
            ['/be-schema', 'ถ้า bootstrap แบบ minimal → ค่อย add entities ทีหลัง'],
            ['/be-api', 'เพิ่ม feature modules หลังมี skeleton'],
        ],
    }


def cmd_be_schema():
    return {
        'title': '/be-schema — ออกแบบ DB Schema',
        'summary': 'สร้าง/แก้ Prisma schema + safe migrations',
        'shortcut': '/be-s',
        'agent': '📐 schema-architect',
        'needs_skeleton': '✅ ต้องมี (มี prisma/schema.prisma)',
        'frequency': '⭐⭐⭐ ทุก entity ใหม่',
        'duration': '~30 sec - 1 min',
        'use_cases': [
            '✅ เพิ่ม entity ใหม่ (User, Product, Order, ฯลฯ)',
            '✅ เพิ่ม column ใน entity ที่มีอยู่',
            '✅ เปลี่ยน relation (1-N → N-N)',
            '✅ เพิ่ม index เพื่อ optimize query',
            '✅ Setup soft delete pattern',
            '✅ เพิ่ม RLS policies',
        ],
        'anti_cases': [
            '❌ ใช้ Supabase JS variant (ไม่มี Prisma) → ออกแบบ schema ใน Supabase Studio แทน',
            '❌ ต้องการแค่ query ไม่แก้ schema → ใช้ /be-api ตรง',
            '❌ ลบ table ในโปรเจกต์ production → ระบบจะปฏิเสธ destructive ops auto-apply',
        ],
        'examples': [
            {
                'title': 'เพิ่ม entity ใหม่',
                'command': '/be-schema add Product entity (name, price, stock, category, isActive)',
                'explanation': 'AI สร้าง model Product พร้อม indexes + migration',
            },
            {
                'title': 'เพิ่ม relation',
                'command': '/be-schema add OrderItems junction between Order and Product',
                'explanation': 'AI สร้าง many-to-many junction table',
            },
            {
                'title': 'Soft delete',
                'command': '/be-schema add soft delete to User',
                'explanation': 'เพิ่ม deletedAt + index + adjust queries',
            },
            {
                'title': 'Performance index',
                'command': '/be-schema add composite index on Order(userId, status, createdAt)',
                'explanation': 'AI วิเคราะห์ query patterns + เพิ่ม index ตามที่เหมาะ',
            },
        ],
        'outputs': [
            'แก้ prisma/schema.prisma',
            'Migration file ใน prisma/migrations/<timestamp>_<name>/',
            'Apply migration: npx prisma migrate dev',
            'Regenerate Prisma client: npx prisma generate',
            'Update .be/memory/schema.md',
            'Indexes ครบ (FK columns + unique + soft delete + query patterns)',
        ],
        'mistakes': [
            '❌ <b>ลืม preview migration</b> — schema-architect จะ <font face="Courier">--create-only</font> ก่อน apply เสมอ ห้าม skip',
            '❌ <b>auto-apply destructive migrations</b> (drop column) — ต้อง confirm 2-phase ก่อน',
            '❌ <b>ไม่ index FK columns</b> — schema-architect บังคับเพิ่มให้',
            '❌ <b>ใช้ Int autoincrement</b> — ใช้ UUID v4 ตามมาตรฐาน becraft',
        ],
        'pairs_with': [
            ['/be-api', 'หลัง schema → /be-api สร้าง CRUD endpoints'],
            ['/be-test', 'หลัง schema + api → /be-test ทดสอบ'],
        ],
    }


def cmd_be_api():
    return {
        'title': '/be-api — สร้าง API Endpoints',
        'summary': 'สร้าง NestJS controller + service + DTOs + OpenAPI สำหรับ resource',
        'shortcut': '/be-a',
        'agent': '🔌 api-builder',
        'needs_skeleton': '✅ ต้องมี (มี src/main.ts + app.module.ts)',
        'frequency': '⭐⭐⭐⭐ ทุก resource — ใช้บ่อยมาก',
        'duration': '~30 sec - 1 min ต่อ resource',
        'use_cases': [
            '✅ สร้าง CRUD endpoints สำหรับ entity ที่มี schema แล้ว',
            '✅ เพิ่ม endpoint เฉพาะ (เช่น POST /orders/:id/cancel)',
            '✅ เพิ่ม search endpoint with filters',
            '✅ เพิ่ม pagination แบบ cursor',
            '✅ เพิ่ม custom action endpoint',
        ],
        'anti_cases': [
            '❌ Folder ว่าง (ไม่มี skeleton) → /be-bootstrap ก่อน',
            '❌ Schema ยังไม่มี → /be-schema ก่อน',
            '❌ ต้องการ GraphQL → becraft รองรับเฉพาะ REST',
            '❌ ต้องการ change auth requirements → /be-auth',
        ],
        'examples': [
            {
                'title': 'CRUD ครบ',
                'command': '/be-api create CRUD for products',
                'explanation': 'POST/GET/GET:id/PATCH/DELETE — ครบ 5 endpoints',
            },
            {
                'title': 'Custom action',
                'command': '/be-api add POST /orders/:id/cancel endpoint',
                'explanation': 'เพิ่ม endpoint เฉพาะ ไม่สร้าง CRUD ทั้งหมด',
            },
            {
                'title': 'Search + filters',
                'command': '/be-api add search to /products with filters: category, minPrice, maxPrice, sort',
                'explanation': 'เพิ่ม endpoint with PaginationDto + FilterDto',
            },
            {
                'title': 'Public read endpoint',
                'command': '/be-api add public GET /products (no auth required)',
                'explanation': 'เพิ่ม @Public() decorator',
            },
        ],
        'outputs': [
            'src/<resource>/dto/{create,update,response}.dto.ts',
            'src/<resource>/<resource>.controller.ts (5 endpoints + OpenAPI)',
            'src/<resource>/<resource>.service.ts (Prisma หรือ Supabase queries)',
            'src/<resource>/<resource>.module.ts',
            'แก้ src/app.module.ts (register module)',
            'class-validator decorators on DTOs',
            'Idempotency-Key header on POST/PUT',
            'Cursor pagination (default)',
            'Soft delete (PATCH /:id with deletedAt)',
            '@Exclude() sensitive fields in response',
            'Update .be/memory/api-registry.md + contracts.md',
        ],
        'mistakes': [
            '❌ <b>ใช้กับ folder ว่าง</b> — api-builder จะแนะนำให้ /be-bootstrap ก่อน',
            '❌ <b>ลืม schema ก่อน</b> — /be-schema ต้องมาก่อน /be-api เสมอ',
            '❌ <b>คาดหวัง GraphQL</b> — รองรับเฉพาะ REST',
            '❌ <b>verbs in URL</b> (เช่น /getUsers) — api-builder ใช้ noun ตาม REST conventions',
        ],
        'pairs_with': [
            ['/be-schema', '*ต้อง*ก่อน /be-api (entity ต้องมี schema)'],
            ['/be-test', 'หลัง /be-api → /be-test สร้าง tests'],
            ['/be-auth', 'ถ้า endpoint ต้อง auth → /be-auth ก่อน'],
        ],
    }


def cmd_be_auth():
    return {
        'title': '/be-auth — Authentication & Authorization',
        'summary': 'JWT + RBAC + rate limiting + idempotency + bcrypt',
        'shortcut': '/be-au',
        'agent': '🛡️ auth-guard',
        'needs_skeleton': '✅ ต้องมี (User entity ใน schema)',
        'frequency': '⭐⭐ ครั้งเดียวต่อ feature',
        'duration': '~1 min',
        'use_cases': [
            '✅ Setup login + register + refresh token',
            '✅ เพิ่ม OAuth (Google, GitHub, etc.)',
            '✅ เพิ่ม role-based access (USER, ADMIN)',
            '✅ Protect endpoints ด้วย @UseGuards',
            '✅ เพิ่ม rate limit on /auth/*',
            '✅ เพิ่ม idempotency middleware',
        ],
        'anti_cases': [
            '❌ User entity ยังไม่มี → /be-schema ก่อน',
            '❌ ต้องการ session-based auth — becraft default = JWT (stateless)',
            '❌ ต้องการ basic auth — ไม่แนะนำใน production',
        ],
        'examples': [
            {
                'title': 'Setup JWT auth',
                'command': '/be-auth setup JWT login/register/refresh',
                'explanation': 'สร้าง 5 endpoints + JWT strategy + guards',
            },
            {
                'title': 'Add Google OAuth',
                'command': '/be-auth add Google OAuth',
                'explanation': 'เพิ่ม Google strategy + callback endpoint',
            },
            {
                'title': 'Add admin role',
                'command': '/be-auth add ADMIN role with @Roles guard',
                'explanation': 'RBAC implementation + admin-only endpoints',
            },
        ],
        'outputs': [
            'src/auth/{module,controller,service}.ts',
            'src/auth/tokens.service.ts (refresh rotation in Redis)',
            'src/auth/strategies/jwt.strategy.ts',
            'src/auth/dto/{register,login,refresh}.dto.ts',
            'src/common/guards/{jwt-auth,roles}.guard.ts',
            'src/common/decorators/{public,roles,current-user}.decorator.ts',
            'Update src/app.module.ts (global guards)',
            'Update .env.example (JWT_SECRET, JWT_REFRESH_SECRET)',
            'Rate limit on /auth/login (5/min) + /auth/register (10/hr)',
            'bcrypt rounds 12 (industry standard)',
            'Constant-time login (no enumeration)',
        ],
        'mistakes': [
            '❌ <b>ลืม set JWT_SECRET</b> — ต้อง <font face="Courier">openssl rand -base64 32</font>',
            '❌ <b>เก็บ refresh token ใน localStorage</b> — auth-guard ใช้ HttpOnly cookies (production)',
            '❌ <b>ไม่ rate limit /login</b> — เปิดช่อง brute force',
            '❌ <b>ใช้ secret เดียวสำหรับ access + refresh</b> — แยกออก 2 ตัว',
        ],
        'pairs_with': [
            ['/be-schema', 'User entity *ต้อง*มีก่อน'],
            ['/be-test', 'หลัง /be-auth → /be-test สำหรับ auth flow'],
            ['/be-api', 'ใช้ @UseGuards ใน controllers ที่ /be-api สร้าง'],
        ],
    }


def cmd_be_observe():
    return {
        'title': '/be-observe — Logs + Metrics + Health',
        'summary': 'Production observability baseline (Pino + Prometheus + Terminus)',
        'shortcut': '/be-o',
        'agent': '📊 observability',
        'needs_skeleton': '✅ ต้องมี',
        'frequency': '⭐ ครั้งเดียวต่อโปรเจกต์',
        'duration': '~30 sec',
        'use_cases': [
            '✅ เตรียม deploy production',
            '✅ ต้องการ Prometheus metrics',
            '✅ ต้องการ Kubernetes-ready health checks (live + ready)',
            '✅ ต้องการ structured JSON logs (queryable)',
            '✅ Setup OpenTelemetry tracing',
            '✅ Setup Sentry error tracking',
        ],
        'anti_cases': [
            '❌ Local development เท่านั้น — log แบบ pretty-print ก็พอ (default ใน becraft)',
            '❌ Project เล็กไม่ deploy — overkill',
        ],
        'examples': [
            {
                'title': 'Production baseline',
                'command': '/be-observe setup logging + metrics',
                'explanation': 'Pino + /metrics + /health/live + /health/ready',
            },
            {
                'title': 'Custom business metrics',
                'command': '/be-observe add custom metrics: orders_total, revenue_total',
                'explanation': 'Counter + Histogram สำหรับ business events',
            },
            {
                'title': 'Enable Sentry',
                'command': '/be-observe enable Sentry error tracking',
                'explanation': 'เพิ่ม Sentry init (ถ้ามี SENTRY_DSN ใน env)',
            },
        ],
        'outputs': [
            'src/observability/metrics.module.ts',
            'src/health/{module,controller}.ts (3 endpoints: /, /live, /ready)',
            'src/common/middleware/request-id.middleware.ts',
            'src/common/interceptors/metrics.interceptor.ts',
            'Pino redact list (PII protection)',
            'Update .env.example (LOG_LEVEL, SENTRY_DSN, OTEL_*)',
            'Default Node.js metrics + HTTP histogram (RED method)',
        ],
        'mistakes': [
            '❌ <b>ลืม redact PII ใน logs</b> — observability config ทำให้แล้ว แต่ตรวจ paths',
            '❌ <b>ใช้ /health เดียวสำหรับทั้ง liveness + readiness</b> — แยก 2 endpoints',
            '❌ <b>console.log ใน production code</b> — Pino logger ทุกที่',
        ],
        'pairs_with': [
            ['/be-test', 'verify endpoints ทำงานหลัง /be-observe'],
        ],
    }


def cmd_be_test():
    return {
        'title': '/be-test — Generate + Run Tests',
        'summary': 'Jest + Supertest + Testcontainers (real DB) + auto-fix loop',
        'shortcut': '/be-t',
        'agent': '🧪 test-runner',
        'needs_skeleton': '✅ ต้องมี',
        'frequency': '⭐⭐⭐⭐ ทุกครั้งหลัง implement',
        'duration': '~1-3 min (ขึ้นกับ test suite)',
        'use_cases': [
            '✅ สร้าง unit tests สำหรับ service ใหม่',
            '✅ สร้าง e2e tests สำหรับ controller',
            '✅ เพิ่ม contract tests vs OpenAPI',
            '✅ Run existing test suite + auto-fix failures',
            '✅ Setup Testcontainers ครั้งแรก',
            '✅ ก่อน deploy production',
        ],
        'anti_cases': [
            '❌ ยังไม่ได้ implement feature → ใช้ /be-api ก่อน',
            '❌ มี bug รู้ตำแหน่งแล้ว → /be-fix ตรงเลย',
        ],
        'examples': [
            {
                'title': 'สร้าง tests สำหรับ feature',
                'command': '/be-test for users module',
                'explanation': 'Unit + e2e tests + auto-fix until pass',
            },
            {
                'title': 'Run existing tests',
                'command': '/be-test run all',
                'explanation': 'รันทั้ง suite + report failures',
            },
            {
                'title': 'Coverage report',
                'command': '/be-test with coverage',
                'explanation': 'รัน + generate coverage report',
            },
        ],
        'outputs': [
            'src/<resource>/<resource>.service.spec.ts (unit, mocked)',
            'test/<resource>.e2e-spec.ts (integration, real DB via Testcontainers)',
            'test/setup-integration.ts (Testcontainers helper)',
            'test/factories/*.ts (faker-based)',
            'jest.config.js + jest-e2e.config.js',
            'Coverage report (target ≥80%)',
            'Auto-fix log (silent — แสดงเฉพาะ final result)',
        ],
        'mistakes': [
            '❌ <b>Mock the database</b> — test-runner ใช้ Testcontainers (real Postgres)',
            '❌ <b>setTimeout ใน tests</b> — ใช้ waitFor pattern',
            '❌ <b>Shared state</b> — ทุก test ใช้ factory + truncate',
            '❌ <b>Skip auth tests</b> — ทั้ง 401 + 403 + valid path',
        ],
        'pairs_with': [
            ['/be-fix', 'ถ้า test fail หลังแก้ → /be-fix'],
            ['/be-api หรือ /be-auth', 'หลัง implement → /be-test ทันที'],
        ],
    }


def cmd_be_fix():
    return {
        'title': '/be-fix — Debug + Fix',
        'summary': 'Diagnose root cause → minimal fix → verify with tests',
        'shortcut': '/be-f',
        'agent': '🧪 test-runner (in fix mode)',
        'needs_skeleton': '✅ ต้องมี',
        'frequency': '⭐⭐⭐ เมื่อมี bug',
        'duration': '~30 sec - 5 min (ขึ้นกับ bug)',
        'use_cases': [
            '✅ Test fail',
            '✅ Build fail',
            '✅ Runtime error (500)',
            '✅ Endpoint คืนค่าผิด (wrong status, wrong shape)',
            '✅ N+1 query (slow endpoint)',
            '✅ Migration drift',
        ],
        'anti_cases': [
            '❌ ต้องการ refactor — /be-fix ทำ minimal fix เท่านั้น',
            '❌ ต้องการ add feature — /be-api แทน',
            '❌ ไม่รู้ว่าอะไรพัง — /be (smart router) ช่วย diagnose ก่อน',
        ],
        'examples': [
            {
                'title': 'Test failure',
                'command': '/be-fix failing test in auth.spec.ts line 42',
                'explanation': 'Reproduce → diagnose → minimal fix → verify',
            },
            {
                'title': 'Build error',
                'command': '/be-fix npm run build fails with TS2345',
                'explanation': 'AI อ่าน error → fix type mismatch',
            },
            {
                'title': 'Slow endpoint',
                'command': '/be-fix N+1 query in /orders endpoint',
                'explanation': 'ใช้ Prisma include หรือ select แทน loop',
            },
            {
                'title': 'Wrong status code',
                'command': '/be-fix POST /users returns 200 instead of 201',
                'explanation': 'แก้ @HttpCode(201)',
            },
        ],
        'outputs': [
            'แก้ไฟล์ที่เกี่ยวข้อง (minimal change)',
            'Run failing test/build → verify pass',
            'Run full suite → no regression',
            'Update .be/memory/changelog.md (logged fix)',
            'Update .be/memory/agents-log.md (auto-fixes)',
        ],
        'mistakes': [
            '❌ <b>ขอให้ refactor surrounding code</b> — /be-fix ทำ minimal fix',
            '❌ <b>ไม่ verify หลัง fix</b> — agent run tests + build เสมอ',
            '❌ <b>Skip root cause</b> — fix symptom = bug returns later',
            '❌ <b>คาดหวังการ explain ละเอียด</b> — agent focus ที่ fix, ไม่ใช่ tutorial',
        ],
        'pairs_with': [
            ['/be-test', 'หลัง /be-fix → /be-test verify ไม่มี regression'],
        ],
    }


# ============================================================
# Real-world Scenarios
# ============================================================

def chapter_scenarios(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 13: Real-world Scenarios', 'Chapter', styles))
    elems.append(H('''บทนี้แสดงลำดับการใช้ commands ใน workflow จริง''', 'Body', styles))

    # Scenario 1
    elems.append(H('13.1 สร้าง User Management API ตั้งแต่ต้น', 'Section', styles))
    elems.append(H('''<b>เป้าหมาย:</b> ระบบจัดการ user พร้อม register, login, profile CRUD''', 'Body', styles))

    elems.append(H('<b>Workflow:</b>', 'SubSection', styles))
    elems.append(code_block('''Step 1: เตรียม folder
$ mkdir user-api && cd user-api
$ npx -y github:phitsanu07/becraft#v0.4.1 install --quick

Step 2: Bootstrap (one-shot)
$ claude .
> /be-bootstrap user management API with JWT auth and profile CRUD

AI จะทำให้:
- Phase 1: 📋 plan วางแผน 5 phases
- Phase 2: 🏗️ bootstrap-agent สร้าง skeleton (~5s)
- Phase 3: 📐 schema-architect สร้าง User entity
- Phase 4: 🔌 api-builder + 🛡️ auth-guard (parallel)
- Phase 5: 📊 observability + 🧪 test-runner

Step 3: ตั้ง .env
$ cp .env.example .env
$ echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
$ echo "JWT_REFRESH_SECRET=$(openssl rand -base64 32)" >> .env

Step 4: Run
$ docker-compose up -d postgres redis
$ npx prisma migrate dev
$ npm install && npm run start:dev

Step 5: Verify
$ curl http://localhost:3000/health
$ open http://localhost:3000/docs

Total time: ~10 นาที (ส่วนใหญ่เป็น npm install)'''))

    # Scenario 2
    elems.append(H('13.2 เพิ่ม Products feature ในโปรเจกต์ที่มีอยู่', 'Section', styles))
    elems.append(H('''<b>เป้าหมาย:</b> โปรเจกต์มี User + Auth แล้ว ต้องการเพิ่ม Products CRUD''', 'Body', styles))

    elems.append(code_block('''Step 1: ออกแบบ schema
> /be-schema add Product (name, price, stock, category, isActive)

AI:
- Add Product model to prisma/schema.prisma
- Generate migration
- Apply: npx prisma migrate dev
- Update .be/memory/schema.md

Step 2: สร้าง endpoints
> /be-api create CRUD for products with public GET endpoints

AI:
- src/products/{module,controller,service}.ts
- src/products/dto/{create,update,response}.dto.ts
- @Public() on GET endpoints
- @UseGuards(JwtAuthGuard) on POST/PATCH/DELETE
- Update src/app.module.ts

Step 3: Tests
> /be-test for products module

AI:
- src/products/products.service.spec.ts (unit)
- test/products.e2e-spec.ts (integration)
- Run: npm test
- Auto-fix any failures
- Coverage report

Step 4: Verify
$ open http://localhost:3000/docs
$ curl http://localhost:3000/api/v1/products

Total time: ~5-10 นาที'''))

    # Scenario 3
    elems.append(H('13.3 เพิ่ม Google OAuth ในระบบที่มี JWT แล้ว', 'Section', styles))
    elems.append(code_block('''Step 1:
> /be-auth add Google OAuth

AI:
- Install passport-google-oauth20
- src/auth/strategies/google.strategy.ts
- Add /auth/google + /auth/google/callback endpoints
- Update User entity (add googleId field)
- Migration: npx prisma migrate dev
- Update .env.example: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

Step 2: ตั้ง credentials
$ # Get from https://console.cloud.google.com
$ echo "GOOGLE_CLIENT_ID=..." >> .env
$ echo "GOOGLE_CLIENT_SECRET=..." >> .env

Step 3: Test
> /be-test for Google OAuth flow

Step 4: Verify
$ curl http://localhost:3000/api/v1/auth/google
# → redirect to Google consent screen'''))

    # Scenario 4
    elems.append(H('13.4 Fix failing tests + debug', 'Section', styles))
    elems.append(code_block('''สถานการณ์: หลัง refactor มี tests fail

Step 1: Run + identify
$ npm test
> 3 failing tests in users.e2e-spec.ts

Step 2: Fix
> /be-fix failing tests in users.e2e-spec.ts after refactor

AI:
- อ่าน test failures
- อ่าน recent changes (git diff หรือ changelog)
- Identify root cause (DTO field renamed)
- Apply minimal fix
- Run tests → verify pass
- Run full suite → no regression
- Build → no errors

Step 3: Confirm
$ npm test
> All tests pass ✓

Time: ~1-2 นาที'''))

    # Scenario 5
    elems.append(H('13.5 เตรียม deploy production', 'Section', styles))
    elems.append(code_block('''Step 1: Add production observability
> /be-observe setup full stack (logs + metrics + Sentry + tracing)

AI:
- Pino with redact list
- /metrics endpoint
- /health/live + /health/ready
- Sentry (if SENTRY_DSN set)
- OpenTelemetry (if OTEL_* set)

Step 2: Verify all tests pass
> /be-test run all with coverage

AI:
- Run full suite
- Auto-fix any flaky tests
- Coverage ≥80%

Step 3: Build production image
$ docker build -t user-api:v1 .
$ docker run -p 3000:3000 --env-file .env user-api:v1

Step 4: Smoke test
$ curl http://localhost:3000/health/live
$ curl http://localhost:3000/health/ready
$ curl http://localhost:3000/metrics

Step 5: Push to registry + deploy
$ docker tag user-api:v1 registry.example.com/user-api:v1
$ docker push registry.example.com/user-api:v1
# Deploy ตาม infra (Kubernetes, Railway, Fly.io, etc.)'''))

    return elems


# ============================================================
# Common Mistakes
# ============================================================

def chapter_mistakes(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 14: Common Mistakes', 'Chapter', styles))
    elems.append(H('''ความผิดพลาดที่พบบ่อยจากการใช้ becraft ที่ผ่านมา''', 'Body', styles))

    mistakes = [
        ('1. ใช้ /be-api กับ folder ว่าง',
         '''❌ User: <font face="Courier">/be-api create products endpoint</font> (ใน folder ว่าง)
✅ ใช้ <font face="Courier">/be-bootstrap</font> ก่อน → จากนั้นค่อย <font face="Courier">/be-api</font>'''),

        ('2. ลืมตั้ง .env หลัง bootstrap',
         '''❌ Run <font face="Courier">npm run start:dev</font> ทันที → ZodError: SUPABASE_URL is required
✅ Always: <font face="Courier">cp .env.example .env</font> → แก้ secrets → <font face="Courier">npm run start:dev</font>'''),

        ('3. ใช้ /be-api ก่อน /be-schema',
         '''❌ <font face="Courier">/be-api create CRUD for products</font> (ไม่มี Product model)
✅ <font face="Courier">/be-schema add Product</font> → จากนั้น <font face="Courier">/be-api</font>'''),

        ('4. คาดหวัง MySQL/MongoDB',
         '''❌ "ใช้ MySQL ได้ไหม?" — becraft รองรับเฉพาะ Postgres
✅ ใช้ Postgres หรือ Supabase แทน, หรือ port becraft (effort สูง)'''),

        ('5. Mock database ใน integration tests',
         '''❌ Mock PrismaService ใน e2e tests → tests pass but production breaks
✅ test-runner ใช้ Testcontainers (real Postgres) — ไม่ override default'''),

        ('6. ลืม run /be-test หลัง implement',
         '''❌ /be-api → push to git ทันที
✅ /be-api → /be-test → verify → push'''),

        ('7. ใช้ /be-fix แทน /be-api',
         '''❌ <font face="Courier">/be-fix add new endpoint /products/search</font>
✅ <font face="Courier">/be-api add search endpoint</font> (เพิ่ม feature, ไม่ใช่แก้ bug)'''),

        ('8. คาดหวังว่า /be-bootstrap จะรองรับ stack อื่น',
         '''❌ <font face="Courier">/be-bootstrap with Express + MongoDB</font>
✅ becraft v0.4 รองรับเฉพาะ NestJS + Postgres (Prisma หรือ Supabase JS)'''),

        ('9. Bypass quality gate',
         '''❌ "Skip tests, deploy เลย"
✅ ทุก agent มี quality gate (build + lint) ก่อน "done" — ห้าม override'''),

        ('10. ไม่อ่าน workflow plan ที่ /be แสดง',
         '''❌ พิมพ์ "Go" โดยไม่อ่าน plan
✅ Plan มี file count + agents ใช้ + estimated time → check ก่อน Go'''),

        ('11. Run /be-bootstrap ทับ folder ที่มีโค้ด',
         '''❌ rsync จะ overwrite ไฟล์เก่า
✅ /be-bootstrap ต้องใน folder ใหม่/ว่างเท่านั้น'''),

        ('12. คาดหวัง AI ตอบทันทีโดยไม่มีบริบท',
         '''❌ <font face="Courier">/be-fix it</font> (ไม่บอกว่าอะไรพัง)
✅ <font face="Courier">/be-fix endpoint /users returns 500 with stack trace ...</font>'''),
    ]

    for title, content in mistakes:
        elems.append(H(title, 'SubSection', styles))
        elems.append(Paragraph(content, styles['Mistake']))

    return elems


# ============================================================
# Cheat Sheet
# ============================================================

def chapter_cheatsheet(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 15: Cheat Sheet — สรุป 1 หน้า', 'Chapter', styles))

    elems.append(H('🚀 Quick Reference', 'Section', styles))

    quick = [
        ['สถานการณ์', 'Command', 'หลังจากนั้น'],
        ['เริ่มโปรเจกต์ใหม่', '/be-bootstrap', '+ /be-test'],
        ['เพิ่ม entity ใหม่', '/be-schema', '+ /be-api + /be-test'],
        ['เพิ่ม CRUD endpoints', '/be-api', '+ /be-test'],
        ['เพิ่ม login/register', '/be-auth', '+ /be-test'],
        ['เตรียม production', '/be-observe', '+ /be-test'],
        ['Test fail / build fail', '/be-fix', '+ /be-test'],
        ['งานใหญ่ ไม่แน่ใจ', '/be-plan', 'รอ confirm → execute'],
        ['ทำงานทั่วไป', '/be (anything)', '-'],
        ['ลืม commands', '/be-help', '-'],
    ]
    elems.append(make_table(quick, col_widths=[5 * cm, 4.5 * cm, 6.5 * cm], font_size=9.5))

    elems.append(H('📋 Pre-Flight Checklist (ก่อนรัน command ทุกครั้ง)', 'Section', styles))
    bullets = [
        '☐ Stack ระบุชัดเจนหรือยัง? (Prisma / Supabase JS)',
        '☐ Folder state ตรงกับ command? (greenfield → /be-bootstrap; existing → others)',
        '☐ ถ้าเป็น /be-api: schema entity มีหรือยัง?',
        '☐ ถ้าเป็น /be-auth: User model มีหรือยัง?',
        '☐ .env มี secrets ครบ? (DATABASE_URL, JWT_SECRET, etc.)',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('🎯 Workflow Templates', 'Section', styles))

    elems.append(H('<b>A) New Project (Greenfield)</b>', 'SubSection', styles))
    elems.append(code_block('''mkdir my-api && cd my-api
npx -y github:phitsanu07/becraft#v0.4.1 install --quick
claude .
> /be-bootstrap user management API with JWT
> # ตั้ง .env, run npm install, npm run start:dev'''))

    elems.append(H('<b>B) Add Resource (Existing project)</b>', 'SubSection', styles))
    elems.append(code_block('''> /be-schema add Product (name, price, stock)
> /be-api create CRUD for products
> /be-test for products'''))

    elems.append(H('<b>C) Production Hardening</b>', 'SubSection', styles))
    elems.append(code_block('''> /be-observe setup logs + metrics + Sentry
> /be-test run all with coverage
> # Build + push image + deploy'''))

    elems.append(H('🆘 When in doubt', 'Section', styles))
    elems.append(Paragraph('''<b>ถ้าไม่แน่ใจว่าจะใช้ command ไหน → ใช้ <font face="Courier">/be</font>
แล้วบอกสิ่งที่อยากได้เป็นภาษาธรรมชาติ</b><br/><br/>
ตัวอย่าง:<br/>
• <font face="Courier">/be สร้างระบบ booking ห้องประชุม</font><br/>
• <font face="Courier">/be แก้ test ที่ fail</font><br/>
• <font face="Courier">/be ทำต่อจากเมื่อวาน</font><br/>
<br/>
AI จะวิเคราะห์ + เลือก command ที่ถูก + แสดง plan ก่อน execute''', styles['Tip']))

    # Closing
    elems.append(PageBreak())
    elems.append(Spacer(1, 4 * cm))
    elems.append(Paragraph('🛠️ becraft', styles['Title']))
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(Paragraph('Commands Guide v0.4.1', styles['Subtitle']))
    elems.append(Spacer(1, 2 * cm))
    elems.append(Paragraph('สับสน หาย รู้ตอนนี้ใช้อะไร เมื่อไหร่ ทำไม',
                            styles['BodyCenter']))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph('ขอให้สนุกกับการ craft production backends!',
                            styles['BodyCenter']))

    return elems


# ============================================================
# Build PDF
# ============================================================

def build_pdf():
    styles = get_styles()

    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title='becraft — Commands Guide',
        author='becraft team',
        subject='Detailed guide for becraft 10 commands with use cases',
    )

    cover_frame = Frame(
        0, 0, A4[0], A4[1],
        leftPadding=2 * cm, rightPadding=2 * cm,
        topPadding=2 * cm, bottomPadding=2 * cm,
        id='cover',
    )
    body_frame = Frame(
        2 * cm, 1.8 * cm,
        A4[0] - 4 * cm, A4[1] - 4 * cm,
        id='body',
    )

    cover_template = PageTemplate(id='cover', frames=[cover_frame], onPage=cover_page)
    body_template = PageTemplate(id='body', frames=[body_frame], onPage=page_header_footer)

    doc.addPageTemplates([cover_template, body_template])

    story = []

    # Cover + TOC
    story.extend(build_cover(styles))
    story.append(NextPageTemplate('body'))
    story.append(PageBreak())
    story.extend(build_toc(styles))

    # Content
    story.extend(chapter_intro(styles))
    story.extend(chapter_overview(styles))
    story.extend(chapter_decision_tree(styles))

    # Per-command chapters (3-12)
    commands = [
        cmd_be(),
        cmd_be_help(),
        cmd_be_plan(),
        cmd_be_bootstrap(),
        cmd_be_schema(),
        cmd_be_api(),
        cmd_be_auth(),
        cmd_be_observe(),
        cmd_be_test(),
        cmd_be_fix(),
    ]
    for i, cmd in enumerate(commands, start=3):
        story.extend(make_command_chapter(i, cmd, styles))

    # Final chapters
    story.extend(chapter_scenarios(styles))
    story.extend(chapter_mistakes(styles))
    story.extend(chapter_cheatsheet(styles))

    doc.build(story)
    print(f"✅ Generated: {OUTPUT}")
    print(f"   Size: {OUTPUT.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    build_pdf()
