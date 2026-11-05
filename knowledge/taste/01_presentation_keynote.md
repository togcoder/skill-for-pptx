# Domain 1: Keynote & Presentation Design

## 1. Overview & Cultural Authority
Presentation design at the world-class level (Apple Keynotes, Nancy Duarte's studio work, TED Conferences, and top Silicon Valley venture decks) treats slides not as illustrated documents or teleprompters, but as **glance media** designed to amplify a spoken narrative.

The fundamental insight of Duarte, Reynolds, and Jobs is that the human brain processes visual input and auditory language through separate cognitive channels (Paivio's Dual-Coding Theory). When a slide contains bulleted paragraphs, the audience attempts to read while listening, creating immediate cognitive split-attention overload.

## 2. Core Principles & Formulas

### 2.1. The 3-Second Glance Test (Nancy Duarte)
A slide is a billboard on a highway, not a magazine article.
- **Formula / Criterion:**
  $$\text{Comprehension Time} \le 3.0 \text{ seconds}$$
  If an audience member cannot perceive:
  1. *What* the subject is,
  2. *The direction* of the claim (positive/negative/comparison),
  within 3 seconds of looking at the slide, the layout fails. Detailed explanatory text belongs exclusively in the speaker notes or an accompanying leave-behind document (`.docx` / memo).

### 2.2. The Sparkline Narrative Arc (Duarte, *Resonate*)
Presentations that persuade follow an oscillating wave between the current painful reality and the aspirational future state:
```
[Beginning] What Is ───────────┐
                               ▼
                        What Could Be ───────┐
                                             ▼
                                      What Is ───────────┐
                                                         ▼
                                                  What Could Be (Climax / "Star" Moment)
                                                         │
                                                         ▼
[Ending]                                          New Bliss / Call to Action
```
- **Rule:** Never jump straight to the solution on Slide 2. Establish tension on Slide 2 ("What Is" / The Friction), elevate to "What Could Be" on Slide 3, test against real-world constraints on Slide 4, and resolve.

### 2.3. The 1-Idea Rule & Typographic Domination (Apple Keynote)
- Exactly **one conceptual claim** per slide view.
- Contrast ratio between primary hero text and secondary context must be extreme:
  $$\frac{\text{Hero Headline Font Size}}{\text{Body Context Font Size}} \ge 2.5$$
  - Example on $1920\times 1080$ ($16:9$ canvas):
    - Hero Metric / Claim: $72\text{pt} - 96\text{pt}$ (Bold / Black weight)
    - Subtitle / Explanation: $20\text{pt} - 24\text{pt}$ (Regular weight, muted tint)

### 2.4. Signal-to-Noise Ratio (Garr Reynolds, *Presentation Zen*)
$$\text{Signal-to-Noise Ratio} = \frac{\text{Meaningful Content}}{\text{Total Visual Elements}}$$
- Eliminate all non-signal elements:
  - No decorative company logos stamped on every single slide footer (the audience already knows who is presenting).
  - No decorative clip art or stock vector humans shaking hands.
  - No decorative lines or gradient ribbons under section headers.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Structure** | State the takeaway in the slide title: *"Enterprise churn dropped 42% after SSO migration"* | Vague topic label: *"Churn Analysis"* or *"Status Update"* |
| **Lists** | Max 3 visual blocks per slide; treat each block as an independent spatial card with clear padding | Bulleted lists with 5–8 bullet points |
| **Typography** | Minimum body text size of $18\text{pt}$ (legible from the back of an auditorium) | $10\text{pt} - 12\text{pt}$ fine print paragraphs |
| **Imagery** | High-resolution hero image or vector asset with intentional crop and spatial breathing room | Tiling 4 tiny low-res screenshots across the slide |
| **Whitespace** | Leave $\ge 40\%$ of the canvas as clean, unpopulated background | Filling every corner with disclaimer boxes, date stamps, and decorative icons |

## 4. Translation to PowerPoint (OOXML)
- **Slide Dimensions:** Fixed $13.333"\times 7.500"$ ($16:9$ widescreen, $12,192,000 \times 6,858,000$ EMUs).
- **Margins:** Exterior padding $\ge 0.8"$ ($731,520$ EMUs) left/right, $\ge 0.6"$ top/bottom.
- **Card Spacing:** Horizontal gap between multi-column cards $\ge 0.4"$ ($365,760$ EMUs).
- **Title Box:** Single text frame for title and subtitle to eliminate cross-box text collisions.
