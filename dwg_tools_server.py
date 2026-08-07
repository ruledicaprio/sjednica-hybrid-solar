import os
import platform
import asyncio
import json
from pathlib import Path

import ezdxf
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
DEFAULT_ODA = (
    r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
    if platform.system() == "Windows"
    else "/usr/local/bin/ODAFileConverter"
)

# Allows overriding via environment variable 
ODA_CONVERTER = os.getenv("ODA_CONVERTER_PATH", DEFAULT_ODA)

if not os.path.exists(ODA_CONVERTER):
    import warnings
    warnings.warn(f"ODA Converter not found at {ODA_CONVERTER}. Tools requiring conversion will fail.")

# -------------------------------------------------------------------
# Helper: run ODA File Converter DWG <-> DXF (Asynchronous)
# -------------------------------------------------------------------
async def _run_oda(input_file: str, output_dir: str, to_dxf: bool = True) -> None:
    """Convert between DWG and DXF using ODA File Converter asynchronously."""
    version = "ACAD2018"
    audit = "true"
    ext, in_filter, out_filter = ("dxf", "*.dwg", "*.dxf") if to_dxf else ("dwg", "*.dxf", "*.dwg")

    cmd = [
        ODA_CONVERTER,
        str(Path(input_file).parent),
        output_dir,
        version,
        ext.upper(),
        audit,
        "true",
        in_filter,
        out_filter
    ]
    
    # Non-blocking subprocess execution
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise RuntimeError(f"ODA Converter failed with code {process.returncode}:\n{stderr.decode()}")

# -------------------------------------------------------------------
# Tool implementations
# -------------------------------------------------------------------
async def dwg_to_dxf_tool(dwg_path: str, output_dir: str = None) -> str:
    """Convert a .dwg to .dxf and return the .dxf path."""
    dwg = Path(dwg_path)
    if not dwg.exists():
        raise FileNotFoundError(f"DWG file not found: {dwg_path}")
    
    # Keep intermediate files next to the source unless told otherwise
    if output_dir is None:
        output_dir = str(dwg.parent)
    else:
        os.makedirs(output_dir, exist_ok=True)

    await _run_oda(str(dwg), output_dir, to_dxf=True)
    dxf_name = dwg.stem + ".dxf"
    dxf_path = Path(output_dir) / dxf_name
    
    if not dxf_path.exists():
        raise RuntimeError("DXF conversion failed.")
    return str(dxf_path)

async def dxf_to_dwg_tool(dxf_path: str, output_dir: str = None) -> str:
    """Convert a .dxf back to .dwg."""
    dxf = Path(dxf_path)
    if not dxf.exists():
        raise FileNotFoundError(f"DXF file not found: {dxf_path}")
        
    if output_dir is None:
        output_dir = str(dxf.parent)
    else:
        os.makedirs(output_dir, exist_ok=True)

    await _run_oda(str(dxf), output_dir, to_dxf=False)
    dwg_name = dxf.stem + ".dwg"
    dwg_path = Path(output_dir) / dwg_name
    
    if not dwg_path.exists():
        raise RuntimeError("DWG conversion failed.")
    return str(dwg_path)

async def list_layers_tool(dxf_path: str) -> list:
    """Return all layer names in a DXF file."""
    doc = ezdxf.readfile(dxf_path)
    return [layer.dxf.name for layer in doc.layers if layer.dxf.name != "0"]

async def add_circle_tool(dxf_path: str, center_x: float, center_y: float,
                          radius: float, layer: str = "0") -> str:
    """Add a circle to a DXF file and save it in-place."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    msp.add_circle(
        center=(center_x, center_y),
        radius=radius,
        dxfattribs={"layer": layer}
    )
    doc.save()
    return f"Circle added at ({center_x},{center_y}), radius {radius} on layer '{layer}'."

async def add_line_tool(dxf_path: str, x1: float, y1: float, x2: float, y2: float,
                        layer: str = "0") -> str:
    """Add a line to a DXF file."""
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    msp.add_line((x1, y1), (x2, y2), dxfattribs={"layer": layer})
    doc.save()
    return f"Line from ({x1},{y1}) to ({x2},{y2}) added."

# -------------------------------------------------------------------
# MCP server boilerplate
# -------------------------------------------------------------------
app = Server("dwg-tools")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="dwg_to_dxf",
            description="Convert a DWG file to DXF format",
            inputSchema={
                "type": "object",
                "properties": {
                    "dwg_path": {"type": "string"},
                    "output_dir": {"type": "string"}
                },
                "required": ["dwg_path"]
            }
        ),
        Tool(
            name="dxf_to_dwg",
            description="Convert a DXF file back to DWG format",
            inputSchema={
                "type": "object",
                "properties": {
                    "dxf_path": {"type": "string"},
                    "output_dir": {"type": "string"}
                },
                "required": ["dxf_path"]
            }
        ),
        Tool(
            name="list_layers",
            description="List all layers in a DXF file",
            inputSchema={
                "type": "object",
                "properties": {"dxf_path": {"type": "string"}},
                "required": ["dxf_path"]
            }
        ),
        Tool(
            name="add_circle",
            description="Add a circle to a DXF file",
            inputSchema={
                "type": "object",
                "properties": {
                    "dxf_path": {"type": "string"},
                    "center_x": {"type": "number"},
                    "center_y": {"type": "number"},
                    "radius": {"type": "number"},
                    "layer": {"type": "string", "default": "0"}
                },
                "required": ["dxf_path", "center_x", "center_y", "radius"]
            }
        ),
        Tool(
            name="add_line",
            description="Add a line to a DXF file",
            inputSchema={
                "type": "object",
                "properties": {
                    "dxf_path": {"type": "string"},
                    "x1": {"type": "number"}, "y1": {"type": "number"},
                    "x2": {"type": "number"}, "y2": {"type": "number"},
                    "layer": {"type": "string", "default": "0"}
                },
                "required": ["dxf_path", "x1", "y1", "x2", "y2"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result_text = ""
    if name == "dwg_to_dxf":
        result_text = await dwg_to_dxf_tool(**arguments)
    elif name == "dxf_to_dwg":
        result_text = await dxf_to_dwg_tool(**arguments)
    elif name == "list_layers":
        layers = await list_layers_tool(**arguments)
        result_text = json.dumps(layers)
    elif name == "add_circle":
        result_text = await add_circle_tool(**arguments)
    elif name == "add_line":
        result_text = await add_line_tool(**arguments)
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