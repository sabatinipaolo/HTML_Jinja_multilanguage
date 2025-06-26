from pathlib import Path
import shutil
from jinja2 import Environment, FileSystemLoader


INPUT_DIR = Path("src")
OUTPUT_DIR = Path("_site")
ESTENSIONI_PROCESSABILI = {'.html','.jinja', '.jinja2'}


#todo unificare lingue e bandiere in un unico array ( anzi meglio studiare dizionario esterno ...)
LINGUE          = ["it", "en", "fr", "de", "es", "pt" , "ru" , "zh", "jp","ko"]  # Elenco delle lingue supportate
BANDIERE_LINGUE = ["🇮🇹", "🇬🇧", "🇫🇷", "🇩🇪", "🇪🇸", "🇵🇹" , "🇷🇺", "🇨🇭", "🇯🇵"]

BANDIERA = dict(zip(LINGUE, BANDIERE_LINGUE))

NOME_LINGUA= {
    "it" : "Italiano",
    "en" : "English", 
    "fr" : "Français",
    "de" : "Deutsch",
    "es" : "Español",
    "jp" : "日本語"
}

INCLUDE_DIR = "include"  # Define the include directory
##INCLUDE_DIR = INPUT_DIR / "include"  # Define the include directory
LINGUA_DEFAULT = "it"  # Lingua predefinita

def pulisci_cartella_output():
    """Cancella ricorsivamente la cartella output se esiste, poi la ricrea."""
    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)  # Cancella tutto ricorsivamente
        except Exception as e:
            print(f"Errore nella pulizia: {e}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Ricrea la cartella


def is_directly_in_xx(path: Path) -> bool:
    """
    Verifica se il percorso è direttamente dentro src/xx/
    Restituisce True solo per:
    - src/xx/miadir
    - src/xx/
    """
    try:
        parts = path.relative_to(INPUT_DIR).parts
        return len(parts) >= 1 and parts[0] == "xx"
    except ValueError:
        return False
    
def is_processabile(filepath: Path) -> bool:
    return filepath.suffix.lower() in ESTENSIONI_PROCESSABILI 


def main():
    pulisci_cartella_output()

    
    for input_path in sorted(INPUT_DIR.rglob("*")):
        if input_path.is_dir() :
            print(f"{input_path} è una directory , salto")
            continue
        
        if input_path.is_file() and not is_directly_in_xx(input_path):
            print(f"{input_path} non è direttamente in src/xx/")
            print("        copio in _file")
            dst = OUTPUT_DIR / input_path.relative_to(INPUT_DIR)
            # Crea la directory di destinazione se non esiste
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Copia il file
            shutil.copy2(input_path, dst)  # copy2 preserva i metadati
            continue

        ## dovrebbero rimanere solo file in xx/ 
        if input_path.is_file() :
            print(f"processo {input_path}")
            if not is_processabile( input_path): 
                for lingua in LINGUE:
                    dst = OUTPUT_DIR / lingua / input_path.relative_to(INPUT_DIR / "xx")
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(input_path, dst)  
            else:
                for lingua in LINGUE:
                    ##processa con jinja
                    template_dir = input_path.parent
                    env = Environment(loader=FileSystemLoader([INCLUDE_DIR, template_dir])) # Modified line
                    template = env.get_template(input_path.name)  
                    pagePath=str(input_path.relative_to(INPUT_DIR / "xx"))             
                    output = template.render(lingua=lingua,lingue=LINGUE,bandiera=BANDIERA, linguaDefault=LINGUA_DEFAULT,nomeLingua=NOME_LINGUA,pagePath=pagePath)
                    dst = OUTPUT_DIR / lingua / input_path.relative_to(INPUT_DIR / "xx")
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    with open(dst, 'w', encoding='utf-8') as f:
                        f.write(output)

        else:
            print(f"{input_path} che cosa è QUESTO NON DOVEVVA ACCADERE")

    print(f"Generazione completata in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()



