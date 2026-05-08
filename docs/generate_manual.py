"""
Generate becraft user manual (Thai) as PDF.
Uses reportlab + Sarabun font.

Run:
    python3 generate_manual.py
"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, NextPageTemplate, Image
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas

# ============================================================
# Setup
# ============================================================

BASE = Path(__file__).parent
FONTS = BASE / "fonts"
OUTPUT = BASE / "becraft-คู่มือการใช้งาน.pdf"

# Register Thai fonts
pdfmetrics.registerFont(TTFont('Sarabun', str(FONTS / 'Sarabun-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Bold', str(FONTS / 'Sarabun-Bold.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Italic', str(FONTS / 'Sarabun-Italic.ttf')))
pdfmetrics.registerFont(TTFont('Sarabun-Light', str(FONTS / 'Sarabun-Light.ttf')))

# Colors
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
CODE_BG = HexColor('#1E293B')
CODE_FG = HexColor('#F1F5F9')

# ============================================================
# Styles
# ============================================================

def get_styles():
    s = {}
    s['Title'] = ParagraphStyle(
        name='Title', fontName='Sarabun-Bold', fontSize=32, leading=40,
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=12,
    )
    s['Subtitle'] = ParagraphStyle(
        name='Subtitle', fontName='Sarabun-Light', fontSize=16, leading=22,
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
        name='Code', fontName='Courier', fontSize=9, leading=13,
        textColor=CODE_FG, backColor=CODE_BG,
        leftIndent=10, rightIndent=10, spaceAfter=8, spaceBefore=4,
        borderPadding=(8, 8, 8, 8),
    )
    s['Inline'] = ParagraphStyle(
        name='Inline', fontName='Courier', fontSize=9.5, leading=14,
        textColor=DARK,
    )
    s['Note'] = ParagraphStyle(
        name='Note', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=8, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#FEF3C7'),
    )
    s['Warning'] = ParagraphStyle(
        name='Warning', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=8, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#FEE2E2'),
    )
    s['Tip'] = ParagraphStyle(
        name='Tip', fontName='Sarabun', fontSize=10, leading=14,
        textColor=DARK, alignment=TA_LEFT, spaceAfter=8, spaceBefore=4,
        leftIndent=10, rightIndent=10, borderPadding=(8, 8, 8, 8),
        backColor=HexColor('#D1FAE5'),
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


# ============================================================
# Helpers
# ============================================================

def code_block(text):
    """Render code block with monospace font + dark bg."""
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('\n', '<br/>')
    text = text.replace(' ', '&nbsp;')
    return Paragraph(text, get_styles()['Code'])


def make_table(data, col_widths=None, header=True, align='LEFT'):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths, hAlign=align)
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Sarabun'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
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
            ('FONTSIZE', (0, 0), (-1, 0), 10),
        ])
        # Alternate row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), GRAY_BG))
    t.setStyle(TableStyle(style))
    return t


def page_header_footer(canvas, doc):
    """Footer with page number."""
    canvas.saveState()
    canvas.setFont('Sarabun', 8)
    canvas.setFillColor(GRAY)

    # Footer
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.drawString(2 * cm, 1.0 * cm, 'becraft — คู่มือการใช้งาน')
    canvas.drawRightString(A4[0] - 2 * cm, 1.0 * cm, f'หน้า {doc.page}')

    # Header
    canvas.setFont('Sarabun-Light', 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, 'becraft v0.1.0')
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm,
                            'Contract-Driven Backend Development')
    canvas.line(2 * cm, A4[1] - 1.5 * cm, A4[0] - 2 * cm, A4[1] - 1.5 * cm)

    canvas.restoreState()


def cover_page(canvas, doc):
    """Cover page (no header/footer)."""
    canvas.saveState()

    # Background gradient effect (top stripe)
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, A4[1] - 4 * cm, A4[0], 4 * cm, fill=1, stroke=0)

    # Bottom stripe
    canvas.setFillColor(SECONDARY)
    canvas.rect(0, 0, A4[0], 1.5 * cm, fill=1, stroke=0)

    canvas.restoreState()


# ============================================================
# Content blocks
# ============================================================

def H(text, style='Body', styles=None):
    if styles is None:
        styles = get_styles()
    return Paragraph(text, styles[style])


def build_cover(styles):
    elems = []
    elems.append(Spacer(1, 4 * cm))
    elems.append(Paragraph('becraft', styles['Title']))
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(Paragraph('Contract-Driven Backend Development Framework',
                            styles['Subtitle']))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(Paragraph('"Craft Production Backends, Not Prototypes"',
                            styles['Subtitle']))
    elems.append(Spacer(1, 4 * cm))

    elems.append(Paragraph('คู่มือการใช้งานฉบับสมบูรณ์',
                            ParagraphStyle('Cover', fontName='Sarabun-Bold',
                                            fontSize=24, leading=28,
                                            textColor=DARK, alignment=TA_CENTER)))
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(Paragraph('ฉบับภาษาไทย', styles['CoverInfo']))
    elems.append(Spacer(1, 5 * cm))

    elems.append(Paragraph('สำหรับ Claude Code & Google Antigravity', styles['CoverInfo']))
    elems.append(Spacer(1, 0.2 * cm))
    elems.append(Paragraph('NestJS + PostgreSQL + Prisma', styles['CoverInfo']))
    elems.append(Spacer(1, 0.2 * cm))
    elems.append(Paragraph('Version 0.1.0 • 2026', styles['CoverInfo']))
    return elems


def build_toc(styles):
    elems = [
        H('สารบัญ', 'Chapter', styles),
        Spacer(1, 6),
    ]
    chapters = [
        ('คำนำ', 1),
        ('บทที่ 1: ทำความรู้จัก becraft', 2),
        ('  1.1 becraft คืออะไร', 1),
        ('  1.2 ปรัชญา Contract-Driven Development', 1),
        ('  1.3 ใครควรใช้ becraft', 1),
        ('  1.4 ความแตกต่างจาก toh-framework', 1),
        ('บทที่ 2: เครื่องมือที่ต้องเตรียม', 2),
        ('  2.1 Node.js 22+', 1),
        ('  2.2 Docker (สำหรับฐานข้อมูล)', 1),
        ('  2.3 Claude Code', 1),
        ('  2.4 Google Antigravity', 1),
        ('  2.5 Git + GitHub', 1),
        ('บทที่ 3: การติดตั้ง becraft', 2),
        ('  3.1 ติดตั้งจาก GitHub (แนะนำ)', 1),
        ('  3.2 ติดตั้งจาก NPM', 1),
        ('  3.3 ติดตั้งแบบ local development', 1),
        ('  3.4 ตรวจสอบหลังติดตั้ง', 1),
        ('บทที่ 4: โครงสร้างหลังติดตั้ง', 2),
        ('  4.1 ไดเรกทอรีที่ถูกสร้าง', 1),
        ('  4.2 บทบาทของแต่ละโฟลเดอร์', 1),
        ('  4.3 ไฟล์ CLAUDE.md และ AGENT.md', 1),
        ('บทที่ 5: คำสั่งทั้ง 10 ตัว', 2),
        ('  5.1 /be — Smart Router', 1),
        ('  5.2 /be-help', 1),
        ('  5.3 /be-plan', 1),
        ('  5.4 /be-bootstrap', 1),
        ('  5.5 /be-schema', 1),
        ('  5.6 /be-api', 1),
        ('  5.7 /be-auth', 1),
        ('  5.8 /be-observe', 1),
        ('  5.9 /be-test', 1),
        ('  5.10 /be-fix', 1),
        ('บทที่ 6: Tutorial — สร้าง User Management API', 2),
        ('  6.1 ขั้นตอนทั้งหมดแบบ end-to-end', 1),
        ('  6.2 การตั้งค่า environment', 1),
        ('  6.3 การรันและทดสอบ API', 1),
        ('บทที่ 7: ระบบ Memory (9 ไฟล์)', 2),
        ('  7.1 ทำไมต้องมี memory', 1),
        ('  7.2 บทบาทของแต่ละไฟล์', 1),
        ('  7.3 Cross-IDE synchronization', 1),
        ('บทที่ 8: 6 Agents เข้าใจการทำงาน', 2),
        ('  8.1 plan-orchestrator (THE BRAIN)', 1),
        ('  8.2 schema-architect', 1),
        ('  8.3 api-builder', 1),
        ('  8.4 auth-guard', 1),
        ('  8.5 observability', 1),
        ('  8.6 test-runner', 1),
        ('บทที่ 9: 10 Skills', 2),
        ('บทที่ 10: Tech Stack อธิบายลึก', 2),
        ('บทที่ 11: Best Practices', 2),
        ('บทที่ 12: FAQ + Troubleshooting', 2),
        ('บทที่ 13: คำสั่งสรุปแบบรวดเร็ว (Cheat Sheet)', 2),
    ]
    for title, level in chapters:
        st = 'TOC1' if level == 2 else 'TOC2'
        elems.append(Paragraph(title, styles[st]))
    return elems


# ============================================================
# Chapter 1
# ============================================================

def chapter_1(styles):
    elems = []
    elems.append(H('คำนำ', 'Chapter', styles))
    elems.append(H('''ขอบคุณที่เลือกใช้ <b>becraft</b> — เฟรมเวิร์ก AI-orchestrated
สำหรับสร้าง Backend ระดับ production โดยใช้ Claude Code และ Google Antigravity เป็น IDE หลัก''', 'Body', styles))
    elems.append(H('''คู่มือฉบับนี้จะพาคุณตั้งแต่ติดตั้งครั้งแรก ไปจนถึงการสร้าง API
ที่พร้อมขึ้น production ภายในไม่กี่นาที โดยไม่ต้องเขียนโค้ดเองสักบรรทัด — แค่พิมพ์คำสั่ง
ในภาษาธรรมชาติ AI agents จะออกแบบ schema, สร้าง endpoints, ตั้งค่า authentication,
เขียน tests, และเพิ่ม observability ให้ครบถ้วน''', 'Body', styles))
    elems.append(Paragraph('''<b>เหมาะสำหรับใคร?</b> Solo Developer, Solopreneur,
Startup Founder, Freelancer ที่อยากส่งมอบ backend ที่ใช้งานได้จริงให้ลูกค้า
โดยไม่ต้องสะสมประสบการณ์หลายปีก่อน''', styles['Body']))

    elems.append(PageBreak())

    elems.append(H('บทที่ 1: ทำความรู้จัก becraft', 'Chapter', styles))

    elems.append(H('1.1 becraft คืออะไร', 'Section', styles))
    elems.append(H('''<b>becraft</b> คือเฟรมเวิร์กที่นำเทคนิค "AI Agent Orchestration"
มาใช้กับงาน <b>backend development</b> โดยตรง แทนที่จะให้คุณเป็นคนเขียน boilerplate code
หรือออกแบบโครงสร้างเอง becraft ติดตั้ง <b>"ทีม AI agents"</b> เข้าไปใน IDE ของคุณ
ที่จะทำงานกันเหมือนทีมพัฒนาจริง:''', 'Body', styles))

    bullets = [
        '• <b>Plan Orchestrator</b> — วิเคราะห์ความต้องการ วางแผน orchestrate agents อื่นๆ',
        '• <b>Schema Architect</b> — ออกแบบฐานข้อมูล PostgreSQL พร้อม Prisma migrations',
        '• <b>API Builder</b> — สร้าง endpoints, DTOs, OpenAPI documentation',
        '• <b>Auth Guard</b> — JWT, RBAC, rate limiting, password hashing',
        '• <b>Observability</b> — logging, metrics, health checks, tracing',
        '• <b>Test Runner</b> — เขียนและรัน tests พร้อม auto-fix loop',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(Spacer(1, 8))
    elems.append(H('''<b>เป้าหมาย:</b> พิมพ์คำสั่งเดียว ได้ backend พร้อม deploy ทันที''',
                    'Body', styles))

    elems.append(H('1.2 ปรัชญา Contract-Driven Development (CDD)', 'Section', styles))
    elems.append(H('''becraft ยึดหลัก <b>"Contract First, Code Second, Production Third"</b>
ซึ่งหมายความว่า:''', 'Body', styles))

    elems.append(H('''<b>1. Contract First</b> — เขียน OpenAPI spec, DTOs, error schema
ก่อนเริ่มเขียนโค้ด เพื่อให้ team (รวมถึง front-end ที่จะมาเชื่อม) เห็น
"สัญญา" ของ API ชัดเจนก่อน''', 'Body', styles))

    elems.append(H('''<b>2. Schema Derived</b> — โครงสร้างฐานข้อมูลถูกออกแบบจาก
TypeScript types/DTOs ที่กำหนดไว้ ไม่ใช่ในทางตรงกันข้าม
ทำให้โค้ดและฐานข้อมูล type-safe ตั้งแต่ต้นจนจบ''', 'Body', styles))

    elems.append(H('''<b>3. Test Pyramid Mandatory</b> — ทุกฟีเจอร์ต้องมี Unit Tests +
Integration Tests (ใช้ Testcontainers) + Contract Tests
ไม่มีการ "เพิ่ม tests ทีหลัง"''', 'Body', styles))

    elems.append(H('''<b>4. Production Baseline</b> — ทุก API endpoint ที่ถูกสร้าง
จะมาพร้อม structured logs, Prometheus metrics, health checks, rate limiting,
idempotency keys, และ RFC 7807 error format โดยอัตโนมัติ''', 'Body', styles))

    elems.append(H('''<b>5. Self-Healing</b> — เมื่อมี TypeScript errors, build errors,
หรือ test failures, AI agents จะแก้เองอัตโนมัติ (silent loop, max 5 attempts)
ผู้ใช้เห็นแต่ผลลัพธ์ที่สำเร็จ''', 'Body', styles))

    elems.append(H('1.3 ใครควรใช้ becraft', 'Section', styles))
    target_data = [
        ['ประเภทผู้ใช้', 'ทำไมเหมาะ'],
        ['Solo Developer', 'สร้าง SaaS แบบมือเดียวได้โดยไม่ต้องเป็นผู้เชี่ยวชาญทุกด้าน'],
        ['Solopreneur', 'สร้าง MVP ภายในวันเดียวเพื่อทดสอบตลาด'],
        ['Startup Founder', 'สร้าง prototype ที่ใช้งานได้จริงให้นักลงทุนดู'],
        ['Freelancer', 'ส่งมอบงานลูกค้าได้เร็วขึ้น 10 เท่า'],
        ['Backend Engineer', 'ลด boilerplate, focus ที่ business logic'],
        ['Tech Lead', 'มี standard ที่ทีมยึดได้ตั้งแต่วันแรก'],
    ]
    elems.append(make_table(target_data, col_widths=[5 * cm, 11 * cm]))

    elems.append(H('1.4 ความแตกต่างจาก toh-framework', 'Section', styles))
    elems.append(H('''<b>becraft</b> ได้แรงบันดาลใจจาก <b>toh-framework</b> ของคุณ
Wasin Treesinthuros ซึ่งเน้น <b>frontend</b> (Next.js + UI generation)
แต่ becraft ปรับ pattern เดียวกันสำหรับ <b>backend</b>:''', 'Body', styles))

    diff_data = [
        ['ด้าน', 'toh-framework', 'becraft'],
        ['โฟกัส', 'Frontend (Next.js)', 'Backend (NestJS)'],
        ['ปรัชญา', 'UI First', 'Contract First'],
        ['Stack', 'Next.js + Tailwind + shadcn', 'NestJS + Prisma + Postgres'],
        ['Premium baseline', 'Animations, multi-page', 'Logs, metrics, idempotency'],
        ['Mock data', 'Thai/EN names', 'Factories + seed scripts'],
        ['Anti-patterns', 'Purple gradients', 'console.log in prod, missing rate limit'],
        ['Output', 'localhost:3000 (UI)', 'localhost:3000/docs (API)'],
        ['Agents', '7 (UI + Dev + Backend...)', '6 (Schema + API + Auth...)'],
    ]
    elems.append(make_table(diff_data, col_widths=[3.5 * cm, 6 * cm, 6 * cm]))

    return elems


# ============================================================
# Chapter 2
# ============================================================

def chapter_2(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 2: เครื่องมือที่ต้องเตรียม', 'Chapter', styles))

    elems.append(H('''ก่อนเริ่มใช้ becraft คุณต้องติดตั้งเครื่องมือต่อไปนี้บนเครื่อง
ของคุณก่อน''', 'Body', styles))

    elems.append(H('2.1 Node.js 22 LTS', 'Section', styles))
    elems.append(H('''becraft ต้องการ Node.js เวอร์ชัน 22 ขึ้นไป (Long Term Support).
Node.js เป็น JavaScript runtime ที่ใช้รัน becraft CLI และ NestJS server''',
                    'Body', styles))
    elems.append(H('<b>การติดตั้งบน macOS:</b>', 'SubSection', styles))
    elems.append(code_block('# วิธีที่ 1: ใช้ Homebrew (แนะนำ)\nbrew install node@22\n\n# วิธีที่ 2: ใช้ nvm (สามารถสลับเวอร์ชันได้)\ncurl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash\nnvm install 22\nnvm use 22\n\n# ตรวจสอบ\nnode --version   # ควรขึ้น v22.x.x\nnpm --version'))

    elems.append(H('<b>การติดตั้งบน Windows:</b>', 'SubSection', styles))
    elems.append(code_block('# ดาวน์โหลด installer จาก https://nodejs.org/\n# เลือก LTS version (22.x)\n# หรือใช้ winget:\nwinget install OpenJS.NodeJS.LTS'))

    elems.append(H('2.2 Docker + Docker Compose', 'Section', styles))
    elems.append(H('''Docker ใช้สำหรับรัน PostgreSQL และ Redis ในเครื่องของคุณ
โดยไม่ต้องติดตั้งฐานข้อมูลตรงๆ''', 'Body', styles))

    elems.append(H('<b>macOS:</b>', 'SubSection', styles))
    elems.append(code_block('# ดาวน์โหลด Docker Desktop:\n# https://www.docker.com/products/docker-desktop/\n\n# หรือใช้ Homebrew:\nbrew install --cask docker\n\n# ตรวจสอบ\ndocker --version\ndocker compose version'))

    elems.append(Paragraph('''<b>หลังติดตั้ง</b> เปิดแอป Docker Desktop และรอจน status
เป็น "Engine running" ก่อนใช้งาน''', styles['Note']))

    elems.append(H('2.3 Claude Code (Anthropic)', 'Section', styles))
    elems.append(H('''<b>Claude Code</b> เป็น AI coding tool ของ Anthropic
ที่รองรับ becraft แบบ native — สามารถ delegate งานไปยัง sub-agents
และทำงาน parallel ได้จริง''', 'Body', styles))

    elems.append(H('<b>ขั้นตอนการติดตั้ง:</b>', 'SubSection', styles))

    install_cc = [
        ['1', 'ไปที่ https://claude.com/code'],
        ['2', 'สมัคร Anthropic account (ถ้ายังไม่มี)'],
        ['3', 'ติดตั้ง Claude Code CLI: <font face="Courier">npm install -g @anthropic-ai/claude-code</font>'],
        ['4', 'Login: <font face="Courier">claude login</font>'],
        ['5', 'ทดสอบ: <font face="Courier">claude --version</font>'],
    ]
    elems.append(make_table(install_cc, col_widths=[1.5 * cm, 14.5 * cm], header=False))

    elems.append(H('<b>การเริ่มใช้งาน Claude Code ใน project:</b>', 'SubSection', styles))
    elems.append(code_block('cd your-project\nclaude .          # เปิด Claude Code ในโฟลเดอร์นี้\n\n# ในหน้า REPL พิมพ์คำสั่ง /be-* เพื่อใช้ becraft'))

    elems.append(H('2.4 Google Antigravity', 'Section', styles))
    elems.append(H('''<b>Google Antigravity</b> เป็น AI IDE จาก Google
รองรับ becraft ผ่าน <b>workflows</b> ที่ pre-bundled มาให้แล้ว
(self-contained: agents และ skills ถูก inline เข้าไปในไฟล์เดียว)''',
                    'Body', styles))

    elems.append(H('<b>ขั้นตอน:</b>', 'SubSection', styles))

    install_ag = [
        ['1', 'ดาวน์โหลด Antigravity จาก https://labs.google/antigravity'],
        ['2', 'ติดตั้งและ login ด้วย Google account'],
        ['3', 'เปิด project ที่ติดตั้ง becraft แล้ว'],
        ['4', 'พิมพ์ <font face="Courier">/</font> ในหน้าต่าง chat — จะเห็น <font face="Courier">/be-*</font> commands'],
    ]
    elems.append(make_table(install_ag, col_widths=[1.5 * cm, 14.5 * cm], header=False))

    elems.append(Paragraph('''<b>หมายเหตุ:</b> command syntax เหมือน Claude Code
(<font face="Courier">/be-vibe</font>, <font face="Courier">/be-api</font>) — ใช้ขีดกลาง ไม่ใช่ทวิภาค''', styles['Tip']))

    elems.append(H('2.5 Git + GitHub', 'Section', styles))
    elems.append(H('''Git ใช้สำหรับ version control และ deploy code
GitHub ใช้สำหรับ host repository (ทั้ง becraft framework เองและ project ของคุณ)''',
                    'Body', styles))
    elems.append(code_block('# ตรวจสอบ\ngit --version\n\n# ตั้งค่าครั้งแรก\ngit config --global user.name "Your Name"\ngit config --global user.email "you@example.com"\n\n# Login GitHub CLI (optional)\nbrew install gh\ngh auth login'))

    return elems


# ============================================================
# Chapter 3
# ============================================================

def chapter_3(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 3: การติดตั้ง becraft', 'Chapter', styles))
    elems.append(H('''มี 3 วิธีในการติดตั้ง becraft ลงในโปรเจกต์ของคุณ
แต่ละวิธีเหมาะกับสถานการณ์ต่างกัน''', 'Body', styles))

    elems.append(H('3.1 ติดตั้งจาก GitHub (แนะนำ)', 'Section', styles))
    elems.append(H('''<b>วิธีนี้เหมาะที่สุด</b> สำหรับการเริ่มต้น
เพราะไม่ต้องรอให้ becraft publish ขึ้น NPM และคุณจะได้เวอร์ชันล่าสุดเสมอ''', 'Body', styles))

    elems.append(H('<b>One-shot install (แนะนำ):</b>', 'SubSection', styles))
    elems.append(code_block('# สร้าง project folder ใหม่\nmkdir my-api && cd my-api\n\n# ติดตั้ง becraft จาก GitHub\nnpx -y github:phitsanu07/becraft install\n\n# หรือ quick mode (ไม่ถามอะไร, ใช้ default ทั้งหมด)\nnpx -y github:phitsanu07/becraft install --quick'))

    elems.append(H('<b>Global install:</b>', 'SubSection', styles))
    elems.append(code_block('npm install -g github:phitsanu07/becraft\n\n# จากนั้นใช้ได้ทุกที่:\ncd any-project\nbecraft install'))

    elems.append(H('<b>Specific version (commit / tag / branch):</b>', 'SubSection', styles))
    elems.append(code_block('# Specific commit\nnpx github:phitsanu07/becraft#abc1234 install\n\n# Specific tag\nnpx github:phitsanu07/becraft#v0.1.0 install\n\n# Specific branch\nnpx github:phitsanu07/becraft#dev install'))

    elems.append(H('3.2 ติดตั้งจาก NPM (หลัง publish)', 'Section', styles))
    elems.append(H('''หลังจาก becraft ถูก publish ขึ้น NPM แล้ว
คุณจะใช้คำสั่งสั้นกว่าได้:''', 'Body', styles))
    elems.append(code_block('# One-shot (ได้ version ล่าสุดเสมอ)\nnpx becraft install\n\n# Global install\nnpm install -g becraft\nbecraft install\n\n# Specific version\nnpx becraft@0.1.0 install\nnpx becraft@latest install'))

    elems.append(H('3.3 ติดตั้งแบบ Local Development', 'Section', styles))
    elems.append(H('''ถ้าคุณต้องการ <b>แก้ไข becraft เอง</b> หรือศึกษาโค้ด:''',
                    'Body', styles))
    elems.append(code_block('# Clone repo\ngit clone https://github.com/phitsanu07/becraft.git\ncd becraft\n\n# ติดตั้ง dependencies\nnpm install\n\n# ทำให้คำสั่ง becraft ใช้ได้ทุกที่ในเครื่อง (link)\nnpm link\n\n# ทดสอบ\nbecraft --version\nbecraft list\n\n# ใช้กับ project อื่น\ncd ../my-api\nbecraft install'))

    elems.append(H('3.4 ตัวเลือก Interactive vs Quick', 'Section', styles))
    elems.append(H('<b>Interactive mode</b> (default):', 'SubSection', styles))
    elems.append(code_block('npx -y github:phitsanu07/becraft install\n\n# จะถาม:\n# - ภาษา (en/th)\n# - target directory\n# - IDEs ที่ใช้ (Claude Code, Antigravity)\n# - components ที่ติดตั้ง (skills, agents, commands, templates)'))

    elems.append(H('<b>Quick mode</b> (ใช้ default ทั้งหมด):', 'SubSection', styles))
    elems.append(code_block('npx -y github:phitsanu07/becraft install --quick\n\n# default คือ:\n# - language: en\n# - IDEs: claude + antigravity (ทั้งคู่)\n# - components: skills + agents + commands + templates (ทั้งหมด)'))

    elems.append(H('<b>Custom flags:</b>', 'SubSection', styles))
    elems.append(code_block('# เลือก IDE เฉพาะ\nbecraft install --ide claude\nbecraft install --ide antigravity\nbecraft install --ide "claude,antigravity"\n\n# เลือก language\nbecraft install --lang th\n\n# เลือก target directory\nbecraft install --target /path/to/project\n\n# รวมทั้งหมด\nbecraft install --quick --ide claude --lang en --target ./my-api'))

    elems.append(H('3.5 ตรวจสอบหลังติดตั้ง', 'Section', styles))
    elems.append(H('<b>ดูสถานะการติดตั้ง:</b>', 'SubSection', styles))
    elems.append(code_block('cd my-api\nbecraft status\n\n# จะแสดง:\n# ✓ Installed: v0.1.0\n# ✓ Components: skills (10), agents (13), commands (11), templates (21)\n# ✓ Memory: 9 files\n# ✓ IDE Config: CLAUDE.md, .claude/agents/, .agent/workflows/'))

    elems.append(H('<b>ดูคำสั่งทั้งหมด:</b>', 'SubSection', styles))
    elems.append(code_block('becraft list\n\n# แสดง:\n# - 10 commands (/be, /be-help, /be-bootstrap, ...)\n# - 6 agents (plan, schema, api, auth, observability, test-runner)\n# - 10 skills'))

    return elems


# ============================================================
# Chapter 4
# ============================================================

def chapter_4(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 4: โครงสร้างหลังติดตั้ง', 'Chapter', styles))
    elems.append(H('''หลังจากรัน <font face="Courier">becraft install</font>
โปรเจกต์ของคุณจะมีโฟลเดอร์ใหม่ๆ ปรากฏขึ้น แต่ละอันมีบทบาทแตกต่างกัน''',
                    'Body', styles))

    elems.append(H('4.1 ไดเรกทอรีที่ถูกสร้าง', 'Section', styles))
    elems.append(code_block('''my-api/
├── CLAUDE.md                  # System prompt สำหรับ Claude Code
│
├── .claude/                   # ไฟล์สำหรับ Claude Code
│   ├── agents/               # 6 sub-agent definitions
│   │   ├── plan-orchestrator.md
│   │   ├── schema-architect.md
│   │   ├── api-builder.md
│   │   ├── auth-guard.md
│   │   ├── observability.md
│   │   └── test-runner.md
│   ├── skills/               # 10 skill files
│   │   ├── contract-first/SKILL.md
│   │   ├── schema-design/SKILL.md
│   │   └── ...
│   └── commands/             # 10 command files
│       ├── be.md
│       ├── be-bootstrap.md
│       └── ...
│
├── .agent/                    # ไฟล์สำหรับ Antigravity
│   ├── AGENT.md              # System context
│   └── workflows/            # 10 self-contained workflows
│       ├── be.md
│       ├── be-bootstrap.md   # ~7,000 lines (orchestrator + agents + skills)
│       └── ...
│
└── .be/                       # Memory + reference (shared)
    ├── manifest.json         # ข้อมูล install
    ├── memory/               # 9-file memory system
    │   ├── active.md
    │   ├── summary.md
    │   ├── decisions.md
    │   ├── changelog.md
    │   ├── agents-log.md
    │   ├── architecture.md
    │   ├── api-registry.md
    │   ├── schema.md
    │   ├── contracts.md
    │   └── archive/
    ├── skills/               # reference copies
    ├── agents/               # reference copies
    ├── commands/             # reference copies
    └── templates/            # NestJS starter
        └── nestjs-base/'''))

    elems.append(H('4.2 บทบาทของแต่ละโฟลเดอร์', 'Section', styles))

    role_data = [
        ['โฟลเดอร์', 'บทบาท', 'IDE'],
        ['CLAUDE.md', 'System prompt บอก Claude Code ว่าเป็น "becraft Orchestrator"', 'Claude Code'],
        ['.claude/agents/', 'Sub-agent definitions (Claude Code native format)', 'Claude Code'],
        ['.claude/skills/', 'Skills ที่ load on-demand', 'Claude Code'],
        ['.claude/commands/', 'Slash commands (/be-*)', 'Claude Code'],
        ['.agent/AGENT.md', 'System context สำหรับ Antigravity', 'Antigravity'],
        ['.agent/workflows/', 'Pre-bundled workflows (self-contained)', 'Antigravity'],
        ['.be/memory/', '9-file shared memory (ทั้งสอง IDE อ่าน/เขียนที่นี่)', 'Both'],
        ['.be/templates/', 'NestJS starter project ที่ agents ใช้เป็น base', 'Both'],
        ['.be/manifest.json', 'metadata ของ install (version, IDE, components)', 'Both'],
    ]
    elems.append(make_table(role_data, col_widths=[4 * cm, 9 * cm, 3 * cm]))

    elems.append(H('4.3 ไฟล์ CLAUDE.md และ AGENT.md', 'Section', styles))
    elems.append(H('<b>CLAUDE.md (สำหรับ Claude Code):</b>', 'SubSection', styles))
    elems.append(H('''ถูก auto-generate ตอน install มีเนื้อหา:''', 'Body', styles))
    bullets = [
        '• Identity — บอก Claude ว่ามันคือ "becraft Orchestrator"',
        '• Tech Stack — บังคับใช้ NestJS + PostgreSQL + Prisma',
        '• Command recognition table — รู้จัก /be-* commands ทั้งหมด',
        '• Memory protocol — บังคับให้อ่าน 9 ไฟล์ก่อนทำงาน',
        '• Skills loading checkpoint — ต้อง print skills ที่ load',
        '• Anti-patterns — ห้ามใช้ console.log, any type, ฯลฯ',
        '• Required patterns — ต้องมี OpenAPI, validation, rate limit',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('<b>AGENT.md (สำหรับ Antigravity):</b>', 'SubSection', styles))
    elems.append(H('''มีโครงสร้างคล้าย CLAUDE.md แต่ปรับให้เหมาะกับ Antigravity:''',
                    'Body', styles))
    bullets = [
        '• Memory location ชี้ไป .be/memory/ เพื่อ sync กับ Claude Code',
        '• Reference workflow files ที่ self-contained',
        '• Command syntax ใช้ /be-* (ขีดกลาง) เหมือน Claude Code',
        '• ไม่มี sub-agent delegation (Antigravity ใช้ AI ตัวเดียวที่สลับ role)',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(Paragraph('''<b>หมายเหตุสำคัญ:</b> Memory ทั้งสอง IDE ใช้ที่
<font face="Courier">.be/memory/</font> ที่เดียว
ทำให้คุณสามารถสลับใช้ระหว่าง Claude Code และ Antigravity ได้
โดยไม่สูญเสีย context''', styles['Tip']))

    return elems


# ============================================================
# Chapter 5
# ============================================================

def chapter_5(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 5: คำสั่งทั้ง 10 ตัว', 'Chapter', styles))
    elems.append(H('''becraft มีคำสั่งทั้งหมด 10 ตัว ใช้ได้ใน Claude Code
และ Antigravity ด้วย syntax เดียวกัน (<font face="Courier">/be-*</font>)''',
                    'Body', styles))

    cmd_summary = [
        ['คำสั่ง', 'Shortcut', 'ใช้เมื่อ'],
        ['/be', '/b', 'อยากให้ AI เลือก agent ให้เอง'],
        ['/be-help', '/be-h', 'ดูคำสั่งทั้งหมด'],
        ['/be-plan', '/be-p', 'วางแผนก่อนสร้าง (มี planning step)'],
        ['/be-bootstrap', '/be-b', 'สร้าง backend ครบใน 1 คำสั่ง'],
        ['/be-schema', '/be-s', 'ออกแบบ DB schema + migration'],
        ['/be-api', '/be-a', 'สร้าง endpoints + DTOs'],
        ['/be-auth', '/be-au', 'JWT, RBAC, rate limit'],
        ['/be-observe', '/be-o', 'logs + metrics + health'],
        ['/be-test', '/be-t', 'สร้าง + รัน tests'],
        ['/be-fix', '/be-f', 'debug + แก้ bug'],
    ]
    elems.append(make_table(cmd_summary, col_widths=[3 * cm, 2.2 * cm, 10.8 * cm]))

    # ---- Detailed commands ----

    cmds = [
        {
            'name': '/be',
            'short': '/b',
            'title': '5.1 /be — Smart Router',
            'desc': '''คำสั่งสำหรับเริ่มต้นที่ดีที่สุด — พิมพ์อะไรก็ได้ในภาษาธรรมชาติ
AI จะวิเคราะห์ intent, score confidence, เลือก agent เอง''',
            'when': 'เมื่อยังไม่แน่ใจว่าจะใช้คำสั่งไหน หรืองานที่ต้องใช้หลาย agent',
            'examples': '''/be สร้าง endpoint POST /products ที่รับ name, price, stock
/be add inventory tracking with audit log
/be ทำต่อ                     # AI อ่าน memory แล้วต่อจากที่ทำค้างไว้''',
            'flow': '''1. อ่าน memory 9 ไฟล์
2. วิเคราะห์ intent (HIGH ≥80, MEDIUM 50-79, LOW <50)
3. ถ้า HIGH → execute เลย
   ถ้า MEDIUM → route ไป plan-orchestrator
   ถ้า LOW → ถามให้ชัดขึ้น
4. แสดง workflow plan ก่อนรัน
5. Execute พร้อม progress updates''',
        },
        {
            'name': '/be-help',
            'short': '/be-h',
            'title': '5.2 /be-help — แสดงคำสั่งทั้งหมด',
            'desc': 'แสดงคำสั่ง, agents, skills ทั้งหมด พร้อมตัวอย่างการใช้',
            'when': 'เมื่อจำไม่ได้ว่ามีคำสั่งอะไรบ้าง',
            'examples': '/be-help',
            'flow': 'ไม่ต้องอ่าน memory, ไม่ delegate ไป agent — แสดงข้อมูลทันที',
        },
        {
            'name': '/be-plan',
            'short': '/be-p',
            'title': '5.3 /be-plan — วางแผนก่อนสร้าง',
            'desc': '''Mode "วางแผน" — AI จะวิเคราะห์ requirements
แสดง plan เป็น phases รอให้คุณยืนยันก่อนเริ่มสร้าง''',
            'when': 'งานซับซ้อน หลายขั้นตอน อยากเห็นแผนก่อน',
            'examples': '''/be-plan สร้างระบบ booking ห้องประชุมพร้อม notification
/be-p e-commerce backend with payment integration''',
            'flow': '''Phase 1: PLANNING
- อ่าน memory
- วิเคราะห์ business domain
- ออกแบบ entities, endpoints, auth strategy
- แสดง plan ให้ user ดู
- รอ "Go" หรือ adjustment

Phase 2: EXECUTING
- รัน phase by phase
- Pause หลังแต่ละ phase
- รายงาน progress real-time''',
        },
        {
            'name': '/be-bootstrap',
            'short': '/be-b',
            'title': '5.4 /be-bootstrap — สร้าง backend ครบในคำสั่งเดียว',
            'desc': '''คำสั่งทรงพลังที่สุด — orchestrate 6 agents ทั้งหมด
สร้าง backend สมบูรณ์ภายใน ~30-40 นาที''',
            'when': 'เริ่ม project ใหม่จากศูนย์',
            'examples': '''/be-bootstrap user management API with JWT auth
/be-b restaurant booking system with payment
/be-bootstrap inventory tracking for warehouse''',
            'flow': '''Phase 1: 📋 plan-orchestrator → วิเคราะห์ + วางแผน
Phase 2: 📐 schema-architect → ออกแบบ DB + generate migration
Phase 3: 🔌 api-builder + 🛡️ auth-guard (parallel ใน Claude Code)
Phase 4: 📊 observability → logs/metrics/health
Phase 5: 🧪 test-runner → สร้าง + รัน tests
Phase 6: Final verify → npm run build + npm test

ผลลัพธ์: API พร้อมใช้ที่ http://localhost:3000/docs''',
        },
        {
            'name': '/be-schema',
            'short': '/be-s',
            'title': '5.5 /be-schema — ออกแบบ DB Schema',
            'desc': 'สร้าง/แก้ไข Prisma schema พร้อม migration ที่ปลอดภัย',
            'when': 'เพิ่ม entity ใหม่, แก้ relationships, เพิ่ม indexes',
            'examples': '''/be-schema เพิ่ม Product (name, price, stock, category)
/be-s add order_items table with line totals
/be-schema add soft delete to Customer''',
            'flow': '''1. อ่าน prisma/schema.prisma + .be/memory/schema.md
2. Map TypeScript types → Prisma models
3. เพิ่ม indexes บน FK, unique columns
4. Preview migration: npx prisma migrate dev --create-only
5. Apply: npx prisma migrate dev
6. Generate Prisma client
7. Update .be/memory/schema.md''',
        },
        {
            'name': '/be-api',
            'short': '/be-a',
            'title': '5.6 /be-api — สร้าง API Endpoints',
            'desc': '''สร้าง NestJS controllers + services + DTOs + OpenAPI
ตามหลัก Contract-First''',
            'when': 'มี schema แล้ว ต้องการเพิ่ม CRUD endpoints',
            'examples': '''/be-api create CRUD for products
/be-a สร้าง endpoint POST /orders/:id/cancel
/be-api add search endpoint with cursor pagination''',
            'flow': '''1. อ่าน prisma/schema.prisma
2. Generate (in order):
   - dto/*.ts (request, response, update)
   - <resource>.service.ts (business logic)
   - <resource>.controller.ts (endpoints + OpenAPI)
   - <resource>.module.ts
3. Register ใน app.module.ts
4. npm run build → ตรวจ TypeScript errors
5. Auto-fix errors
6. Update .be/memory/api-registry.md + contracts.md''',
        },
        {
            'name': '/be-auth',
            'short': '/be-au',
            'title': '5.7 /be-auth — Authentication & Authorization',
            'desc': '''ตั้งค่า JWT (access + refresh), RBAC, rate limiting,
password hashing, idempotency''',
            'when': 'ต้องการระบบสมัครสมาชิก, login, protect routes',
            'examples': '''/be-auth setup JWT login/register/refresh
/be-au add Google OAuth
/be-auth add admin role with RBAC''',
            'flow': '''1. อ่าน User model
2. Install: @nestjs/jwt, passport, bcrypt, @nestjs/throttler
3. Generate:
   - src/auth/{module,controller,service}.ts
   - src/auth/strategies/jwt.strategy.ts
   - src/auth/tokens.service.ts (Redis rotation)
   - src/common/guards/{jwt-auth,roles}.guard.ts
   - src/common/decorators/{public,roles,current-user}.ts
4. Register global guards
5. Add JWT_SECRET to .env.example
6. Verify build''',
        },
        {
            'name': '/be-observe',
            'short': '/be-o',
            'title': '5.8 /be-observe — Logging + Metrics + Health',
            'desc': '''Production observability baseline — Pino structured logs,
Prometheus /metrics, health checks (live + ready)''',
            'when': 'เตรียม deploy ขึ้น production, เพิ่ม monitoring',
            'examples': '''/be-observe setup logging + metrics
/be-o add custom business metrics (orders_total, revenue)
/be-observe enable Sentry error tracking''',
            'flow': '''1. Install: nestjs-pino, @nestjs/terminus, prom-client
2. Configure Pino with redact list (PII protection)
3. Create /health, /health/live, /health/ready
4. Create /metrics endpoint
5. Apply request-id middleware globally
6. Update .env.example''',
        },
        {
            'name': '/be-test',
            'short': '/be-t',
            'title': '5.9 /be-test — Generate + Run Tests',
            'desc': '''สร้าง Jest tests (unit) + Supertest e2e tests
(ใช้ Testcontainers PostgreSQL จริง) พร้อม auto-fix loop''',
            'when': 'มี code แล้ว ต้องการ tests',
            'examples': '''/be-test for users module
/be-t generate integration tests for /orders
/be-test add load tests with k6''',
            'flow': '''1. อ่าน service + controller + DTOs
2. Install: jest, supertest, @testcontainers/postgresql, faker
3. Setup: jest config, Testcontainers helper, factories
4. Generate:
   - <name>.service.spec.ts (unit, mocked)
   - <name>.e2e-spec.ts (integration, real DB)
5. Run: npm test
6. Auto-fix loop (max 5 attempts)
7. รายงานผล (passed, coverage, auto-fixes)''',
        },
        {
            'name': '/be-fix',
            'short': '/be-f',
            'title': '5.10 /be-fix — Debug & Fix',
            'desc': '''Diagnose ปัญหา → identify root cause → apply minimal fix → verify''',
            'when': 'มี bug, test failures, build errors',
            'examples': '''/be-fix endpoint /users return 500
/be-f failing test in auth.spec.ts
/be-fix N+1 query in /orders''',
            'flow': '''Phase 1: REPRODUCE
- อ่าน user's bug description
- อ่าน related files
- เช็ค changelog (recent changes)
- Run failing test

Phase 2: DIAGNOSE
- Identify root cause (not symptom)

Phase 3: FIX
- Apply minimal change
- Don't refactor surrounding code

Phase 4: VERIFY
- Run failing test (should pass)
- Run full suite (no regression)
- npm run build''',
        },
    ]

    for cmd in cmds:
        elems.append(H(cmd['title'], 'Section', styles))
        elems.append(H(f"<b>คำอธิบาย:</b> {cmd['desc']}", 'Body', styles))

        elems.append(H('<b>เมื่อไหร่ใช้:</b>', 'SubSection', styles))
        elems.append(H(cmd['when'], 'Body', styles))

        elems.append(H('<b>ตัวอย่างการใช้:</b>', 'SubSection', styles))
        elems.append(code_block(cmd['examples']))

        elems.append(H('<b>ขั้นตอนการทำงาน:</b>', 'SubSection', styles))
        elems.append(code_block(cmd['flow']))

    return elems


# ============================================================
# Chapter 6 - Tutorial
# ============================================================

def chapter_6(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 6: Tutorial — สร้าง User Management API', 'Chapter', styles))
    elems.append(H('''บทนี้พาคุณสร้าง backend จริงตั้งแต่ต้นจนจบ
ภายใน 30 นาที''', 'Body', styles))

    elems.append(H('6.1 สิ่งที่จะได้', 'Section', styles))
    bullets = [
        '✅ User registration + login + refresh token',
        '✅ JWT authentication (access 15m + refresh 7d)',
        '✅ Profile CRUD (GET, PATCH, DELETE)',
        '✅ Role-based access control (USER, ADMIN)',
        '✅ Rate limiting (5/min on /login, 10/hr on /register)',
        '✅ OpenAPI docs ที่ /docs',
        '✅ Health checks (/health/live, /health/ready)',
        '✅ Prometheus metrics ที่ /metrics',
        '✅ All endpoints ทดสอบครบ (Jest + Supertest + Testcontainers)',
        '✅ Docker + docker-compose พร้อม deploy',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('6.2 ขั้นตอนทั้งหมด (End-to-End)', 'Section', styles))

    elems.append(H('<b>Step 1: เตรียม project folder</b>', 'SubSection', styles))
    elems.append(code_block('mkdir user-management-api\ncd user-management-api'))

    elems.append(H('<b>Step 2: ติดตั้ง becraft</b>', 'SubSection', styles))
    elems.append(code_block('npx -y github:phitsanu07/becraft install --quick'))
    elems.append(H('''หลังเสร็จคุณจะมี: <font face="Courier">CLAUDE.md</font>,
<font face="Courier">.claude/</font>, <font face="Courier">.agent/</font>,
<font face="Courier">.be/</font>''', 'Body', styles))

    elems.append(H('<b>Step 3: เปิด IDE</b>', 'SubSection', styles))
    elems.append(code_block('# ใช้ Claude Code\nclaude .\n\n# หรือ Antigravity\n# เปิด Antigravity แล้วเลือก folder นี้'))

    elems.append(H('<b>Step 4: รัน /be-bootstrap</b>', 'SubSection', styles))
    elems.append(code_block('/be-bootstrap user management API with JWT auth and RBAC'))

    elems.append(H('''AI จะ:''', 'Body', styles))
    bullets = [
        '1. อ่าน memory 9 ไฟล์ (ครั้งแรกจะว่าง)',
        '2. วิเคราะห์ requirements → user, role, session entities',
        '3. แสดง plan ให้ดู (มี 5 phases)',
        '4. คุณพิมพ์ "Go" → AI เริ่มทำ',
        '5. Phase 1-5 รัน sequential กับ parallel ตามที่วางแผน',
        '6. ตอนจบ AI report สิ่งที่สร้าง + คำสั่งที่ต้องรัน',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('<b>Step 5: ตั้ง environment</b>', 'SubSection', styles))
    elems.append(code_block('''cp .env.example .env

# Generate JWT secrets
echo "JWT_SECRET=$(openssl rand -base64 32)" >> .env
echo "JWT_REFRESH_SECRET=$(openssl rand -base64 32)" >> .env

# ตั้ง DATABASE_URL + REDIS_URL (ถ้าใช้ docker-compose)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/becraft?schema=public
# REDIS_URL=redis://localhost:6379'''))

    elems.append(H('<b>Step 6: เริ่ม PostgreSQL + Redis</b>', 'SubSection', styles))
    elems.append(code_block('docker-compose up -d postgres redis\n\n# ตรวจสอบ\ndocker ps'))

    elems.append(H('<b>Step 7: รัน migrations</b>', 'SubSection', styles))
    elems.append(code_block('npx prisma migrate dev'))

    elems.append(H('<b>Step 8: ติดตั้ง dependencies + รัน server</b>', 'SubSection', styles))
    elems.append(code_block('npm install\nnpm run start:dev'))

    elems.append(H('''Console จะขึ้น:''', 'Body', styles))
    elems.append(code_block('''🚀 becraft API listening on http://localhost:3000
📖 OpenAPI docs at http://localhost:3000/docs
🏥 Health check at http://localhost:3000/health'''))

    elems.append(H('<b>Step 9: ทดสอบ API</b>', 'SubSection', styles))
    elems.append(H('<b>9.1 สมัครสมาชิก:</b>', 'Body', styles))
    elems.append(code_block('''curl -X POST http://localhost:3000/api/v1/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123",
    "name": "Test User"
  }'

# ผลลัพธ์:
# { "accessToken": "eyJ...", "refreshToken": "eyJ..." }'''))

    elems.append(H('<b>9.2 Login:</b>', 'Body', styles))
    elems.append(code_block('''curl -X POST http://localhost:3000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123"
  }'

# เก็บ accessToken ไว้ใช้ขั้นต่อไป
TOKEN="eyJ..."'''))

    elems.append(H('<b>9.3 ดึงข้อมูล profile (ต้อง auth):</b>', 'Body', styles))
    elems.append(code_block('''curl http://localhost:3000/api/v1/auth/me \\
  -H "Authorization: Bearer $TOKEN"

# { "id": "uuid", "email": "...", "name": "...", "role": "USER" }'''))

    elems.append(H('<b>9.4 ดู OpenAPI:</b>', 'Body', styles))
    elems.append(H('''เปิด browser ไปที่ <font face="Courier">http://localhost:3000/docs</font>
จะเห็น Swagger UI ที่ทดลอง endpoints ได้แบบ interactive''', 'Body', styles))

    elems.append(H('<b>Step 10: รัน tests</b>', 'SubSection', styles))
    elems.append(code_block('''npm test           # Unit tests
npm run test:e2e   # Integration (ใช้ Testcontainers)
npm run test:cov   # With coverage report'''))

    elems.append(Paragraph('''<b>เสร็จแล้ว!</b> คุณมี backend ที่:
1) ทดสอบครบ 2) มี documentation 3) มี monitoring 4) production-ready''',
                            styles['Tip']))

    elems.append(H('6.3 การเพิ่ม feature ใหม่ภายหลัง', 'Section', styles))
    elems.append(H('<b>เพิ่ม Posts entity:</b>', 'SubSection', styles))
    elems.append(code_block('''# 1. ออกแบบ schema
/be-schema เพิ่ม Post entity (title, content, authorId, published)

# 2. สร้าง CRUD endpoints
/be-api create CRUD for posts (auth required, only author can edit)

# 3. สร้าง tests
/be-test for posts module

# เสร็จ! ใช้เวลาประมาณ 5-10 นาที'''))

    return elems


# ============================================================
# Chapter 7 - Memory
# ============================================================

def chapter_7(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 7: ระบบ Memory (9 ไฟล์)', 'Chapter', styles))

    elems.append(H('7.1 ทำไมต้องมี memory', 'Section', styles))
    elems.append(H('''เมื่อคุณทำงานกับ AI ใน session ใหม่ AI ไม่รู้ว่าก่อนหน้านี้คุณทำอะไรไป
ถ้าไม่มี memory ทุกครั้งคุณต้องอธิบาย project ใหม่ตั้งแต่ต้น''', 'Body', styles))

    elems.append(H('''becraft แก้ปัญหานี้ด้วย <b>9-file memory system</b>
ที่บันทึกบริบทของ project ทั้งหมดลงใน markdown files
AI จะ <b>อ่าน 9 ไฟล์ก่อนเริ่มงาน</b> และ <b>อัปเดตหลังทำงาน</b>''', 'Body', styles))

    elems.append(H('7.2 บทบาทของแต่ละไฟล์', 'Section', styles))

    mem_data = [
        ['ไฟล์', 'บทบาท', 'ขนาด'],
        ['active.md', 'งานที่กำลังทำ + next steps', '~500 tokens'],
        ['summary.md', 'ภาพรวม project + tech stack', '~1,000 tokens'],
        ['decisions.md', 'Architecture Decision Records (ADRs)', '~500 tokens'],
        ['changelog.md', 'การเปลี่ยนแปลงในแต่ละ session', '~300 tokens'],
        ['agents-log.md', 'log การทำงานของ agents', '~300 tokens'],
        ['architecture.md', 'โครงสร้างของ services', '~500 tokens'],
        ['api-registry.md', 'รายการ endpoints + DTOs + auth', '~600 tokens'],
        ['schema.md', 'DB schema + migration history', '~500 tokens'],
        ['contracts.md', 'OpenAPI snapshots + breaking changes', '~400 tokens'],
    ]
    elems.append(make_table(mem_data, col_widths=[3.5 * cm, 9 * cm, 3.5 * cm]))

    elems.append(H('<b>รวม budget: ~4,600 tokens</b> สำหรับโหลด memory ครบ', 'Body', styles))

    elems.append(H('7.3 Memory Protocol — กฎที่ AI ต้องทำตาม', 'Section', styles))

    elems.append(H('<b>ก่อนทำงานทุกครั้ง (BEFORE):</b>', 'SubSection', styles))
    elems.append(code_block('''STEP 1: เช็คว่า .be/memory/ มีอยู่
        ├── ไม่มี → สร้างจาก template
        └── มี → ต่อไป Step 2

STEP 2: อ่าน 9 ไฟล์แบบ PARALLEL
        (ใช้ parallel tool calls ประหยัดเวลา)

STEP 3: สร้างความเข้าใจ
        - Project นี้เกี่ยวกับอะไร?
        - งาน active คืออะไร?
        - มี decisions อะไรบ้าง?
        - Schema state ปัจจุบัน?

STEP 4: รายงานผู้ใช้
        "💾 Memory: Loaded ✅ (9 files)"'''))

    elems.append(H('<b>หลังทำงานเสร็จ (AFTER):</b>', 'SubSection', styles))
    elems.append(code_block('''STEP 1: อัปเดต active.md (เสมอ)
        - Current Focus → สิ่งที่เพิ่งทำ
        - Just Completed → เพิ่มของที่เสร็จ
        - Next Steps → เสนอขั้นตอนถัดไป

STEP 2: อัปเดต changelog.md (เสมอ)
        - เพิ่มแถว: | Agent | Action | Files |

STEP 3: อัปเดต agents-log.md (เสมอ)
        - เพิ่มแถว: | Time | Agent | Task | Status |

STEP 4: อัปเดตไฟล์เฉพาะทาง (ถ้ามี)
        - Schema เปลี่ยน → schema.md
        - API endpoint → api-registry.md + contracts.md
        - Architecture → architecture.md
        - Decision → decisions.md
        - Feature เสร็จ → summary.md

STEP 5: ยืนยัน
        "💾 Memory: Saved ✅"'''))

    elems.append(H('7.4 Cross-IDE Synchronization', 'Section', styles))
    elems.append(H('''ปัญหา: Claude Code และ Antigravity อาจรันคนละ session
แต่ user คาดหวังให้บริบท persist ข้าม IDE''', 'Body', styles))

    elems.append(H('''<b>วิธีแก้ของ becraft:</b> Memory location เดียวกัน — <font face="Courier">.be/memory/</font>
ทั้งสอง IDE อ่าน/เขียนที่นี่ที่เดียว''', 'Body', styles))

    elems.append(H('<b>การใช้งานจริง:</b>', 'SubSection', styles))
    bullets = [
        '✅ เริ่มงานใน Claude Code → AI อัปเดต .be/memory/active.md',
        '✅ ปิด Claude Code → เปิด Antigravity ในโปรเจกต์เดียวกัน',
        '✅ Antigravity AI อ่าน .be/memory/ → รู้ว่าค้างอะไรไว้',
        '✅ ทำงานต่อได้ทันที ไม่ต้องอธิบาย context ใหม่',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(Paragraph('''<b>สำคัญ:</b> ห้ามใช้ <font face="Courier">.claude/memory/</font>
หรือ <font face="Courier">.agent/memory/</font> — ใช้
<font face="Courier">.be/memory/</font> เท่านั้น''', styles['Warning']))

    elems.append(H('7.5 Archive Strategy', 'Section', styles))
    elems.append(H('''เมื่อ <font face="Courier">active.md</font> ยาวเกิน 50 บรรทัด
หรือ session จบ:''', 'Body', styles))
    elems.append(code_block('''1. Snapshot active.md → archive/active-{YYYY-MM-DD-HHMM}.md
2. Reset active.md (เก็บแค่ Next Steps section)
3. ย้าย summary points → summary.md

เมื่อ changelog.md > 200 บรรทัด:
1. ย้ายเซสชันเก่าสุด → archive/changelog-{YYYY-MM}.md
2. เก็บ 5 sessions ล่าสุดในไฟล์หลัก'''))

    return elems


# ============================================================
# Chapter 8 - Agents
# ============================================================

def chapter_8(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 8: 6 Agents — เข้าใจการทำงานของแต่ละตัว', 'Chapter', styles))
    elems.append(H('''ส่วนนี้อธิบาย role + workflow ของแต่ละ agent
เพื่อให้คุณเข้าใจว่าใครจะมาทำอะไร เวลาไหน''', 'Body', styles))

    agents = [
        {
            'title': '8.1 📋 plan-orchestrator (THE BRAIN)',
            'role': 'วิเคราะห์, วางแผน, orchestrate agents อื่นๆ',
            'when': 'งานซับซ้อนที่ต้องใช้หลาย agents',
            'workflow': '''Mode 1: PLANNING
- อ่าน memory + วิเคราะห์ request
- ออกแบบ phases
- แสดง plan ให้ user

Mode 2: EXECUTING
- รัน phase by phase
- Pause + report หลังแต่ละ phase
- Spawn agents ตาม plan''',
            'tools': 'Read, Write, Edit, Bash, WebFetch',
        },
        {
            'title': '8.2 📐 schema-architect',
            'role': 'ออกแบบ PostgreSQL schema + Prisma migrations',
            'when': 'เพิ่ม entity ใหม่, modify schema, optimize indexes',
            'workflow': '''1. อ่าน prisma/schema.prisma + types
2. Map TypeScript types → Prisma models
3. Add indexes บน FK + unique
4. Preview migration (--create-only)
5. Apply migration
6. Update schema.md''',
            'tools': 'Read, Write, Edit, Bash',
        },
        {
            'title': '8.3 🔌 api-builder',
            'role': 'สร้าง NestJS endpoints + DTOs + OpenAPI',
            'when': 'เพิ่ม REST endpoints, CRUD, custom routes',
            'workflow': '''1. อ่าน schema + existing controllers
2. Generate (in order): DTOs → Service → Controller → Module
3. เพิ่ม OpenAPI annotations
4. Apply class-validator
5. Add Idempotency-Key, pagination
6. Update api-registry.md + contracts.md''',
            'tools': 'Read, Write, Edit, Bash',
        },
        {
            'title': '8.4 🛡️ auth-guard',
            'role': 'JWT authentication, RBAC, rate limiting',
            'when': 'Setup login/register, protect routes',
            'workflow': '''1. อ่าน User model
2. Install passport, jwt, bcrypt, throttler
3. Generate auth module + strategies
4. Create JwtAuthGuard + RolesGuard
5. Add @Public, @Roles, @CurrentUser decorators
6. Configure rate limits on /auth/*''',
            'tools': 'Read, Write, Edit, Bash',
        },
        {
            'title': '8.5 📊 observability',
            'role': 'Logging + metrics + health checks',
            'when': 'เตรียม production, debug performance',
            'workflow': '''1. Install nestjs-pino, terminus, prom-client
2. Configure Pino + redact list
3. Create /health/live + /health/ready
4. Create /metrics endpoint (Prometheus)
5. Apply request-id middleware''',
            'tools': 'Read, Write, Edit, Bash',
        },
        {
            'title': '8.6 🧪 test-runner',
            'role': 'Generate + run tests with auto-fix loop',
            'when': 'หลังสร้าง feature, ก่อน deploy',
            'workflow': '''1. อ่าน service + controller + DTOs
2. Setup Jest + Testcontainers
3. Generate unit tests (mocked)
4. Generate e2e tests (real DB)
5. Run + auto-fix loop (max 5 attempts)
6. Report success only (silent fixes)''',
            'tools': 'Read, Write, Edit, Bash',
        },
    ]

    for ag in agents:
        elems.append(H(ag['title'], 'Section', styles))
        elems.append(H(f"<b>บทบาท:</b> {ag['role']}", 'Body', styles))
        elems.append(H(f"<b>เมื่อใช้:</b> {ag['when']}", 'Body', styles))
        elems.append(H(f"<b>Tools ที่ใช้ได้:</b> <font face='Courier'>{ag['tools']}</font>",
                        'Body', styles))
        elems.append(H('<b>Workflow:</b>', 'SubSection', styles))
        elems.append(code_block(ag['workflow']))

    elems.append(H('8.7 Parallel Execution Matrix', 'Section', styles))
    elems.append(H('''ใน Claude Code agents สามารถรันคู่ขนานได้
(Antigravity ใช้ AI ตัวเดียวจึงต้อง sequential)''', 'Body', styles))

    parallel_data = [
        ['Agent', 'MUST WAIT FOR', 'CAN PARALLEL WITH'],
        ['plan-orchestrator', '(none)', '(orchestrates others)'],
        ['schema-architect', 'plan', 'api-builder (mock mode)'],
        ['api-builder', 'schema', 'auth-guard, observability'],
        ['auth-guard', 'schema', 'api-builder'],
        ['observability', 'api-builder', 'test-runner'],
        ['test-runner', 'api-builder', 'observability'],
    ]
    elems.append(make_table(parallel_data, col_widths=[4 * cm, 3.5 * cm, 8.5 * cm]))

    return elems


# ============================================================
# Chapter 9 - Skills
# ============================================================

def chapter_9(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 9: 10 Skills', 'Chapter', styles))
    elems.append(H('''Skills คือ "knowledge bases" ที่ AI อ่านเพื่อรู้
best practices, patterns, anti-patterns ของแต่ละด้าน
แต่ละ skill มี ~200-400 บรรทัดของเนื้อหาเชิงลึก''', 'Body', styles))

    elems.append(H('9.1 Core Skills (โหลดเสมอ)', 'Section', styles))
    core_data = [
        ['Skill', 'หน้าที่'],
        ['memory-system', '9-file memory protocol — read/write rules'],
        ['response-format', '3-section response template (What I Did / What You Get / What You Need To Do)'],
        ['smart-routing', 'Intent classification + confidence scoring สำหรับ /be'],
    ]
    elems.append(make_table(core_data, col_widths=[4 * cm, 12 * cm]))

    elems.append(H('9.2 Domain Skills (โหลดตาม command)', 'Section', styles))
    domain_data = [
        ['Skill', 'เนื้อหา'],
        ['contract-first', 'Master CDD workflow — Contract → Schema → Code → Test'],
        ['schema-design', 'PostgreSQL + Prisma patterns: UUID, indexes, FK, soft delete, RLS, migrations'],
        ['api-design', 'REST conventions: URL naming, HTTP methods, status codes, pagination, versioning, OpenAPI'],
        ['auth-patterns', 'JWT (access+refresh), OAuth, bcrypt, RBAC, rate limiting, idempotency'],
        ['testing-pyramid', 'Unit + Integration (Testcontainers) + Contract tests, factories, isolation'],
        ['observability', 'Pino + Prometheus + OpenTelemetry + health checks, redact PII'],
        ['error-handling', 'RFC 7807 Problem Details, retry, circuit breaker, idempotency, graceful shutdown'],
    ]
    elems.append(make_table(domain_data, col_widths=[3.5 * cm, 12.5 * cm]))

    elems.append(H('9.3 ตัวอย่างเนื้อหาใน skill', 'Section', styles))
    elems.append(H('''ทุก skill จะประกอบด้วย:''', 'Body', styles))
    bullets = [
        '• YAML frontmatter (name, description, related_skills)',
        '• Purpose — เป้าหมายของ skill',
        '• Core Principles — หลักการสำคัญ 3-5 ข้อ',
        '• Patterns — รูปแบบ code ที่ดี (with examples)',
        '• Anti-Patterns — สิ่งที่ห้ามทำ พร้อมเหตุผล',
        '• Checklist — รายการตรวจก่อน merge',
        '• Integration — ความเชื่อมโยงกับ skills อื่น',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('<b>ตัวอย่าง: anti-pattern ใน api-design skill</b>', 'SubSection', styles))
    elems.append(code_block('''❌ Verbs in URL
   WRONG: POST /api/v1/getUsers
   RIGHT: GET /api/v1/users

❌ Returning passwordHash in response
   WRONG: { "id": "...", "passwordHash": "$2b$..." }
   RIGHT: ใช้ @Exclude() decorator + ClassSerializerInterceptor

❌ Stack traces in error responses
   WRONG: { "error": "stack trace..." }
   RIGHT: { "type", "title", "status", "detail" } (no stack)
          Log full stack server-side only

❌ Missing pagination on list endpoints
   WRONG: GET /users returns all 1M users
   RIGHT: ใช้ PaginationDto with cursor-based pagination'''))

    return elems


# ============================================================
# Chapter 10 - Tech Stack
# ============================================================

def chapter_10(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 10: Tech Stack อธิบายลึก', 'Chapter', styles))
    elems.append(H('''becraft เลือกใช้ stack ที่ <b>opinionated</b> —
ไม่มีการให้คุณเลือกเองเพื่อลดการตัดสินใจ''', 'Body', styles))

    elems.append(H('10.1 Stack Overview', 'Section', styles))

    stack_data = [
        ['Layer', 'Technology', 'เหตุผล'],
        ['Runtime', 'Node.js 22 LTS', 'Stable, performance ดี, ecosystem ใหญ่'],
        ['Framework', 'NestJS 10', 'DI + decorator + modules ทำให้ AI อ่าน structure ง่าย'],
        ['Language', 'TypeScript (strict)', 'Type safety = AI ทำพังน้อย'],
        ['Database', 'PostgreSQL 16', 'Battle-tested, ACID, JSON support, RLS'],
        ['ORM', 'Prisma 5', 'Type-safe queries, auto migrations, great DX'],
        ['Cache', 'Redis 7', 'Refresh tokens, idempotency keys, throttler'],
        ['Queue', 'BullMQ', 'Background jobs, retry, dead letter'],
        ['Auth', 'Passport JWT', 'Mature, flexible, supports OAuth'],
        ['Validation', 'class-validator + Zod', 'DTO validation + env validation'],
        ['Logger', 'Pino', 'Fast structured JSON logging'],
        ['Metrics', 'prom-client', 'Prometheus standard'],
        ['Tests', 'Jest + Supertest + Testcontainers', 'Real DB integration tests'],
        ['Container', 'Docker + Compose', 'Reproducible environments'],
        ['Docs', '@nestjs/swagger', 'Auto-generated OpenAPI'],
    ]
    elems.append(make_table(stack_data, col_widths=[3 * cm, 5 * cm, 8 * cm]))

    elems.append(H('10.2 ทำไมเลือก NestJS', 'Section', styles))
    bullets = [
        '✅ <b>Modular architecture</b> — แต่ละ feature เป็น module ทำให้ scale ได้ดี',
        '✅ <b>Dependency Injection</b> — testable, mockable, swappable',
        '✅ <b>Decorators</b> — readable: @Get(), @ApiProperty(), @Roles()',
        '✅ <b>Built-in support</b> สำหรับ guards, interceptors, pipes, filters',
        '✅ <b>OpenAPI auto-generation</b> — @nestjs/swagger',
        '✅ <b>WebSockets, GraphQL, Microservices</b> — ใช้ pattern เดียวกัน',
        '✅ <b>Active community</b> — solutions เยอะใน Stack Overflow',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('10.3 ทำไมเลือก Prisma', 'Section', styles))
    bullets = [
        '✅ <b>Type-safe queries</b> — IntelliSense ทุก query',
        '✅ <b>Schema-first</b> — มี single source of truth (schema.prisma)',
        '✅ <b>Safe migrations</b> — auto-generated SQL ที่ review ได้',
        '✅ <b>Relation handling</b> — เข้าใจ 1-N, M-N, self-ref ได้ง่าย',
        '✅ <b>Studio</b> — GUI สำหรับ inspect database',
        '✅ <b>RLS support</b> — ผ่าน raw migrations',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('10.4 ทำไมต้องมี Redis', 'Section', styles))
    bullets = [
        '🔁 <b>Refresh token rotation</b> — เก็บ token IDs เพื่อ revoke ได้',
        '🚦 <b>Rate limiting</b> — counter ที่ shared ระหว่าง instances',
        '🔁 <b>Idempotency cache</b> — เก็บ response ของ POST/PUT 24 ชม.',
        '⚡ <b>BullMQ backend</b> — job queue ที่ persist',
        '💾 <b>Application cache</b> — cache hot data',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    return elems


# ============================================================
# Chapter 11 - Best Practices
# ============================================================

def chapter_11(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 11: Best Practices', 'Chapter', styles))

    elems.append(H('11.1 Contract First Workflow', 'Section', styles))
    elems.append(H('''becraft enforce ลำดับการทำงานต่อไปนี้:''', 'Body', styles))
    elems.append(code_block('''Step 1: CONTRACT
- เขียน OpenAPI spec / DTOs ก่อนเขียน controller
- Define error schema
- Declare auth requirements

Step 2: SCHEMA (derived from contract)
- Map DTO entities → DB tables
- Add indexes ตาม query patterns
- Generate migration

Step 3: IMPLEMENTATION
- Controller signatures match contract
- Service implements business rules
- Repository abstracts DB

Step 4: VERIFICATION (3 layers)
- Contract tests (vs OpenAPI)
- Integration tests (Testcontainers)
- Unit tests (business logic)

Step 5: PRODUCTION
- Pino logs + request-id
- /metrics exposed
- /health endpoints
- Rate limit configured
- Idempotency keys
- /docs auto-served'''))

    elems.append(H('11.2 ห้ามทำเด็ดขาด (NEVER)', 'Section', styles))
    bullets = [
        '❌ <font face="Courier">console.log</font> ใน production code → ใช้ Pino logger',
        '❌ <font face="Courier">any</font> type → ใช้ <font face="Courier">unknown</font> + narrow',
        '❌ Stack traces ใน API response → log server-side only',
        '❌ Hardcoded secrets → ใช้ env vars + validate',
        '❌ Tables without RLS หรือ RBAC check',
        '❌ N+1 queries → ใช้ Prisma <font face="Courier">include</font> หรือ <font face="Courier">select</font>',
        '❌ Missing rate limit on /auth/*',
        '❌ Missing Idempotency-Key on POST/PUT side effects',
        '❌ Sync work in request handlers → ใช้ BullMQ',
        '❌ Skipping OpenAPI annotations',
        '❌ Unvalidated user input → ทุก DTO ต้องมี class-validator',
        '❌ Hard delete by default → ใช้ soft delete (deletedAt)',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('11.3 ต้องทำเสมอ (ALWAYS)', 'Section', styles))
    bullets = [
        '✅ อ่าน 9 memory files ก่อนเริ่มงาน',
        '✅ Print Skills Loaded checkpoint at start',
        '✅ ใช้ NestJS DI patterns',
        '✅ Validate input ด้วย class-validator + Zod',
        '✅ Document with @ApiProperty / @ApiOperation',
        '✅ Generate Prisma migrations safely (additive first)',
        '✅ Add indexes to all FK columns',
        '✅ Use Pino structured logging',
        '✅ Add request-id propagation',
        '✅ Run <font face="Courier">npm run build</font> + <font face="Courier">npm test</font> before declaring done',
        '✅ Update memory after work',
        '✅ Use 3-section response format',
        '✅ Suggest next steps',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    elems.append(H('11.4 Production Deployment Checklist', 'Section', styles))
    bullets = [
        '☐ <font face="Courier">JWT_SECRET</font> + <font face="Courier">JWT_REFRESH_SECRET</font> ตั้งใน production env',
        '☐ <font face="Courier">DATABASE_URL</font> ชี้ไป production DB (ไม่ใช่ localhost)',
        '☐ <font face="Courier">REDIS_URL</font> ชี้ไป production Redis',
        '☐ <font face="Courier">NODE_ENV=production</font>',
        '☐ <font face="Courier">CORS_ORIGIN</font> ตั้ง strict (ไม่ใช่ *)',
        '☐ Migrations applied: <font face="Courier">npx prisma migrate deploy</font>',
        '☐ Tests pass: <font face="Courier">npm test</font>',
        '☐ Build pass: <font face="Courier">npm run build</font>',
        '☐ Health endpoints return 200: <font face="Courier">/health/live</font>, <font face="Courier">/health/ready</font>',
        '☐ Sentry DSN ตั้ง (ถ้าใช้)',
        '☐ Prometheus scrape config ตั้ง (ถ้าใช้)',
        '☐ Backup schedule for PostgreSQL',
        '☐ HTTPS only (no HTTP)',
        '☐ Helmet security headers active',
        '☐ Rate limits ทดสอบแล้ว',
    ]
    for b in bullets:
        elems.append(H(b, 'Bullet', styles))

    return elems


# ============================================================
# Chapter 12 - FAQ
# ============================================================

def chapter_12(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 12: FAQ + Troubleshooting', 'Chapter', styles))

    faqs = [
        ('Q: จะเปลี่ยน stack เป็นอย่างอื่นได้ไหม (Express, Fastify, etc.)?',
         '''A: ไม่ได้ครับ — Phase 1 ของ becraft รองรับแค่ NestJS เท่านั้น
ใน Phase 2 อาจเพิ่ม profiles (FastAPI, Go-Fiber) แต่ตอนนี้แนะนำให้ใช้ NestJS
ซึ่งครอบคลุม use cases 80%+ ของ Solo Developer'''),

        ('Q: ใช้ MongoDB แทน PostgreSQL ได้ไหม?',
         '''A: ตอนนี้ไม่ได้ — becraft ใช้ Prisma + PostgreSQL เพราะ:
1) ACID transactions ที่จำเป็นสำหรับ business apps
2) RLS support สำหรับ multi-tenancy
3) Type safety ที่แน่นอน
ถ้าต้องการ NoSQL จริงๆ ใช้ JSONB columns ใน PostgreSQL ได้'''),

        ('Q: AI สร้างโค้ดผิด แก้ยังไง?',
         '''A: 1) ใช้ <font face="Courier">/be-fix</font> + อธิบายปัญหา
2) ตรวจ memory ที่ <font face="Courier">.be/memory/active.md</font> และ <font face="Courier">changelog.md</font>
3) ถ้ายังไม่ได้ ลอง <font face="Courier">git diff</font> ดูสิ่งที่ AI เปลี่ยน
4) Rollback: <font face="Courier">git checkout .</font>
5) อธิบายให้ AI ใหม่ด้วยข้อมูลที่ชัดขึ้น'''),

        ('Q: Memory เริ่มเต็ม จัดการยังไง?',
         '''A: AI จะ archive ให้อัตโนมัติเมื่อ:
- <font face="Courier">active.md</font> > 50 บรรทัด → snapshot to <font face="Courier">archive/</font>
- <font face="Courier">changelog.md</font> > 200 บรรทัด → ย้ายเก่าออก
ถ้าอยากบังคับ archive: ลบไฟล์ใน <font face="Courier">.be/memory/</font>
แล้วรัน <font face="Courier">becraft install</font> ใหม่ — มันจะ regenerate templates'''),

        ('Q: จะ update becraft เป็น version ใหม่ยังไง?',
         '''A: รัน install อีกครั้งทับเดิม:
<font face="Courier">npx -y github:phitsanu07/becraft@latest install</font>
มันจะถาม "Update or Fresh Install" — เลือก Update
จะ preserve <font face="Courier">.be/memory/</font> ไว้ แต่อัปเดต skills/agents/commands'''),

        ('Q: ใช้ becraft ฟรีไหม?',
         '''A: becraft เป็น MIT license — ฟรี, ใช้ได้ทุกที่ รวมถึง commercial
แต่คุณต้องจ่าย:
- Claude Code subscription (Anthropic)
- Antigravity (free preview ตอนนี้, อนาคตอาจมี paid tier)'''),

        ('Q: ทำงานบน Linux/Windows ได้ไหม?',
         '''A: ได้ครับ — ทดสอบบน macOS แต่ Node.js + Docker ทำงานได้ทุก OS
ปัญหาที่อาจเจอ:
- Windows: WSL2 แนะนำสำหรับ Docker performance ดีกว่า
- Linux: ใช้ได้เลย ไม่มีปัญหา'''),

        ('Q: AI ทำงานช้ามาก แก้ยังไง?',
         '''A: 1) Check internet connection
2) ใน Claude Code: ใช้ Sonnet model (เร็วกว่า Opus, คุณภาพใกล้เคียง)
3) แบ่งงานเป็น chunks เล็กๆ แทน /be-bootstrap ใหญ่
4) ถ้า memory ใหญ่มาก archive ก่อน'''),

        ('Q: Antigravity workflow file ใหญ่ 7,000 บรรทัด — context window พอไหม?',
         '''A: Gemini มี context window 1M tokens ดังนั้นพอเหลือเฟือ
ถ้าเจอปัญหา truncation ลองแบ่งงานเป็น phases เล็กๆ
หรือใช้ <font face="Courier">/be-plan</font> เพื่อ pause หลังแต่ละ phase'''),

        ('Q: จะ contribute เพิ่ม agent หรือ skill ได้ไหม?',
         '''A: ได้ครับ — fork repo บน GitHub, แก้ใน <font face="Courier">src/agents/</font>
หรือ <font face="Courier">src/skills/</font>, รัน <font face="Courier">node scripts/bundle.js</font>
เพื่อ regenerate Antigravity workflows, แล้วส่ง PR'''),
    ]

    for q, a in faqs:
        elems.append(H(q, 'Section', styles))
        elems.append(H(a, 'Body', styles))

    elems.append(H('Troubleshooting Common Errors', 'Section', styles))

    err_data = [
        ['Error', 'สาเหตุ + วิธีแก้'],
        ['<font face="Courier">command not found: becraft</font>',
         'ติดตั้ง global ก่อน: <font face="Courier">npm install -g github:phitsanu07/becraft</font>'],
        ['<font face="Courier">EACCES: permission denied</font>',
         'ใช้ <font face="Courier">npx</font> แทน หรือ <font face="Courier">sudo npm install -g</font>'],
        ['<font face="Courier">DATABASE_URL not set</font>',
         'สร้าง <font face="Courier">.env</font> + ใส่ <font face="Courier">DATABASE_URL=postgresql://...</font>'],
        ['<font face="Courier">Prisma Client not generated</font>',
         'รัน <font face="Courier">npx prisma generate</font>'],
        ['<font face="Courier">Migration drift detected</font>',
         '<font face="Courier">npx prisma migrate reset</font> (DEV only — จะลบ data)'],
        ['<font face="Courier">JWT secret too short</font>',
         '<font face="Courier">openssl rand -base64 32</font> ใส่ใน <font face="Courier">JWT_SECRET</font>'],
        ['<font face="Courier">Connection refused on Redis</font>',
         '<font face="Courier">docker-compose up -d redis</font> หรือเช็ค <font face="Courier">REDIS_URL</font>'],
        ['<font face="Courier">Tests timeout</font>',
         'Testcontainers อาจช้าตอน start — เพิ่ม <font face="Courier">testTimeout: 60000</font>'],
        ['<font face="Courier">Cannot find module &#39;@/...&#39;</font>',
         'เช็ค <font face="Courier">tsconfig.json</font> ว่ามี <font face="Courier">paths</font> mapping'],
    ]
    elems.append(make_table(err_data, col_widths=[6 * cm, 10 * cm]))

    return elems


# ============================================================
# Chapter 13 - Cheat Sheet
# ============================================================

def chapter_13(styles):
    elems = []
    elems.append(PageBreak())
    elems.append(H('บทที่ 13: Cheat Sheet — คำสั่งสรุปแบบรวดเร็ว', 'Chapter', styles))

    elems.append(H('13.1 Installation', 'Section', styles))
    elems.append(code_block('''# Quick install จาก GitHub
npx -y github:phitsanu07/becraft install --quick

# Custom IDE
npx -y github:phitsanu07/becraft install --ide claude

# Specific version
npx github:phitsanu07/becraft#v0.1.0 install

# Local dev
git clone https://github.com/phitsanu07/becraft.git
cd becraft && npm install && npm link

# Status check
becraft status
becraft list'''))

    elems.append(H('13.2 IDE Slash Commands', 'Section', styles))
    elems.append(code_block('''# Smart router
/be ทำอะไรก็ได้

# Help
/be-help

# Planning
/be-plan สร้างระบบ booking
/be-bootstrap user management API

# Domain commands
/be-schema add Product entity
/be-api create CRUD for products
/be-auth setup JWT
/be-observe add metrics
/be-test for products module
/be-fix endpoint /users return 500'''))

    elems.append(H('13.3 NestJS Project Commands', 'Section', styles))
    elems.append(code_block('''# Development
npm install
npm run start:dev          # Watch mode
npm run start:debug        # Debug mode

# Database
npx prisma migrate dev     # Apply pending migrations
npx prisma migrate dev --name add_users
npx prisma generate        # Regenerate client
npx prisma studio          # GUI at localhost:5555
npx prisma migrate reset   # Drop + recreate DB (DEV ONLY)

# Build + Production
npm run build              # Compile TypeScript
npm run start:prod         # Run dist/main.js

# Testing
npm test                   # Unit tests
npm run test:watch         # Watch
npm run test:cov           # Coverage
npm run test:e2e           # E2E with Testcontainers

# Linting
npm run lint               # ESLint
npm run format             # Prettier'''))

    elems.append(H('13.4 Docker Commands', 'Section', styles))
    elems.append(code_block('''# Start services
docker-compose up -d postgres redis      # DB + cache only
docker-compose up -d                     # All including app
docker-compose ps                        # Status
docker-compose logs -f app               # Follow logs
docker-compose down                      # Stop + remove

# Rebuild app
docker-compose build app
docker-compose up -d --build app'''))

    elems.append(H('13.5 Memory Files Reference', 'Section', styles))
    elems.append(code_block('''.be/memory/
├── active.md           # Current task
├── summary.md          # Project overview
├── decisions.md        # ADRs
├── changelog.md        # Session changes
├── agents-log.md       # Agent activity
├── architecture.md     # Service structure
├── api-registry.md     # Endpoints + DTOs
├── schema.md           # DB schema + migrations
├── contracts.md        # OpenAPI snapshots
└── archive/            # Old snapshots (loaded on demand)'''))

    elems.append(H('13.6 Useful URLs (after start:dev)', 'Section', styles))
    url_data = [
        ['URL', 'Purpose'],
        ['http://localhost:3000/docs', 'Swagger UI (interactive)'],
        ['http://localhost:3000/health', 'Overall health'],
        ['http://localhost:3000/health/live', 'Liveness probe (k8s)'],
        ['http://localhost:3000/health/ready', 'Readiness probe (k8s)'],
        ['http://localhost:3000/metrics', 'Prometheus metrics'],
        ['http://localhost:5555', 'Prisma Studio (DB GUI)'],
    ]
    elems.append(make_table(url_data, col_widths=[8 * cm, 8 * cm]))

    elems.append(H('13.7 Environment Variables', 'Section', styles))
    elems.append(code_block('''# Required
DATABASE_URL=postgresql://user:pass@host:5432/db?schema=public
REDIS_URL=redis://host:6379
JWT_SECRET=                           # 32+ random bytes
JWT_REFRESH_SECRET=                   # different from above

# Optional
NODE_ENV=development                  # development|test|production
PORT=3000
LOG_LEVEL=info                        # fatal|error|warn|info|debug|trace
JWT_ACCESS_TTL=15m
JWT_REFRESH_TTL=7d
BCRYPT_ROUNDS=12
CORS_ORIGIN=http://localhost:3000

# Optional (advanced)
SENTRY_DSN=
OTEL_EXPORTER_OTLP_ENDPOINT=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Generate secrets
openssl rand -base64 32'''))

    elems.append(H('13.8 Resources', 'Section', styles))
    res_data = [
        ['Resource', 'URL'],
        ['becraft repo', 'https://github.com/phitsanu07/becraft'],
        ['NestJS docs', 'https://docs.nestjs.com'],
        ['Prisma docs', 'https://www.prisma.io/docs'],
        ['Pino docs', 'https://getpino.io'],
        ['Testcontainers', 'https://node.testcontainers.org'],
        ['OpenAPI spec', 'https://www.openapis.org'],
        ['Claude Code', 'https://claude.com/code'],
        ['Antigravity', 'https://labs.google/antigravity'],
    ]
    elems.append(make_table(res_data, col_widths=[5 * cm, 11 * cm]))

    # Closing
    elems.append(PageBreak())
    elems.append(Spacer(1, 4 * cm))
    elems.append(Paragraph('🛠️ becraft', styles['Title']))
    elems.append(Spacer(1, 0.5 * cm))
    elems.append(Paragraph('"Craft Production Backends, Not Prototypes"',
                            styles['Subtitle']))
    elems.append(Spacer(1, 2 * cm))
    elems.append(Paragraph('คู่มือฉบับนี้ขอจบลงเพียงเท่านี้',
                            styles['BodyCenter']))
    elems.append(Paragraph('ขอให้สนุกกับการสร้าง backend ระดับ production!',
                            styles['BodyCenter']))
    elems.append(Spacer(1, 1 * cm))
    elems.append(Paragraph('— ทีม becraft', styles['BodyCenter']))

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
        title='becraft — คู่มือการใช้งาน',
        author='becraft contributors',
        subject='Contract-Driven Backend Development',
    )

    # Frames
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

    # Templates
    cover_template = PageTemplate(
        id='cover', frames=[cover_frame], onPage=cover_page,
    )
    body_template = PageTemplate(
        id='body', frames=[body_frame], onPage=page_header_footer,
    )

    doc.addPageTemplates([cover_template, body_template])

    # Build story
    story = []

    # Cover
    story.extend(build_cover(styles))
    story.append(NextPageTemplate('body'))
    story.append(PageBreak())

    # TOC
    story.extend(build_toc(styles))

    # Chapters
    story.extend(chapter_1(styles))
    story.extend(chapter_2(styles))
    story.extend(chapter_3(styles))
    story.extend(chapter_4(styles))
    story.extend(chapter_5(styles))
    story.extend(chapter_6(styles))
    story.extend(chapter_7(styles))
    story.extend(chapter_8(styles))
    story.extend(chapter_9(styles))
    story.extend(chapter_10(styles))
    story.extend(chapter_11(styles))
    story.extend(chapter_12(styles))
    story.extend(chapter_13(styles))

    doc.build(story)
    print(f"✅ Generated: {OUTPUT}")
    print(f"   Size: {OUTPUT.stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    build_pdf()
