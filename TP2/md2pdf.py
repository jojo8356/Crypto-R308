import argparse
import os
import markdown
from playwright.sync_api import sync_playwright
from pygments.formatters import HtmlFormatter


def convert_md_to_pdf(
    md_filepath,
    pdf_filepath,
    css_filepath="style.css",
    template_filepath="template.html",
):
    if not os.path.exists(md_filepath):
        print(f"❌ Erreur : Fichier Markdown '{md_filepath}' introuvable.")
        return
    if not os.path.exists(template_filepath):
        print(
            f"❌ Erreur : Fichier HTML modèle '{template_filepath}' introuvable."
        )
        return

    with open(md_filepath, "r", encoding="utf-8") as f:
        md_text = f.read()

    with open(template_filepath, "r", encoding="utf-8") as f:
        template_html = f.read()

    custom_css = ""
    if os.path.exists(css_filepath):
        with open(css_filepath, "r", encoding="utf-8") as f:
            custom_css = f.read()

    pygments_css = HtmlFormatter(style="github-dark").get_style_defs(
        ".codehilite"
    )

    # Configuration assouplie pour les maths ($ et $$)
    html_content = markdown.markdown(
        md_text,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "pymdownx.arithmatex",
        ],
        extension_configs={
            "pymdownx.arithmatex": {
                "generic": True,
                "smart_dollar": False,  # Permet de capturer $ et $$ plus souplement
            }
        },
    )

    full_html = (
        template_html.replace("{{CONTENT}}", html_content)
        .replace("{{CUSTOM_CSS}}", custom_css)
        .replace("{{PYGMENTS_CSS}}", pygments_css)
    )

    temp_html_path = "temp_render.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"Génération du PDF : {pdf_filepath}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(
            f"file://{os.path.abspath(temp_html_path)}", wait_until="networkidle"
        )

        try:
            page.wait_for_selector(".katex", timeout=5000)
        except Exception:
            pass

        page.wait_for_timeout(500)

        footer_template = """
        <div style="width: 100%; font-size: 9px; display: flex; justify-content: flex-end; padding-right: 30px; color: #666;">
            <span class="pageNumber"></span> / <span class="totalPages"></span>
        </div>
        """

        page.pdf(
            path=pdf_filepath,
            format="A4",
            margin={
                "top": "20mm",
                "bottom": "20mm",
                "left": "20mm",
                "right": "20mm",
            },
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=footer_template,
            print_background=True,
        )
        browser.close()

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

    print("✅ PDF généré proprement sans $ parasites !")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convertisseur Markdown vers PDF"
    )
    parser.add_argument("input", help="Fichier Markdown source (.md)")
    parser.add_argument(
        "-o",
        "--output",
        help="Fichier PDF de sortie (.pdf)",
        default="output.pdf",
    )
    parser.add_argument(
        "-c", "--css", help="Fichier CSS personnalisé", default="style.css"
    )
    parser.add_argument(
        "-t",
        "--template",
        help="Fichier Modèle HTML",
        default="template.html",
    )

    args = parser.parse_args()
    convert_md_to_pdf(args.input, args.output, args.css, args.template)