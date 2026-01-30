#!/bin/bash

# LaTeX Compilation Script for Investment Memo
# Requires: pdflatex with packages (texlive-full recommended)

echo "======================================================================"
echo "COMPILING INVESTMENT MEMO FROM LATEX"
echo "======================================================================"
echo ""

# Check if pdflatex is installed
if ! command -v pdflatex &> /dev/null; then
    echo "❌ pdflatex not found!"
    echo ""
    echo "To install LaTeX on Ubuntu/Debian:"
    echo "  sudo apt-get install texlive-latex-base texlive-latex-extra"
    echo "  sudo apt-get install texlive-fonts-recommended texlive-fonts-extra"
    echo "  sudo apt-get install texlive-pictures"
    echo ""
    echo "Or install full distribution:"
    echo "  sudo apt-get install texlive-full"
    echo ""
    echo "======================================================================"
    echo "ALTERNATIVE: Use Overleaf"
    echo "======================================================================"
    echo ""
    echo "1. Go to https://www.overleaf.com"
    echo "2. Create free account"
    echo "3. Upload investment_memo.tex"
    echo "4. Click 'Recompile' to generate PDF"
    echo ""
    exit 1
fi

echo "✓ pdflatex found"
echo ""

# Compile LaTeX document (run twice for proper references)
echo "Compiling LaTeX document..."
echo "  (Running pdflatex first pass...)"
pdflatex -interaction=nonstopmode investment_memo.tex > /dev/null 2>&1

echo "  (Running pdflatex second pass...)"
pdflatex -interaction=nonstopmode investment_memo.tex > /dev/null 2>&1

# Check if PDF was generated
if [ -f "investment_memo.pdf" ]; then
    echo ""
    echo "======================================================================"
    echo "✅ PDF GENERATED SUCCESSFULLY"
    echo "======================================================================"
    echo ""
    ls -lh investment_memo.pdf
    echo ""
    echo "Output: latex/investment_memo.pdf"
    echo ""

    # Move to output folder
    mv investment_memo.pdf ../output/investment_memo_latex.pdf
    echo "Moved to: output/investment_memo_latex.pdf"
    echo ""

    # Clean up auxiliary files
    rm -f *.aux *.log *.out *.toc
    echo "✓ Cleaned up auxiliary files"
    echo ""
    echo "======================================================================"
else
    echo ""
    echo "❌ PDF generation failed!"
    echo ""
    echo "Check the log file for errors:"
    echo "  cat investment_memo.log"
    echo ""
    echo "Common issues:"
    echo "  • Missing LaTeX packages (install texlive-full)"
    echo "  • Missing fonts (install texlive-fonts-extra)"
    echo "  • Missing fontawesome (install texlive-fonts-extra)"
    echo ""
    exit 1
fi

echo "======================================================================"
echo "DONE"
echo "======================================================================"
