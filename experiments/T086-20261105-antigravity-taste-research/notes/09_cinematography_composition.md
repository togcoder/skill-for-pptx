# Domain 9: Cinematography, Framing & Spatial Composition

## 1. Overview & Cultural Authority
Cinematographic taste (Roger Deakins' lighting mastery, Walter Murch's *Rule of Six* in film editing, Stanley Kubrick's one-point perspective, and Vittorio Storaro's color philosophy) approaches presentation slides not as static graphic pages, but as **cinematic screen compositions**.

A presenter is a director guiding the audience's visual attention through time and space. When framing is chaotic, subjects collide, or screen direction flips erratically between slides, the audience experiences subconscious disorientation and mental fatigue.

---

## 2. Theoretical Foundations & Cinematic Rules

### 2.1. Walter Murch's Rule of Six (Priorities in Visual Transition)
In *In the Blink of an Eye*, legendary film editor Walter Murch ranked the 6 criteria for evaluating any transition or visual cut:

$$\begin{aligned}
\text{1. Emotion / Narrative Intent} &\approx 51\% \quad (\text{Does the visual reflect the dramatic truth of the data?}) \\
\text{2. Story Progression} &\approx 23\% \quad (\text{Does the slide advance the argument?}) \\
\text{3. Rhythm & Cadence} &\approx 10\% \quad (\text{Does the tempo match the spoken beat?}) \\
\text{4. Eye-Trace (Focal Continuity)} &\approx 7\% \quad (\text{Where was the viewer looking right before the change?}) \\
\text{5. Two-Dimensional Screen Plan} &\approx 5\% \quad (\text{Preserving 180-degree vector direction}) \\
\text{6. Three-Dimensional Action Space} &\approx 4\% \quad (\text{Physical spatial logic})
\end{aligned}$$

*Application to Slides:*
Notice that **Eye-Trace** and **Screen Direction** rank above 3D realism. If an audience member is fixated on a KPI in the top-right corner of Slide 2, the primary focus of Slide 3 must not abruptly jump to the bottom-left corner. Smooth eye-trace minimizes foveal re-acquisition lag.

---

### 2.2. The Rule of Thirds & Power Intersection Points
Divide the $16:9$ canvas into a $3\times 3$ grid using two vertical and two horizontal lines:
$$\begin{aligned}
x_1 &= \frac{1}{3} W \approx 4.444'', \quad x_2 = \frac{2}{3} W \approx 8.888'' \\
y_1 &= \frac{1}{3} H \approx 2.500'', \quad y_2 = \frac{2}{3} H \approx 5.000''
\end{aligned}$$

The 4 intersection points are **Power Focal Points**:
$$P_1 = (x_1, y_1), \quad P_2 = (x_2, y_1), \quad P_3 = (x_1, y_2), \quad P_4 = (x_2, y_2)$$

*Prescription:*
Hero metrics, primary emblems, or focal cards should center on $P_1$ (top-left) or $P_2$ (top-right), rather than dead-centering in the canvas. Dead-centering feels static, formal, and inert; positioning on power intersections creates dynamic visual tension.

---

### 2.3. Asymmetric Visual Mass & The Torque Balance Law
Symmetry is predictable and passive; asymmetry creates energetic engagement. However, asymmetric layouts must remain **visually counterbalanced** across the central axis $x_c = W/2$:

$$\sum_{i} m_i \cdot (x_i - x_c) = 0$$
Where "visual mass" $m_i$ is a function of area, contrast, and color saturation:
$$m_i \approx \text{Area}_i \times \text{Contrast}_i \times \text{ColorWeight}_i$$

*The Lever Principle:*
A small, dense, high-contrast focal badge on the right ($x = 10.5''$, high mass $m = 3$) can perfectly counterbalance a large, airy, muted text block on the left ($x = 3.0''$, lower density $m = 1$).

---

### 2.4. The 180-Degree Line & Screen Direction Continuity
In filmmaking, the 180-degree rule preserves spatial orientation across cuts. If two characters are talking, the camera must stay on one side of the axis of action so Character A always looks right and Character B always looks left.

*Application to Sequential Slides:*
If a system workflow moves from **Left (Input) $\to$ Center (Compute) $\to$ Right (Output)** on Slide 1:
- Slide 2 (Drill-down into Compute) must preserve the input on the left and output on the right.
- Never reverse the direction (e.g. showing Output on the left) on subsequent slides. Reversing screen direction forces the brain to rebuild its mental model of the pipeline.

---

### 2.5. Three Spatial Depth Planes (Foreground, Midground, Background)
A cinematic slide composes elements across 3 distinct spatial layers:
1. **Background Plane ($z = -1$):** Deep canvas void (`#0F172A`), subtle ambient mesh gridlines ($\alpha \le 8\%$).
2. **Midground Plane ($z = 0$):** Primary architectural cards, structural containers, and body text.
3. **Foreground Plane ($z = +1$):** Hero metric badges, active state indicators, and focal tooltips with soft ambient contact shadows.

---

## 3. Python Eye-Trace & Balance Evaluator

```python
"""
Cinematic Visual Balance & Power Point Centering Evaluator
Computes the visual torque balance around the center axis of a 16:9 canvas.
"""
def compute_visual_torque(shapes, canvas_w_in=13.333, canvas_h_in=7.500):
    x_center = canvas_w_in / 2.0
    total_torque = 0.0
    total_mass = 0.0
    
    for s in shapes:
        # Approximate visual mass as Area * ContrastFactor
        area = s["w_in"] * s["h_in"]
        contrast_factor = 2.0 if s.get("is_accent", False) else 1.0
        mass = area * contrast_factor
        
        arm = s["x_in"] + (s["w_in"] / 2.0) - x_center
        torque = mass * arm
        
        total_torque += torque
        total_mass += mass
        
    normalized_balance = total_torque / (total_mass * x_center) if total_mass > 0 else 0.0
    
    # Balance is acceptable if within +/- 15% of zero
    balanced = abs(normalized_balance) <= 0.15
    
    return {
        "normalized_balance": round(normalized_balance, 3),
        "is_balanced": balanced,
        "recommendation": "OK" if balanced else ("SHIFT_WEIGHT_LEFT" if normalized_balance > 0 else "SHIFT_WEIGHT_RIGHT")
    }
```

---

## 4. Comprehensive DOs and DON'Ts

### DO:
1. **Align hero elements with Rule of Thirds power intersections ($x \approx 4.4''$ or $8.9''$).** Avoid dead-center placement on content slides.
2. **Preserve screen direction across sequential slides.** Input on the left, processing in the middle, output on the right.
3. **Guide the viewer's eye-trace deliberately.** Position the hero element on the next slide within $2.0''$ of the preceding slide's exit fixation point.
4. **Counterbalance asymmetric weights.** Pair a compact, high-contrast visual anchor on one side with an airy, readable text measure on the other.

### DON'T:
1. **Never place high-contrast focal elements right on the canvas edge.** Keep all critical content inside the $0.80''$ safe zone.
2. **Never flip visual vectors between slides.** Reversing left-to-right flow causes disorientation.
3. **Never pack all visual weight onto one side leaving the other side completely hollow without purpose.** If the right side is empty, it must serve as intentional negative space balancing a dense left anchor.
