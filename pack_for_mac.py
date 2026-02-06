import zipfile
import os

def zip_project(output_filename):
    # Files to include
    extensions = ['.py', '.json', '.pdf', '.txt', '.md']
    exclude_files = ['Acta_Generada_Web.pdf', 'Acta_Rellenada.pdf', 'debug_overlay.pdf'] # Exclude generated output
    exclude_dirs = ['.git', '__pycache__', '.streamlit']
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Loop through files in current directory
        for root, dirs, files in os.walk('.'):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions) and file not in exclude_files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, '.')
                    print(f"Adding {arcname}")
                    zipf.write(file_path, arcname)

if __name__ == "__main__":
    zip_project("agente_actas_mac.zip")
    print("Project compressed to agente_actas_mac.zip")
