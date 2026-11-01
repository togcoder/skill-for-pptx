#!/usr/bin/env python3
"""LaTeX subset → OMML for native Word equations (T042, docx).

Status: EXPERIMENTAL — T042 [docx], review requested.  Not canonical until an
independent review accepts it.

The parser covers the formulas a report actually uses: fractions, powers,
subscripts, roots, sums/integrals, parentheses, accents, Greek letters and the
common operators.  It is deliberately strict: an unsupported command raises
``ValueError`` so the caller can tell the user exactly what to rewrite, rather
than silently emitting a broken equation.

OMML reference: ISO/IEC 29500-1:2016 §22.1 (Office Math).
"""
from __future__ import annotations

import re
from lxml import etree

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def m(tag: str) -> str:
    return f"{{{M_NS}}}{tag}"


def _el(tag: str):
    return etree.Element(m(tag))


def _run(text: str, *, normal: bool = False):
    r = _el("r")
    if normal:
        rpr = etree.SubElement(r, m("rPr"))
        sty = etree.SubElement(rpr, m("sty"))
        sty.set(m("val"), "p")
    t = etree.SubElement(r, m("t"))
    t.text = text
    return r


def _container(tag: str, nodes):
    node = _el(tag)
    for child in nodes:
        node.append(child)
    return node


def _base(nodes):
    if len(nodes) == 1:
        return nodes[0]
    return _container("e", nodes)


GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ",
    "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π", "Sigma": "Σ", "Phi": "Φ",
    "Psi": "Ψ", "Omega": "Ω",
}

SYMBOLS = {
    "cdot": "·", "times": "×", "div": "÷", "pm": "±", "mp": "∓",
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "neq": "≠",
    "approx": "≈", "equiv": "≡", "sim": "∼", "propto": "∝",
    "infty": "∞", "partial": "∂", "nabla": "∇", "forall": "∀",
    "exists": "∃", "in": "∈", "notin": "∉", "subset": "⊂",
    "supset": "⊃", "cup": "∪", "cap": "∩", "to": "→", "rightarrow": "→",
    "leftarrow": "←", "Rightarrow": "⇒", "Leftarrow": "⇐",
    "leftrightarrow": "↔", "degree": "°", "prime": "′", "ldots": "…", "cdots": "⋯",
}

SPACES = {",": "\u2009", ";": "\u2005", ":": "\u2004", "quad": "\u2003",
          "qquad": "\u2003\u2003", "!": ""}

NARY = {"sum": "∑", "prod": "∏", "int": "∫", "oint": "∮"}

ACCENTS = {"bar": "̄", "hat": "̂", "vec": "⃗", "dot": "̇", "ddot": "̈"}


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0

    def error(self, message: str):
        raise ValueError(f"{message} at position {self.i}: {self.text!r}")

    def skip(self):
        while self.i < len(self.text) and self.text[self.i].isspace():
            self.i += 1

    def group(self) -> str:
        self.skip()
        if self.i >= len(self.text) or self.text[self.i] != "{":
            self.error("expected '{'")
        depth = 0
        start = self.i + 1
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    content = self.text[start:self.i]
                    self.i += 1
                    return content
            self.i += 1
        self.error("unbalanced braces")

    def command(self) -> str:
        self.i += 1
        start = self.i
        while self.i < len(self.text) and self.text[self.i].isalpha():
            self.i += 1
        if start == self.i:
            # escaped punctuation: \{, \}, \%, \_
            if self.i < len(self.text):
                ch = self.text[self.i]
                self.i += 1
                return ch
            self.error("dangling backslash")
        return self.text[start:self.i]

    def argument(self):
        self.skip()
        if self.i < len(self.text) and self.text[self.i] == "{":
            content = self.group()
            return _Parser(content).parse()
        return [self.term()]

    def term(self):
        base = self.atom()
        while True:
            self.skip()
            if self.i < len(self.text) and self.text[self.i] in "_^":
                kind = self.text[self.i]
                self.i += 1
                arg = self.argument()
                base = self.script(base, kind, arg)
            else:
                break
        return base

    def script(self, base, kind: str, arg):
        tag = "sSup" if kind == "^" else "sSub"
        node = _el(tag)
        node.append(_container("e", [base] if not isinstance(base, list) else base))
        node.append(_container("sup" if kind == "^" else "sub", arg))
        return node

    def atom(self):
        self.skip()
        if self.i >= len(self.text):
            self.error("unexpected end")
        ch = self.text[self.i]
        if ch == "\\":
            cmd = self.command()
            if len(cmd) == 1:
                # Escaped punctuation and the LaTeX control space (\%, \&,
                # \_, \{, \}, backslash-space) are literal runs.
                return _run(cmd)
            if cmd in GREEK:
                return _run(GREEK[cmd])
            if cmd in SYMBOLS:
                return _run(SYMBOLS[cmd])
            if cmd in SPACES:
                return _run(SPACES[cmd])
            if cmd == "frac":
                num = self.argument()
                den = self.argument()
                f = _el("f")
                f.append(_container("num", num))
                f.append(_container("den", den))
                return f
            if cmd == "sqrt":
                degree = None
                self.skip()
                if self.i < len(self.text) and self.text[self.i] == "[":
                    end = self.text.find("]", self.i)
                    if end == -1:
                        self.error("unbalanced root degree")
                    degree = _Parser(self.text[self.i + 1:end]).parse()
                    self.i = end + 1
                body = self.argument()
                rad = _el("rad")
                rpr = etree.SubElement(rad, m("radPr"))
                if degree is None:
                    hide = etree.SubElement(rpr, m("degHide"))
                    hide.set(m("val"), "1")
                    rad.append(_el("deg"))
                else:
                    rad.append(_container("deg", degree))
                rad.append(_container("e", body))
                return rad
            if cmd in NARY:
                sub = None
                sup = None
                # consume optional scripts before the body
                while True:
                    self.skip()
                    if self.i < len(self.text) and self.text[self.i] in "_^":
                        kind = self.text[self.i]
                        self.i += 1
                        arg = self.argument()
                        if kind == "_":
                            sub = arg
                        else:
                            sup = arg
                    else:
                        break
                self.skip()
                body = []
                if self.i < len(self.text) and self.text[self.i] not in "}+-=,;":
                    body = [self.term()]
                nary = _el("nary")
                npr = etree.SubElement(nary, m("naryPr"))
                chr_el = etree.SubElement(npr, m("chr"))
                chr_el.set(m("val"), NARY[cmd])
                lim = etree.SubElement(npr, m("limLoc"))
                lim.set(m("val"), "undOvr" if cmd in {"sum", "prod"} else "subSup")
                nary.append(_container("sub", sub or []))
                nary.append(_container("sup", sup or []))
                nary.append(_container("e", body))
                return nary
            if cmd in ACCENTS:
                body = self.argument()
                acc = _el("acc")
                apr = etree.SubElement(acc, m("accPr"))
                chr_el = etree.SubElement(apr, m("chr"))
                chr_el.set(m("val"), ACCENTS[cmd])
                acc.append(_container("e", body))
                return acc
            if cmd in {"text", "mathrm", "operatorname"}:
                content = self.group()
                return _run(content, normal=True)
            if cmd == "left":
                self.skip()
                begin = self.text[self.i] if self.i < len(self.text) else "("
                self.i += 1
                body = self.parse(stop_right=True)
                self.skip()
                if not self.text.startswith("\\right", self.i):
                    self.error("expected \\right")
                self.i += len("\\right")
                self.skip()
                end = self.text[self.i] if self.i < len(self.text) else ")"
                self.i += 1
                d = _el("d")
                dpr = etree.SubElement(d, m("dPr"))
                beg = etree.SubElement(dpr, m("begChr")); beg.set(m("val"), begin)
                en = etree.SubElement(dpr, m("endChr")); en.set(m("val"), end)
                d.append(_container("e", body))
                return d
            if cmd == "right":
                self.error("unexpected \\right")
            if cmd in {"begin", "end"}:
                self.error(f"LaTeX environment \\{cmd} is not supported")
            self.error(f"unsupported LaTeX command \\{cmd}")
        if ch == "{":
            content = self.group()
            return _Parser(content).atom() if len(content.strip()) == 1 else _container("e", _Parser(content).parse())
        if ch.isdigit() or (ch == "." and self.i + 1 < len(self.text) and self.text[self.i + 1].isdigit()):
            start = self.i
            while self.i < len(self.text) and (self.text[self.i].isdigit() or self.text[self.i] == "."):
                self.i += 1
            return _run(self.text[start:self.i])
        # a run of letters/digits up to a script/space/operator; one letter is
        # the safe base for x^2, but a multi-letter word stays one run.
        start = self.i
        while self.i < len(self.text) and self.text[self.i].isalpha() and self.text[self.i] not in "_^{}":
            self.i += 1
        if start == self.i:
            self.i += 1
            return _run(ch)
        return _run(self.text[start:self.i])

    def parse(self, *, stop_right: bool = False):
        nodes = []
        while self.i < len(self.text):
            self.skip()
            if self.i >= len(self.text):
                break
            if stop_right and self.text.startswith("\\right", self.i):
                break
            if self.text[self.i] == "}":
                break
            nodes.append(self.term())
        return nodes


def omml_from_latex(latex: str):
    """Return an ``m:oMath`` element for a supported LaTeX subset."""
    if not latex or not latex.strip():
        raise ValueError("empty LaTeX")
    root = _el("oMath")
    for node in _Parser(latex).parse():
        root.append(node)
    return root


def omml_para(latex: str):
    """Return an ``m:oMathPara`` wrapper for a display equation."""
    para = _el("oMathPara")
    para.append(omml_from_latex(latex))
    return para
