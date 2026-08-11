import os
import sys
import time
import ezdxf

def compile_3dfaces_to_block(input_path):
    """
    Reads a large DXF file, gathers all loose 3DFACE meshes from the ModelSpace,
    moves them into a single centralized block definition, and injects a single 
    block reference back into the drawing.
    """
    # Auto-generate the universal output path within the same directory
    folder, filename = os.path.split(input_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(folder, f"{name}_BLOK{ext}")

    print(f"[*] Step 1: Loading DXF file into memory: {filename}...")
    start_time = time.time()
    
    try:
        doc = ezdxf.readfile(input_path)
    except IOError:
        print(f"[ERROR] Failed to open file. Verify the path or check if it is locked by another process.")
        return False
    except ezdxf.DXFError as e:
        print(f"[ERROR] DXF structural validation failed: {e}")
        return False

    msp = doc.modelspace()
    
    print("[*] Step 2: Querying all loose 3DFACE elements in ModelSpace...")
    all_faces = msp.query('3DFACE')
    face_count = len(all_faces)
    
    print(f"[INFO] Discovered {face_count} independent 3DFACE entities.")
    
    if face_count == 0:
        print("[WARN] No loose 3DFACE elements detected. Geometry might already be structured or optimized.")
        return True

    print("[*] Step 3: Compiling unique block definition structure...")
    # Initialize block definition centered at absolute coordinates (0,0,0)
    compiled_block = doc.blocks.new(name='GENERATOR_MESH', base_point=(0, 0, 0))

    # Memory-safe translation of entity pointers from layout directly into block schema
    for entity in all_faces:
        msp.move_to_layout(entity, compiled_block)

    print("[*] Step 4: Injecting single-instance block reference back to ModelSpace...")
    msp.add_blockref(name='GENERATOR_MESH', insert=(0, 0, 0))

    # Standardize output schema to modern AutoCAD 2018 (AC1032 binary/optimized text mapping)
    doc.acad_release = "R2018"

    print("[*] Step 5: Serializing and saving optimized dataset...")
    try:
        doc.saveas(output_path)
    except IOError as e:
        print(f"[ERROR] Write operations denied for destination path: {e}")
        return False
    
    end_time = time.time()
    print("\n[+] OPTIMIZATION PROCESS COMPLETED SUCCESSFULLY!")
    print(f" |-> Execution Time   : {end_time - start_time:.2f} seconds")
    print(f" |-> Export Location  : {output_path}")
    print(f" |-> Optimized Size   : {os.path.getsize(output_path) / (1024*1024):.2f} MB")
    return True

if __name__ == "__main__":
    # Validate arguments from terminal or tool pipeline calls
    if len(sys.argv) < 2:
        print("[ERROR] Missing target file path parameter.")
        print("Usage: python dxf_block_compiler.py <Absolute_or_Relative_Path_To_DXF>")
        sys.exit(1)
        
    target_file = sys.argv[1]
    if not os.path.exists(target_file):
        print(f"[ERROR] Source file path target does not exist: {target_file}")
        sys.exit(1)
        
    success = compile_3dfaces_to_block(target_file)
    sys.exit(0 if success else 1)
