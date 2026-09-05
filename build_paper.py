"""Markdown-to-LaTeX conversion and XeLaTeX build (not proof replay)."""
from pathlib import Path
import shutil
import subprocess


def main():
    root = Path(__file__).resolve().parent
    engine = shutil.which('xelatex')
    if not engine:
        local = Path.home()/'Library/TinyTeX/bin/universal-darwin/xelatex'
        engine = str(local) if local.is_file() else 'xelatex'
    text = (root/'PROOF.md').read_text()
    body = text[text.index('## 1. Statement and answer'):]
    run = subprocess.run(['pandoc','--from=markdown+tex_math_single_backslash','--to=latex','--syntax-highlighting=none'], input=body, text=True, check=True, capture_output=True)
    # Uncaptioned tables do not need Pandoc's optional 'none' caption counter.
    body_tex = run.stdout.replace('\\def\\LTcaptype{none} % do not increment counter', '')
    (root/'paper-body.tex').write_text(body_tex)
    for _ in range(2):
        subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error','paper.tex'],cwd=root,check=True)


if __name__ == '__main__':
    main()
