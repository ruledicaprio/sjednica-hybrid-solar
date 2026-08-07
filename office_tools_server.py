import os
import platform
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
DEFAULT_SOFFICE = (
    r"C:\Program Files\LibreOffice\program\soffice.exe"
    if platform.system() == "Windows"
    else "/usr/bin/soffice"
)

# Allows overriding via environment variable
SOFFICE_PATH = os.getenv("SOFFICE_PATH", DEFAULT_SOFFICE)

if not os.path.exists(SOFFICE_PATH):
    import warnings
    warnings.warn(f"LibreOffice not found at {SOFFICE_PATH}. Tools requiring conversion will fail.")

# -------------------------------------------------------------------
# Helper: run LibreOffice headless (Asynchronous)
# -------------------------------------------------------------------
async def _run_libreoffice(input_file: str, output_dir: str, out_format: str) -> None:
    """Run LibreOffice in headless mode to convert documents."""
    cmd = [
        SOFFICE_PATH,
        "--headless",
        "--convert-to", out_format,
        "--outdir", output_dir,
        input_file
    ]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise RuntimeError(f"LibreOffice conversion failed with code {process.returncode}:\n{stderr.decode()}")

# -------------------------------------------------------------------
# Tool implementations
# -------------------------------------------------------------------
async def read_document_tool(file_path: str) -> str:
    """Convert a document (.doc, .docx, .odt) to text and return its contents."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    output_dir = str(path.parent)
    # convert-to txt:Text extracts raw text without formatting
    await _run_libreoffice(str(path), output_dir, "txt:Text")
    
    txt_path = path.with_suffix('.txt')
    if not txt_path.exists():
        raise RuntimeError("Text conversion failed.")
        
    return txt_path.read_text(encoding="utf-8", errors="replace")

async def read_spreadsheet_tool(file_path: str) -> str:
    """Convert a spreadsheet (.xls, .xlsx, .ods) to CSV and return its contents."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    output_dir = str(path.parent)
    await _run_libreoffice(str(path), output_dir, "csv")
    
    csv_path = path.with_suffix('.csv')
    if not csv_path.exists():
        raise RuntimeError("CSV conversion failed.")
        
    return csv_path.read_text(encoding="utf-8", errors="replace")

# -------------------------------------------------------------------
# MCP server boilerplate
# -------------------------------------------------------------------
app = Server("office-tools")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="read_document",
            description="Extract text from Word/Writer documents (.doc, .docx, .odt) using LibreOffice",
            inputSchema={
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        ),
        Tool(
            name="read_spreadsheet",
            description="Extract data from Excel/Calc spreadsheets (.xls, .xlsx, .ods) as CSV using LibreOffice",
            inputSchema={
                "type": "object",
                "properties": {"file_path": {"type": "string"}},
                "required": ["file_path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result_text = ""
    if name == "read_document":
        result_text = await read_document_tool(**arguments)
    elif name == "read_spreadsheet":
        result_text = await read_spreadsheet_tool(**arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [TextContent(type="text", text=result_text)]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())