# PDF download toegevoegd
import os
import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
from styles import CSS, JS, EXAMPLES, HEADER_HTML

# Probeer fpdf2 te importeren voor de PDF-functionaliteit
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

load_dotenv(override=True)

# ==========================================
# CONFIGURATIE: Zet op True of False
# ==========================================
ENABLE_PDF_DOWNLOAD = True  


def generate_pdf_report(content: str, filename="research_report.pdf") -> str:
    """Genereert een PDF-bestand op basis van de rapporttekst."""
    if not PDF_AVAILABLE:
        return None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    # Zet de tekst om naar een veilig formaat voor de PDF-generator
    safe_content = content.encode('latin-1', 'replace').decode('latin-1')
    
    for line in safe_content.split('\n'):
        pdf.multi_cell(0, 8, txt=line)
        
    pdf.output(filename)
    return filename


async def run(query: str):
    full_report = ""
    async for status_update in ResearchManager().run(query):
        full_report = status_update
        if ENABLE_PDF_DOWNLOAD and PDF_AVAILABLE:
            yield status_update, gr.update(visible=False)
        else:
            yield status_update, gr.update(visible=False)
            
    # Als de stream klaar is en PDF staat aan, genereer het bestand en toon de downloadknop
    if ENABLE_PDF_DOWNLOAD and PDF_AVAILABLE and full_report:
        pdf_path = generate_pdf_report(full_report)
        yield full_report, gr.update(value=pdf_path, visible=True)
    else:
        yield full_report, gr.update(visible=False)


with gr.Blocks(title="Deep Research") as ui:
    gr.HTML(HEADER_HTML)

    with gr.Row(elem_classes="dr-query-row"):
        query_textbox = gr.Textbox(
            placeholder="Type a research question...",
            show_label=False,
            container=False,
            autofocus=True,
            elem_id="dr-query",
            scale=5,
        )
        run_button = gr.Button("Investigate", variant="primary", elem_id="dr-run", scale=1)

    gr.HTML('<div class="dr-examples-label">Try one</div>')
    gr.Examples(examples=EXAMPLES, inputs=query_textbox, elem_id="dr-examples")

    report = gr.Markdown(elem_id="dr-report")
    
    # Downloadknop voor de PDF (standaard onzichtbaar tot het rapport klaar is)
    download_btn = gr.DownloadButton(
        "📥 Download Report as PDF", 
        visible=False, 
        elem_id="dr-download"
    )

    # Dynamisch de outputs koppelen op basis van de boolean
    if ENABLE_PDF_DOWNLOAD:
        outputs_list = [report, download_btn]
    else:
        outputs_list = [report]

    run_button.click(run, inputs=query_textbox, outputs=outputs_list)
    query_textbox.submit(run, inputs=query_textbox, outputs=outputs_list)


if __name__ == "__main__":
    ui.launch(css=CSS, js=JS, theme=gr.themes.Base())