# Domain 1: Keynote & Presentation Design

## 1. Overview & Cultural Authority
Presentation design at the world-class level (Apple Keynotes, Nancy Duarte's studio work, Garr Reynolds' *Presentation Zen*, TED Conference Visual Guidelines, and top-tier Silicon Valley venture decks from Sequoia and Benchmark) treats slides not as illustrated documents or teleprompters, but as **glance media** designed to amplify a spoken narrative.

The fundamental neuro-cognitive insight (Paivio's Dual-Coding Theory and John Sweller's Cognitive Load Theory) proves that the human brain processes visual geometry and auditory verbal language through separate, bandwidth-constrained working memory channels. When a slide contains bulleted text, the audience attempts to read while listening, triggering immediate **cognitive split-attention interference**. Presentation craftsmanship exists to eliminate this friction entirely.

---

## 2. GitHub Repositories & Agent Skill Ecosystem Analysis

To understand modern programmatic slide craftsmanship, we examined authoritative repositories and AI presentation skills:

| Repository / Project | Architecture & Style | Core Algorithmic Invariant Extracted |
|---|---|---|
| [`slidevjs/slidev`](https://github.com/slidevjs/slidev) | Vue 3 + UnoCSS Markdown presentation engine for developers | Component-based modularity, embedded Monaco editor, direct Shiki tokenization, strict layout separation via slide Frontmatter. |
| [`marp-team/marp`](https://github.com/marp-team/marp) | Pure CSS + CommonMark engine with strict theme isolation | Paged CSS media queries, zero-DOM side-effects, automatic paginate counters, strict container scoping. |
| [`rhuss/cc-slidev`](https://github.com/rhuss/cc-slidev) | Cognitive science guardrails for Claude Code slide generation | Hard programmatic bounds: Miller's Law ($\le 6$ elements), word-count ceiling ($< 50$ words), automatic slide splitting over cramming. |
| [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) | Single-file HTML/Tailwind generator with anti-slop rules | "Show, don't tell" visual discovery; rejection of generic purple-on-white gradients; dark-mode contrast balancing. |
| [`robonuggets/marp-slides`](https://github.com/robonuggets/marp-slides) | 22 reference themes for metric and executive decks | Direct SVG/HTML injection for metric cards, sparklines, and progress bars without external raster dependencies. |
| [`SlideSpeak/presentation-design-prompts`](https://github.com/SlideSpeak/presentation-design-prompts) | Structured LLM slide prompt design templates | 60-30-10 color distribution enforcement, typographic pairing matrices, whitespace protection covenants. |

---

## 3. Mathematical Foundations & Cognitive Formulations

### 3.1. The 3-Second Glance Test (Nancy Duarte)
A slide is a billboard on an expressway, not a technical specification sheet.
$$\text{Glance Time} \le 3.0 \text{ s}$$

If a viewer cannot extract:
1. **The subject** (What system or metric are we examining?),
2. **The delta/direction** (Is it increasing, decaying, fractured, or optimized?),
within $3.0\text{ s}$, the layout has failed. Explanatory paragraphs belong exclusively in speaker notes or leave-behind executive memos (`.docx`).

### 3.2. Miller's Law & Visual Chunking Ceiling
George Miller's cognitive capacity law ($7 \pm 2$) applied to visual layout:
$$N_{\text{chunks}} \le 6 \quad (\text{Optimal } N_{\text{chunks}} \in [2, 4])$$

A "chunk" is defined as any distinct visual object demanding foveal fixation: a KPI card, an emblem, a header block, or a diagram node. A slide with 8 separate cards or 12 bullet points causes immediate cognitive freeze.

### 3.3. Text Word-Budget & Density Index
To prevent "slide-doc" degeneration, we compute the slide textual density:
$$W_{\text{count}} = \sum_{p \in \text{Slide}} \text{words}(p) \le 45 \text{ words}$$
$$\rho_{\text{text}} = \frac{W_{\text{count}}}{\text{Canvas Area (in}^2\text{)}} \le 0.50 \text{ words/in}^2$$
For a standard $16:9$ canvas ($13.333'' \times 7.500'' = 100.0\text{ in}^2$), the absolute maximum word budget across the entire canvas is $50$ words. Ideal hero slides feature $8 - 20$ words total.

### 3.4. The 60-30-10 Color Allocation Law
Every slide palette must be distributed according to strict geometric area coverage:
$$\begin{aligned}
A_{\text{base}} &\approx 60\% \quad (\text{Canvas background, ambient void, dark slate or clean paper}) \\
A_{\text{struct}} &\approx 30\% \quad (\text{Cards, structural panels, borders, secondary typography}) \\
A_{\text{accent}} &\approx 10\% \quad (\text{Hero KPI, active state, focal badge, critical delta highlight})
\end{aligned}$$
When accent colors (e.g. vibrant cyan, amber, neon orange) exceed $15\%$ of canvas area, visual hierarchy collapses into visual noise.

### 3.5. Typographic Dominance Ratio
$$\text{Dominance Ratio} = \frac{\text{FontSize}_{\text{hero}}}{\text{FontSize}_{\text{body}}} \ge 2.5$$
- On a $1920\times 1080$ ($16:9$) screen:
  - Hero metric / claim: $72\text{pt} - 96\text{pt}$ (Bold or Heavy)
  - Body context / subtitle: $18\text{pt} - 22\text{pt}$ (Regular or Light)
  - Secondary metadata / footnote: $12\text{pt} - 14\text{pt}$ (Muted opacity)

### 3.6. The Sparkline Narrative Arc (Duarte, *Resonate*)
Presentations that persuade follow an oscillating wave between the current painful reality and the aspirational future state:
```
[Act I]  What Is (Status Quo / Inefficiency / Pain) ──────┐
                                                           ▼
                                                    What Could Be (Vision / Potential) ──┐
                                                                                         ▼
[Act II]                                                                          What Is (The Real-World Obstacle) ──┐
                                                                                                                      ▼
                                                                                                               What Could Be (The Breakthrough)
                                                                                                                      │
                                                                                                                      ▼
[Act III]                                                                                                      New Bliss / Action
```
- **Rule:** Never place the solution on Slide 2. Slide 2 must establish tension ("What Is" / The Friction). Slide 3 elevates to "What Could Be".

---

## 4. Algorithmic Implementation (Python Slide Validator)

```python
"""
Keynote & Presentation Cognitive Load Auditor
Validates word budget, chunk count, and typographic dominance on PPTX slides.
"""
from pptx import Presentation
from pptx.util import Inches

def audit_slide_cognitive_load(slide):
    word_count = 0
    chunk_count = 0
    max_font_size = 0
    min_font_size = 999
    
    for shape in slide.shapes:
        if shape.is_placeholder and shape.placeholder_format.idx == 0:
            pass # Title placeholder
        
        # Count discrete visual chunks
        if shape.has_text_frame or shape.shape_type in (1, 6): # AutoShape or Group
            chunk_count += 1
            
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                words = p.text.strip().split()
                word_count += len(words)
                for r in p.runs:
                    if r.font.size:
                        pt_size = r.font.size.pt
                        max_font_size = max(max_font_size, pt_size)
                        min_font_size = min(min_font_size, pt_size)
                        
    dominance_ratio = (max_font_size / min_font_size) if min_font_size < 999 else 1.0
    
    violations = []
    if word_count > 50:
        violations.append(f"WORD_BUDGET_EXCEEDED: {word_count} words > 50 limit.")
    if chunk_count > 6:
        violations.append(f"MILLERS_LAW_BREACH: {chunk_count} chunks > 6 maximum.")
    if dominance_ratio < 2.2 and word_count > 10:
        violations.append(f"FLAT_HIERARCHY: Dominance ratio {dominance_ratio:.2f} < 2.50 required.")
        
    return {
        "word_count": word_count,
        "chunk_count": chunk_count,
        "dominance_ratio": dominance_ratio,
        "passed": len(violations) == 0,
        "violations": violations
    }
```

---

## 5. Comprehensive DOs and DON'Ts

### DO:
1. **Enforce 1 claim per slide.** If an idea contains an "and" connecting two complex thoughts, split it into two successive slides.
2. **Anchor the eye with an asymmetric hero element.** Use one massive number ($96\text{pt}$), one striking architectural diagram, or one high-contrast phrase.
3. **Use whitespace as a primary structural element.** Empty space is not wasted space; it is the cognitive frame that grants significance to the focal point.
4. **Direct label data curves.** Put the category label directly next to the line endpoint; never force the audience to cross-reference a detached legend box.

### DON'T:
1. **Never use bullet points.** Bulleted lists are speaker outlines masquerading as visual design. Replace with cards, horizontal progression flows, or isolated metric callouts.
2. **Never stamp repetitive branding.** Do not place company logos, confidentiality watermarks, or stock slide borders on every slide. They consume peripheral cognitive bandwidth without conveying information.
3. **Never center-align paragraphs.** Center-aligned multi-line text forces the eye to locate a new starting position on every single line, dramatically slowing reading comprehension.
4. **Never show raw data tables.** Tables belong in documentation. On slides, extract the single critical delta ($+38\%$) and show only the insight.
