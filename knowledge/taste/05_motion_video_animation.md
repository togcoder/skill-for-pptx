# Domain 5: Video, Motion Graphics & Animation

## 1. Overview & Cultural Authority
Motion in presentation and UI design is not decoration; it is **visual grammar**. It communicates state, relationship, causal hierarchy, and narrative momentum. The discipline draws from Frank Thomas and Ollie Johnston’s *The Illusion of Life: Disney Animation*, modern operating system guidelines (Apple Human Interface Guidelines, Google Material 3 motion tokens), Saul Bass’s kinetic typography, and programmatic animation engines like `reveal.js`, `motion-canvas`, and `Remotion`.

The lab’s hardest lesson (owner feedbacks F2, F8, F14) is that arbitrary motion applied after the fact has no *gu*. Motion must be written as verbs in the story script, with persistent object identities carrying across states.

## 2. Core Principles & Formulas

### 2.1. Disney's 12 Principles Translated to Digital Motion
1. **Squash and Stretch:** Elastic deformation under acceleration or impact ($\le 15\%$ distortion while preserving total 2D volume: $w \times h = \text{const}$).
2. **Anticipation:** A small reverse movement before a major leap (a $3\%-5\%$ dip or pull-back over $100-150\text{ms}$).
3. **Staging:** **Only one focal subject moves per beat.** When the hero element animates, all surrounding elements remain stable or dim to $15\%-30\%$ opacity.
4. **Straight Ahead vs. Pose to Pose:** Presentation morphing is strictly **Pose to Pose**: defining State A (Slide $N$) and State B (Slide $N+1$) with persistent IDs, allowing the engine to interpolate between states.
5. **Follow Through & Overlapping Action:** Sub-elements do not arrive at the exact same instant; child text or secondary badges settle $50-100\text{ms}$ after the parent container.
6. **Slow In and Slow Out (Easing):** Motion must never be linear. Use cubic bezier acceleration and deceleration.
7. **Arcs:** Natural movement follows gentle curves rather than mechanical straight axes.
8. **Secondary Action:** Subtle supportive micro-movements (e.g. icon badge scaling slightly as card expands).
9. **Timing:** Action duration communicates mass and emotional weight.
10. **Exaggeration:** Reserved strictly for error shakes or success confirmations; never on everyday state navigation.
11. **Solid Drawing:** Respecting the visual Z-plane through elevation shadows.
12. **Appeal:** A unified, rhythmic motion language across the entire presentation.

### 2.2. Standard Easing Formulas & Tokens (Material 3 & Apple HIG)
Digital motion requires asymmetric easing:
$$\text{Exit Duration} \approx 0.70 \times \text{Entrance Duration}$$
- **Emphasized Decelerate (Entrance / Arrival):**
  $$\text{cubic-bezier}(0.05, 0.7, 0.1, 1.0)$$
  Fast initial speed that glides smoothly into a confident resting halt.
- **Emphasized Accelerate (Exit / Dismissal):**
  $$\text{cubic-bezier}(0.3, 0.0, 0.8, 0.15)$$
  Elements leave the screen briskly to avoid creating perceived system latency.
- **Spring Physics (Apple HIG):**
  $$F = -k \cdot x - c \cdot v$$
  where $k$ is stiffness and $c$ is damping. Default golden feel:
  $$\text{stiffness} = 100, \quad \text{damping} = 20 \quad (\text{heavy, responsive, zero cartoon bounce})$$

### 2.3. Timing Hierarchy Tiers

| Tier | Duration | Use Case |
|---|---|---|
| **Micro-Feedback** | $100 - 150\text{ms}$ | Button presses, toggle switches, indicator state clicks |
| **State Transitions** | $200 - 300\text{ms}$ | Dropdown reveals, badge appearance, card hover/active lifts |
| **Layout Transformations** | $350 - 500\text{ms}$ | Multi-column grid reordering, sidebar expansion |
| **Focal Scene Morphs** | $600 - 1000\text{ms}$ | Full slide Morph transitions, complex multi-actor choreographies |
| **Ken Burns Hold** | $3000 - 6000\text{ms}$ | Subtle camera push/pan ($1\%-3\%$ scale) on held hero photography |

### 2.4. Saul Bass Kinetic Typography & Pacing
- Words enter from **one single spatial direction** (e.g., rising from below by $20-30\text{px}$ while fading from $0\% \to 100\%$).
- Word-by-word stagger: $60-100\text{ms}$ per word.
- After a major motion sequence or slide cut, give the viewer **$0.6 - 1.0\text{s}$ of visual quiet** before the next action occurs to allow the eye to settle.

### 2.5. Morph / Auto-Animate Object Identity Law (`reveal.js` & PowerPoint)
A Morph transition is an interpolation between two spatial states of the same physical entity:
$$\text{State}_A \xrightarrow{\text{Morph}(\Delta t, \text{easing})} \text{State}_B$$
- **Identity Invariant:** Two shapes morph into each other IF AND ONLY IF their explicit unique identifier matches:
  $$\text{PowerPoint: } \text{Shape Name} = \texttt{!!unique\_id}$$
- **Shape Type Invariant:** Smooth vector interpolation requires identical shape geometry types (e.g., `roundRect` morphing into `roundRect`). Morphing across mismatched shape types (e.g. `ellipse` into `rect`) triggers an abrupt cross-fade.
- **Base State Invariant:** The initial state at $t=0$ on Slide $N$ must NEVER be a completely blank slide. Key anchor elements must be present at $t=0$.

## 3. DOs and DON'Ts

| Aspect | DO | DON'T |
|---|---|---|
| **Purpose** | Motion explains a conceptual shift: *"The isolated card expands into the full architecture overview"* | Motion applied at random: *"Spin this icon because it looks dynamic"* |
| **Focal Eye Trace** | One primary subject moves; the next subject appears where the viewer's eye is already looking | 5 elements flying in simultaneously from 4 different screen corners |
| **Morph Continuity** | Preserve actor names (`!!id`) across slides and maintain logical spatial positions | Discarding shape IDs between slides, forcing PowerPoint to fade everything out and in |
| **Timing Restraint** | Transitions complete in $\le 1.0\text{s}$; micro-feedback in $\le 200\text{ms}$ | Sluggish 2.5-second animations that trap the presenter waiting for text to appear |
| **Entrance Style** | Exponential ease-out from an already grounded layout | Cartoonish elastic bounces, 360-degree rotations, or theatrical fly-ins |

## 4. Translation to PowerPoint (OOXML)
- **Native Morph Transition:** In slide XML (`ppt/slides/slide{N}.xml`):
  ```xml
  <p:transition spd="med" advClick="1">
    <p160:morph option="byObject"/>
  </p:transition>
  ```
- **Actor Pairing:** Both shapes must have identical names prefixed with `!!` in `<p:cNvPr name="!!actor_id"/>`.
- **Morph Duration:** Standard medium speed (`spd="med"`, $1.0\text{s}$) or custom duration in milliseconds.
- **In-Slide Sequence:** When layering effects inside a slide, use sequential click nodes `<p:cTn id="..." nodeType="clickEffect">` with explicit delay tokens (`stCondLst`).
