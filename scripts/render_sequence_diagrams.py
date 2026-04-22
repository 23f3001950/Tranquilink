from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "sequence-diagrams.jpg"

WIDTH = 3200
PAGE_MARGIN = 110
SECTION_GAP = 42
SECTION_SIDE_PAD = 52
HEADER_HEIGHT = 190
PARTICIPANT_BOX_HEIGHT = 64
PARTICIPANT_BOX_WIDTH = 240
LIFELINE_TOP_GAP = 22
MESSAGE_LEFT_PAD = 34
MESSAGE_RIGHT_PAD = 34

BG = "#f6f2ea"
TEXT = "#1d232b"
SUBTEXT = "#566170"
LINE = "#3b4654"
LIFELINE = "#8fa0b3"
LABEL_BG = "#fffffff2"
LABEL_OUTLINE = "#d3dbe4"


SECTIONS = [
    {
        "title": "1. Student Support Journey",
        "subtitle": "Landing page, login, dashboard, mood tracking, and TranquilBot chat.",
        "fill": "#fff8ea",
        "accent": "#d89a2f",
        "participants": ["Student", "Flask App", "Session", "SQLite DB"],
        "items": [
            {"kind": "phase", "label": "Discovery and login"},
            {"src": 0, "dst": 1, "label": "GET /"},
            {"src": 1, "dst": 3, "label": "SELECT approved counsellors"},
            {"src": 3, "dst": 1, "label": "counsellor list", "dashed": True},
            {"src": 1, "dst": 0, "label": "render landing page", "dashed": True},
            {"src": 0, "dst": 1, "label": "POST /register or /login"},
            {"src": 1, "dst": 3, "label": "INSERT user or SELECT user"},
            {"src": 3, "dst": 1, "label": "account result or student row", "dashed": True},
            {"src": 1, "dst": 2, "label": "store user_id, username, role"},
            {"src": 1, "dst": 0, "label": "redirect to /dashboard", "dashed": True},
            {"kind": "phase", "label": "Student activity"},
            {"src": 0, "dst": 1, "label": "GET /dashboard"},
            {"src": 1, "dst": 3, "label": "load appointments, mood logs, exercises"},
            {"src": 3, "dst": 1, "label": "dashboard datasets", "dashed": True},
            {"src": 1, "dst": 0, "label": "render dashboard", "dashed": True},
            {"src": 0, "dst": 1, "label": "POST /mood or /chat/send"},
            {"src": 1, "dst": 3, "label": "save mood entry or user chat message"},
            {"src": 1, "dst": 1, "label": "run ai_response()"},
            {"src": 1, "dst": 3, "label": "save bot reply"},
            {"src": 1, "dst": 0, "label": "redirect or JSON reply (urgent/non-urgent)", "dashed": True},
        ],
    },
    {
        "title": "2. Appointment and Review Flow",
        "subtitle": "Student booking, counsellor or admin updates, and post-session review.",
        "fill": "#eef7ff",
        "accent": "#2d78d2",
        "participants": ["Student", "Flask App", "SQLite DB", "Counsellor", "Admin"],
        "items": [
            {"kind": "phase", "label": "Booking"},
            {"src": 0, "dst": 1, "label": "GET /appointments"},
            {"src": 1, "dst": 2, "label": "SELECT approved counsellors and history"},
            {"src": 2, "dst": 1, "label": "counsellor list and appointments", "dashed": True},
            {"src": 1, "dst": 0, "label": "render booking page", "dashed": True},
            {"src": 0, "dst": 1, "label": "POST /appointments"},
            {"src": 1, "dst": 2, "label": "INSERT appointment (status=pending)"},
            {"src": 2, "dst": 1, "label": "appointment created", "dashed": True},
            {"src": 1, "dst": 0, "label": "success message and redirect", "dashed": True},
            {"kind": "phase", "label": "Management and follow-up"},
            {"src": 3, "dst": 1, "label": "GET /counsellor/dashboard"},
            {"src": 1, "dst": 2, "label": "SELECT appointments, emergencies, reviews"},
            {"src": 2, "dst": 1, "label": "dashboard datasets", "dashed": True},
            {"src": 1, "dst": 3, "label": "render counsellor dashboard", "dashed": True},
            {"src": 3, "dst": 1, "label": "POST /counsellor/appointment/:id/update"},
            {"src": 1, "dst": 2, "label": "UPDATE status and counsellor_notes"},
            {"src": 2, "dst": 1, "label": "appointment updated", "dashed": True},
            {"src": 4, "dst": 1, "label": "POST /admin/appointment/:id/update"},
            {"src": 1, "dst": 2, "label": "UPDATE status"},
            {"src": 1, "dst": 4, "label": "redirect to admin dashboard", "dashed": True},
            {"src": 0, "dst": 1, "label": "GET and POST /counsellor/:cid/review"},
            {"src": 1, "dst": 2, "label": "SELECT completed appointments; INSERT review"},
            {"src": 2, "dst": 1, "label": "eligible sessions or review saved", "dashed": True},
            {"src": 1, "dst": 3, "label": "review appears in /counsellor/reviews", "dashed": True},
        ],
    },
    {
        "title": "3. Counsellor Approval and Admin Oversight",
        "subtitle": "Counsellor onboarding, admin approvals, exercises, emergency cases, and campaigns.",
        "fill": "#effaef",
        "accent": "#3c9b56",
        "participants": ["Counsellor", "Flask App", "SQLite DB", "Session", "Admin", "Student"],
        "items": [
            {"kind": "phase", "label": "Approval lifecycle"},
            {"src": 0, "dst": 1, "label": "POST /counsellor/register"},
            {"src": 1, "dst": 2, "label": "INSERT counsellor (approved=0)"},
            {"src": 2, "dst": 1, "label": "pending counsellor record", "dashed": True},
            {"src": 1, "dst": 0, "label": "show admin approval required", "dashed": True},
            {"src": 4, "dst": 1, "label": "GET /admin"},
            {"src": 1, "dst": 2, "label": "SELECT stats, pending counsellors, campaigns"},
            {"src": 2, "dst": 1, "label": "analytics and approval queue", "dashed": True},
            {"src": 1, "dst": 4, "label": "render admin dashboard", "dashed": True},
            {"src": 4, "dst": 1, "label": "POST approve or reject counsellor"},
            {"src": 1, "dst": 2, "label": "UPDATE approved flag or DELETE counsellor"},
            {"src": 0, "dst": 1, "label": "POST /login (counsellor)"},
            {"src": 1, "dst": 2, "label": "SELECT counsellor by email and password"},
            {"src": 2, "dst": 1, "label": "approved or pending counsellor row", "dashed": True},
            {"src": 1, "dst": 3, "label": "store counsellor_id, username, role"},
            {"src": 1, "dst": 0, "label": "redirect to /counsellor/dashboard", "dashed": True},
            {"kind": "phase", "label": "Ongoing care and reporting"},
            {"src": 0, "dst": 1, "label": "POST /counsellor/exercises"},
            {"src": 1, "dst": 2, "label": "INSERT general or student-specific exercise"},
            {"src": 1, "dst": 5, "label": "exercise appears in /dashboard and /exercises", "dashed": True},
            {"src": 0, "dst": 1, "label": "POST /counsellor/emergency"},
            {"src": 1, "dst": 2, "label": "INSERT emergency_appointments row"},
            {"src": 1, "dst": 4, "label": "open emergency counted on /admin", "dashed": True},
            {"src": 4, "dst": 1, "label": "POST /admin/campaigns or /toggle"},
            {"src": 1, "dst": 2, "label": "INSERT or UPDATE campaign status"},
            {"src": 1, "dst": 4, "label": "refresh campaigns page", "dashed": True},
        ],
    },
]


def load_font(size, bold=False):
    candidates = []
    if bold:
        candidates.extend(
            [
                "C:/Windows/Fonts/segoeuib.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                "C:/Windows/Fonts/segoeui.ttf",
                "C:/Windows/Fonts/arial.ttf",
            ]
        )

    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = load_font(52, bold=True)
SUBTITLE_FONT = load_font(24)
SECTION_FONT = load_font(34, bold=True)
SECTION_SUB_FONT = load_font(22)
PARTICIPANT_FONT = load_font(22, bold=True)
PHASE_FONT = load_font(20, bold=True)
MESSAGE_FONT = load_font(22)
FOOTER_FONT = load_font(18)


def text_size(draw, text, font):
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def wrap_text(draw, text, font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def dashed_line(draw, start, end, fill, width=3, dash=12, gap=8):
    x1, y1 = start
    x2, y2 = end
    total = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    if total == 0:
        return
    dx = (x2 - x1) / total
    dy = (y2 - y1) / total
    dist = 0
    while dist < total:
        seg_end = min(dist + dash, total)
        sx = x1 + dx * dist
        sy = y1 + dy * dist
        ex = x1 + dx * seg_end
        ey = y1 + dy * seg_end
        draw.line((sx, sy, ex, ey), fill=fill, width=width)
        dist += dash + gap


def arrowhead(draw, x, y, direction, fill):
    size = 16
    if direction == "right":
        points = [(x, y), (x - size, y - 8), (x - size, y + 8)]
    elif direction == "left":
        points = [(x, y), (x + size, y - 8), (x + size, y + 8)]
    elif direction == "down":
        points = [(x, y), (x - 8, y - size), (x + 8, y - size)]
    else:
        points = [(x, y), (x - 8, y + size), (x + 8, y + size)]
    draw.polygon(points, fill=fill)


def multiline_metrics(draw, lines, font, spacing=6):
    widths = []
    heights = []
    for line in lines:
        width, height = text_size(draw, line, font)
        widths.append(width)
        heights.append(height)
    total_height = sum(heights) + spacing * max(0, len(lines) - 1)
    return max(widths, default=0), total_height, heights


def prepare_section(draw, section):
    left = PAGE_MARGIN
    right = WIDTH - PAGE_MARGIN
    count = len(section["participants"])
    content_width = right - left - 2 * SECTION_SIDE_PAD
    step = content_width / max(1, count - 1)
    participant_x = [left + SECTION_SIDE_PAD + step * idx for idx in range(count)]

    prepared = []
    total_height = 0
    for item in section["items"]:
        if item.get("kind") == "phase":
            item_copy = dict(item)
            item_copy["height"] = 56
            prepared.append(item_copy)
            total_height += item_copy["height"]
            continue

        item_copy = dict(item)
        if item["src"] == item["dst"]:
            label_width = 330
        else:
            label_width = abs(participant_x[item["dst"]] - participant_x[item["src"]]) - 180
            label_width = max(210, label_width)
        lines = wrap_text(draw, item["label"], MESSAGE_FONT, label_width)
        label_w, label_h, line_heights = multiline_metrics(draw, lines, MESSAGE_FONT)
        item_copy["lines"] = lines
        item_copy["label_width"] = label_w
        item_copy["label_height"] = label_h
        item_copy["line_heights"] = line_heights
        item_copy["height"] = label_h + 42 if item["src"] != item["dst"] else label_h + 78
        prepared.append(item_copy)
        total_height += item_copy["height"]

    panel_height = 165 + total_height + 90
    return participant_x, prepared, panel_height


def draw_label(draw, x, y, lines):
    label_w, label_h, line_heights = multiline_metrics(draw, lines, MESSAGE_FONT)
    box = (
        x - label_w / 2 - MESSAGE_LEFT_PAD / 2,
        y,
        x + label_w / 2 + MESSAGE_RIGHT_PAD / 2,
        y + label_h + 18,
    )
    draw.rounded_rectangle(box, radius=16, fill=LABEL_BG, outline=LABEL_OUTLINE, width=2)
    text_y = y + 9
    for idx, line in enumerate(lines):
        line_w, _ = text_size(draw, line, MESSAGE_FONT)
        draw.text((x - line_w / 2, text_y), line, fill=TEXT, font=MESSAGE_FONT)
        text_y += line_heights[idx] + 6
    return box


def draw_section(draw, top, section):
    participant_x, items, panel_height = prepare_section(draw, section)
    left = PAGE_MARGIN
    right = WIDTH - PAGE_MARGIN
    bottom = top + panel_height

    draw.rounded_rectangle((left, top, right, bottom), radius=34, fill=section["fill"], outline=section["accent"], width=3)

    draw.text((left + 36, top + 28), section["title"], fill=TEXT, font=SECTION_FONT)
    draw.text((left + 36, top + 74), section["subtitle"], fill=SUBTEXT, font=SECTION_SUB_FONT)

    box_top = top + 118
    lifeline_bottom = bottom - 36
    for idx, label in enumerate(section["participants"]):
        cx = participant_x[idx]
        box = (
            cx - PARTICIPANT_BOX_WIDTH / 2,
            box_top,
            cx + PARTICIPANT_BOX_WIDTH / 2,
            box_top + PARTICIPANT_BOX_HEIGHT,
        )
        draw.rounded_rectangle(box, radius=18, fill="white", outline=section["accent"], width=3)
        w, h = text_size(draw, label, PARTICIPANT_FONT)
        draw.text((cx - w / 2, box_top + (PARTICIPANT_BOX_HEIGHT - h) / 2 - 2), label, fill=TEXT, font=PARTICIPANT_FONT)
        dashed_line(draw, (cx, box_top + PARTICIPANT_BOX_HEIGHT + LIFELINE_TOP_GAP), (cx, lifeline_bottom), fill=LIFELINE, width=2)

    y = box_top + PARTICIPANT_BOX_HEIGHT + 42
    for item in items:
        if item.get("kind") == "phase":
            pill_w = draw.textlength(item["label"], font=PHASE_FONT) + 30
            pill = (left + 32, y - 4, left + 32 + pill_w, y + 30)
            draw.rounded_rectangle(pill, radius=15, fill=section["accent"], outline=section["accent"])
            draw.text((pill[0] + 15, y + 2), item["label"], fill="white", font=PHASE_FONT)
            y += item["height"]
            continue

        if item["src"] == item["dst"]:
            cx = participant_x[item["src"]]
            box = draw_label(draw, cx + 96, y, item["lines"])
            line_y = box[3] + 14
            right_x = cx + 132
            lower_y = line_y + 28
            draw.line((cx + 28, line_y, right_x, line_y), fill=LINE, width=4)
            draw.line((right_x, line_y, right_x, lower_y), fill=LINE, width=4)
            draw.line((right_x, lower_y, cx + 28, lower_y), fill=LINE, width=4)
            arrowhead(draw, cx + 28, lower_y, "left", LINE)
        else:
            x1 = participant_x[item["src"]]
            x2 = participant_x[item["dst"]]
            mid_x = (x1 + x2) / 2
            box = draw_label(draw, mid_x, y, item["lines"])
            line_y = box[3] + 14
            direction = 1 if x2 > x1 else -1
            start_x = x1 + direction * (PARTICIPANT_BOX_WIDTH / 2 - 18)
            end_x = x2 - direction * (PARTICIPANT_BOX_WIDTH / 2 - 18)
            if item.get("dashed"):
                dashed_line(draw, (start_x, line_y), (end_x, line_y), fill=LINE, width=3)
            else:
                draw.line((start_x, line_y, end_x, line_y), fill=LINE, width=4)
            arrowhead(draw, end_x, line_y, "right" if direction == 1 else "left", LINE)
        y += item["height"]

    return bottom


def build_image():
    image = Image.new("RGBA", (WIDTH, 100), BG)
    draw = ImageDraw.Draw(image)

    heights = []
    for section in SECTIONS:
        _, _, panel_height = prepare_section(draw, section)
        heights.append(panel_height)

    total_height = HEADER_HEIGHT + sum(heights) + SECTION_GAP * (len(SECTIONS) - 1) + PAGE_MARGIN
    image = Image.new("RGBA", (WIDTH, total_height), BG)
    draw = ImageDraw.Draw(image)

    draw.text((PAGE_MARGIN, 44), "TranquiLink Sequence Diagram Overview", fill=TEXT, font=TITLE_FONT)
    draw.text(
        (PAGE_MARGIN, 108),
        "JPEG export generated from the Flask routes and database interactions in app.py.",
        fill=SUBTEXT,
        font=SUBTITLE_FONT,
    )

    y = HEADER_HEIGHT
    for section in SECTIONS:
        y = draw_section(draw, y, section) + SECTION_GAP

    footer = f"Output: {OUTPUT.relative_to(ROOT)}"
    draw.text((PAGE_MARGIN, total_height - 46), footer, fill=SUBTEXT, font=FOOTER_FONT)

    image.convert("RGB").save(OUTPUT, "JPEG", quality=92, subsampling=0)


if __name__ == "__main__":
    build_image()
    print(OUTPUT)
