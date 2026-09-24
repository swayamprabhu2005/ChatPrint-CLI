"""Platypus document builder that compiles a Conversation model into a clean PDF."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from chatprint.errors import PDFGenerationError
from chatprint.models import (
    CitationBlock,
    CodeBlock,
    Conversation,
    HeadingBlock,
    ListBlock,
    ParagraphBlock,
    Role,
    TableBlock,
)
from chatprint.pdf.assets import safe_reportlab_text
from chatprint.pdf.styles import (
    BG_CODE,
    BORDER_CODE,
    BORDER_LIGHT,
    NumberedCanvas,
    get_pdf_styles,
)


def render_conversation_to_pdf(conversation: Conversation, output_path: Path) -> Path:
    """Render a normalized Conversation object to a professional PDF document.

    Args:
        conversation: Extracted Conversation model.
        output_path: Target PDF destination file path.

    Returns:
        Path to the successfully created PDF.

    Raises:
        PDFGenerationError: If PDF compilation or write fails.
    """
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        doc = SimpleDocTemplate(
            str(path),
            pagesize=letter,
            leftMargin=40,
            rightMargin=40,
            topMargin=50,
            bottomMargin=50,
        )

        styles = get_pdf_styles()
        story = []

        # Document Title
        title_text = safe_reportlab_text(conversation.title or "AI Conversation")
        story.append(Paragraph(title_text, styles["DocTitle"]))

        # Metadata banner: Source, Date, Turns
        date_str = conversation.detected_at.strftime("%B %d, %Y")
        meta_text = (
            f"<b>Source:</b> {conversation.source} &nbsp;|&nbsp; "
            f"<b>Date:</b> {date_str} &nbsp;|&nbsp; "
            f"<b>Messages:</b> {conversation.total_messages_count}"
        )
        story.append(Paragraph(meta_text, styles["DocMeta"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceAfter=14))

        # Render each turn
        usable_width = 532  # 612 letter width - 80 margins

        for msg in conversation.messages:
            turn_flowables = []

            # Turn Header
            if msg.role == Role.USER:
                role_label = "User"
                turn_flowables.append(Paragraph(role_label, styles["UserBadge"]))
            else:
                role_label = conversation.source if conversation.source else "Assistant"
                turn_flowables.append(Paragraph(role_label, styles["AssistantBadge"]))

            # Turn Content Blocks
            for block in msg.blocks:
                if isinstance(block, ParagraphBlock):
                    clean_p = safe_reportlab_text(block.text)
                    if clean_p:
                        turn_flowables.append(Paragraph(clean_p, styles["ConvBody"]))

                elif isinstance(block, HeadingBlock):
                    style_key = "ConvH1" if block.level <= 2 else "ConvH2"
                    clean_h = safe_reportlab_text(block.text)
                    if clean_h:
                        turn_flowables.append(Paragraph(clean_h, styles[style_key]))

                elif isinstance(block, ListBlock):
                    for i, item in enumerate(block.items, start=1):
                        prefix = f"{i}. " if block.ordered else "&bull; "
                        item_text = prefix + safe_reportlab_text(item)
                        turn_flowables.append(Paragraph(item_text, styles["ConvList"]))
                    turn_flowables.append(Spacer(1, 4))

                elif isinstance(block, CodeBlock):
                    # Code inside a shaded box table
                    code_lines = block.code.splitlines()
                    # Truncate very wide lines to avoid overflow
                    wrapped_code = "\n".join(
                        line[:95] + ("..." if len(line) > 95 else "")
                        for line in code_lines
                    )
                    header_label = f"[{block.language}]" if block.language else "[Code]"
                    code_header = Paragraph(f"<b>{header_label}</b>", styles["DocMeta"])
                    code_para = Preformatted(wrapped_code, styles["ConvCode"])

                    code_table = Table(
                        [[code_header], [code_para]],
                        colWidths=[usable_width],
                    )
                    code_table.setStyle(
                        TableStyle([
                            ("BACKGROUND", (0, 0), (-1, -1), BG_CODE),
                            ("BOX", (0, 0), (-1, -1), 0.5, BORDER_CODE),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                            ("LEFTPADDING", (0, 0), (-1, -1), 8),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ])
                    )
                    turn_flowables.append(Spacer(1, 4))
                    turn_flowables.append(code_table)
                    turn_flowables.append(Spacer(1, 6))

                elif isinstance(block, TableBlock):
                    table_data = []
                    if block.headers:
                        table_data.append([
                            Paragraph(safe_reportlab_text(h), styles["ConvTableHead"])
                            for h in block.headers
                        ])
                    for row in block.rows:
                        table_data.append([
                            Paragraph(safe_reportlab_text(cell), styles["ConvTableCell"])
                            for cell in row
                        ])

                    if table_data:
                        num_cols = max(len(r) for r in table_data)
                        col_w = usable_width / max(num_cols, 1)
                        t = Table(table_data, colWidths=[col_w] * num_cols)
                        t.setStyle(
                            TableStyle([
                                ("BACKGROUND", (0, 0), (-1, 0), BG_CODE),
                                ("GRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                            ])
                        )
                        turn_flowables.append(Spacer(1, 4))
                        turn_flowables.append(t)
                        turn_flowables.append(Spacer(1, 6))

                elif isinstance(block, CitationBlock):
                    cite_text = safe_reportlab_text(block.text)
                    if block.url:
                        cite_para = Paragraph(
                            f'Reference: <link href="{block.url}" color="#2563eb"><u>{cite_text}</u></link>',
                            styles["DocMeta"],
                        )
                    else:
                        cite_para = Paragraph(f"Reference: {cite_text}", styles["DocMeta"])
                    turn_flowables.append(cite_para)

            # Turn spacing
            turn_flowables.append(Spacer(1, 10))
            turn_flowables.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceAfter=8))
            story.extend(turn_flowables)

        doc.build(story, canvasmaker=NumberedCanvas)

    except Exception as e:
        raise PDFGenerationError(
            f"Failed to generate PDF document at {path.name}: {e}",
            suggestion="Ensure the destination path is writable and file is not open in another viewer.",
        ) from e

    return path
