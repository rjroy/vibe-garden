#!/usr/bin/env python3
"""
PDF to Markdown converter with maximum losslessness
"""
import subprocess
import sys
from pathlib import Path

def pdf_to_markdown(pdf_path: str, output_path: str = None):
    """Convert PDF to markdown preserving as much formatting as possible"""

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    # Determine output path
    if output_path is None:
        output_path = pdf_file.with_suffix('.md')
    else:
        output_path = Path(output_path)

    print(f"Converting {pdf_file} to {output_path}...")

    # Use pdftotext with layout preservation
    try:
        # First try with -layout flag to preserve formatting
        result = subprocess.run(
            ['pdftotext', '-layout', '-nopgbrk', str(pdf_file), '-'],
            capture_output=True,
            text=True,
            check=True
        )
        text = result.stdout

        # Clean up and format as markdown
        lines = text.split('\n')
        markdown_lines = []

        prev_blank = False
        for line in lines:
            stripped = line.rstrip()

            # Skip excessive blank lines
            if not stripped:
                if not prev_blank:
                    markdown_lines.append('')
                    prev_blank = True
                continue

            prev_blank = False
            markdown_lines.append(stripped)

        markdown_content = '\n'.join(markdown_lines)

        # Write output
        output_path.write_text(markdown_content, encoding='utf-8')
        print(f"✓ Successfully converted to {output_path}")
        print(f"  Original: {pdf_file.stat().st_size / 1024:.1f} KB")
        print(f"  Markdown: {output_path.stat().st_size / 1024:.1f} KB")

    except subprocess.CalledProcessError as e:
        print(f"Error converting PDF: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert_pdf.py <pdf_file> [output_file]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    pdf_to_markdown(pdf_path, output_path)
