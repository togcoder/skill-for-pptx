# Domain 5: Motion Design, Video Graphics & Kinetic Choreography

## 1. Overview & Cultural Authority
Kinetic taste (Disney's 12 Principles of Animation, Grant Sanderson's `manim` mathematical engine, Apple iOS Fluid Interfaces, Google Material Design 3 Motion Tokens, and Remotion video composition) separates amateur, distracting slide transitions from professional, fluid visual storytelling.

Amateur presentations make two fatal errors:
1. **The Theme-Park Trap:** Applying chaotic transitions (Checkerboards, Fly-From-Bottom-Right, Blinds, Bounce-Ins) that call attention to the transition rather than the data.
2. **The Teleportation Trap:** Cutting abruptly between slides with no spatial continuity, forcing the audience's visual cortex to re-parse the entire coordinate layout on every click.

---

## 2. GitHub Repositories & Engine References

| Repository / Project | Architecture & Style | Core Invariant Extracted |
|---|---|---|
| [`3b1b/manim`](https://github.com/3b1b/manim) | Mathematical animation engine by Grant Sanderson | Smooth sigmoidal rate functions ($f(t) = \frac{1}{1 + e^{-k(t-0.5)}}$); squish intervals; Bernstein Bézier polynomial transforms. |
| [`remotion-dev/remotion`](https://github.com/remotion-dev/remotion) | React-based programmatic video rendering engine | Frame-based deterministic clock; mass-spring-damper closed-form evaluation; continuous velocity handoffs. |
| [`framer/motion`](https://github.com/framer/motion) | Declarative animation engine for React | Gesture-driven spring physics; shared layout animations (`layoutId`); projected bounding-box delta transforms. |
| [`reveal/reveal.js`](https://github.com/reveal/reveal.js) | HTML presentation framework with Auto-Animate | Morphological shape matching heuristics; view transition API integrations; automatic keyline pairing. |

---

## 3. Mathematical Foundations: Spring Physics vs. Bézier Curves

### 3.1. Mass-Spring-Damper Dynamics (Second-Order ODE)
Natural physical motion is governed by Newton's second law applied to a damped harmonic oscillator:
$$m \frac{d^2 x}{dt^2} + c \frac{dx}{dt} + k x = 0$$
Where:
- $m$ is object mass.
- $k$ is spring stiffness constant.
- $c$ is damping coefficient.

Defining the undamped natural frequency $\omega_n$ and damping ratio $\zeta$:
$$\omega_n = \sqrt{\frac{k}{m}}, \quad \zeta = \frac{c}{2\sqrt{km}}$$

#### A. Underdamped System ($\zeta < 1.0$) — Bouncy Spring
$$x(t) = 1 - e^{-\zeta \omega_n t} \left( \cos(\omega_d t) + \frac{\zeta}{\sqrt{1 - \zeta^2}} \sin(\omega_d t) \right)$$
Where $\omega_d = \omega_n \sqrt{1 - \zeta^2}$ is the damped angular frequency. Used for playful UI buttons, but strictly forbidden on serious executive data presentations.

#### B. Critically Damped System ($\zeta = 1.0$) — The Professional Standard
$$x(t) = 1 - e^{-\omega_n t} (1 + \omega_n t)$$
Settles to the target coordinate in the minimum possible physical time with **exactly zero overshoot**. This represents the gold standard for enterprise executive slide transitions.

#### C. Overdamped System ($\zeta > 1.0$) — Sluggish
$$x(t) = 1 - \frac{1}{2\sqrt{\zeta^2 - 1}} \left( \frac{e^{-s_1 t}}{s_1} - \frac{e^{-s_2 t}}{s_2} \right)$$
Motion feels heavy, dragged, and unresponsive.

---

### 3.2. Asymmetric Temporal Hierarchy
Human cognitive perception processes entrances and exits differently:
$$\begin{aligned}
T_{\text{enter}} &\in [350\text{ ms}, 500\text{ ms}] \quad (\text{Decelerate into view; allow user to register}) \\
T_{\text{exit}} &\approx 0.65 - 0.70 \times T_{\text{enter}} \in [200\text{ ms}, 300\text{ ms}] \quad (\text{Accelerate out rapidly}) \\
T_{\text{morph}} &\in [600\text{ ms}, 900\text{ ms}] \quad (\text{Complex spatial rearrangement})
\end{aligned}$$

---

## 4. PowerPoint OpenXML Morph Architecture & Rules

PowerPoint's **Morph Transition** is the most powerful native vector interpolation engine available in presentation software. However, it fails silently if specific OpenXML invariants are violated.

### 4.1. Morph Headline Rules (Validated in T074 & T086)
1. **Rule M-01 (Shape Primitive Invariant):**
   A shape cannot morph smoothly into a different primitive topology. A `roundRect` morphing into an `ellipse` breaks into a cross-fade dissolution. To morph a rectangle into a circle, author both shapes as `roundRect`, setting `adj="50000"` (with $W=H$) on the circular state.
2. **Rule M-02 (The `!!id` Persistence Invariant):**
   PowerPoint uses `!!<name>` prefixes to match shapes across slides. Shape on Slide 1: `<p:cNvPr id="10" name="!!kpi_card"/>`. Shape on Slide 2: `<p:cNvPr id="25" name="!!kpi_card"/>`. Even if geometry or color changes, PowerPoint links their identities.
3. **Rule M-03 (Text Frame Decoupling):**
   Never place multi-line text directly inside a morphing container. During Morph, PowerPoint stretches the text matrix, causing horrifying visible font distortion. Decouple text into an independent overlay shape placed with a slight stagger entrance.

### 4.2. OpenXML Acceleration / Deceleration Tokens
PowerPoint does not accept CSS `cubic-bezier()` strings. It requires `accel` and `decel` integers ($0 - 100,000$):
$$\text{accel} + \text{decel} \le 100000$$

| Movement Phase | OpenXML Attributes | Behavior |
|---|---|---|
| **Entrance (Ease-Out)** | `accel="10000" decel="80000"` | Rapid departure, gentle 80% glide into place. |
| **Exit (Ease-In)** | `accel="70000" decel="10000"` | Sudden 70% acceleration away from the scene. |
| **Hero Focal Move** | `accel="40000" decel="40000"` | Symmetric ease-in-out for continuous paths. |

---

## 5. OpenXML Transition & Animation Snippets

```xml
<!-- Slide-level Morph Transition in presentation slide XML -->
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main">
  <!-- Content shapes ... -->
  <p:transition spd="med">
    <p14:morph option="byObject"/>
  </p:transition>
</p:sld>
```

```xml
<!-- In-Slide Animation with Critically Damped Ease-Out -->
<p:cTn id="5" dur="400" fill="hold" accel="10000" decel="80000">
  <p:stCondLst>
    <p:cond delay="0"/>
  </p:stCondLst>
  <p:childTnLst>
    <p:set>
      <p:cBhvr>
        <p:cTn id="6" dur="1" fill="hold"/>
        <p:tgtEl><p:spTgt spid="301"/></p:tgtEl>
        <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
      </p:cBhvr>
      <p:to><p:strVal val="visible"/></p:to>
    </p:set>
  </p:childTnLst>
</p:cTn>
```

---

## 6. Comprehensive DOs and DON'Ts

### DO:
1. **Limit motion to 1 primary actor per beat.** If the header, 3 cards, and a background graphic all fly in simultaneously, the audience experiences visual chaos.
2. **Preserve spatial identity across slides using Morph.** If Slide 2 analyzes a component introduced in Slide 1, morph that component into the hero position rather than destroying and recreating it.
3. **Use asymmetric timing.** Entrances must take $400 - 500\text{ ms}$; exits must take $200 - 250\text{ ms}$.
4. **Hold settling drift on hero objects.** When an object lands, allow a $0.5 - 1.0\text{ s}$ motionless pause so the eye registers the information.

### DON'T:
1. **Never use bouncy springs ($\zeta < 0.70$) on financial or executive data.** Bouncing numbers look like a cartoon video game and undermine data credibility.
2. **Never morph between different shape primitives.** Changing from `triangle` to `roundRect` breaks the vector solver into an ugly cross-dissolve.
3. **Never apply rotation during Morph.** Rotating a card while scaling its width triggers rotational axis flipping in PowerPoint's 3D projection matrix.
