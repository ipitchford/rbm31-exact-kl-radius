# Replay environment

Python 3.10 or newer; verification and constructive queries use only the standard library. Producer replay used Python 3.14 on macOS. Hosted Python 3.11 and 3.13 runs are separately recorded at publication. A hosted rerun is still producer-coordinated, not unaffiliated assurance.

Run `python3 verify.py`, `python3 test_verify.py`, and `python3 test_witness.py`; repeat each with `python3 -O` to show that proof rejection does not rely on removable assert statements. Exact arithmetic is Python integers, Fraction, integer square roots and outward fixed-point logarithm intervals. Decimal tolerances occur only in diagnostic tests.

The manuscript build uses Pandoc and XeLaTeX (TeX Live 2026 in the producer run), Latin Modern fonts, caption/longtable/fancyhdr and a Traditional Chinese font (Noto Serif CJK TC; macOS STHeiti fallback). `python3 build_paper.py` regenerates LaTeX body and PDF. Visual equivalence and scientific text, not cross-platform PDF byte identity, are the portability boundary. Frozen published PDF bytes are checked by the manifest.

Optional discovery dependencies are in requirements-discovery.txt. They are not imported during proof replay or constructive queries. No third-party package is vendored.
