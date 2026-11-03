# Handoff â€” Design Research Lab



Cáº­p nháº­t: 01/11/2026, sau T044. Tá»‡p nĂ y Ä‘Æ°á»£c **viáº¿t láº¡i** má»—i láº§n bĂ n giao,

khĂ´ng ghi ná»‘i thĂªm. Lá»‹ch sá»­: [docs/CHANGELOG.md](docs/CHANGELOG.md). BĂ n giao

trÆ°á»›c: [docs/archive/HANDOFF-T038-2026-11-01.md](docs/archive/HANDOFF-T038-2026-11-01.md).



Repo: https://github.com/togcoder/skill-for-pptx (private). Chá»§ dá»± Ă¡n: togcoder.



## Dá»± Ă¡n bĂ¢y giá» lĂ  gĂ¬



Má»™t **lab nghiĂªn cá»©u thiáº¿t káº¿ Ä‘a lÄ©nh vá»±c (Cross-Domain Agentic AI Lab)**: nhiá»u agent

(nhiá»u model) cĂ¹ng nghiĂªn cá»©u, pháº£n biá»‡n vĂ  xĂ¢u chuá»—i káº¿t quáº£ cho nhiá»u á»©ng dá»¥ng.

Má»—i lÄ©nh vá»±c (domain) cĂ³ luáº­n Ä‘iá»ƒm, nguá»“n, dá»¯ liá»‡u thiáº¿t káº¿ vĂ  thang báº±ng chá»©ng riĂªng;

PowerPoint chá»‰ lĂ  domain lĂ¢u Ä‘á»i nháº¥t.



- CĂ¡ch agent lĂ m viá»‡c: [lab/PROTOCOL.md](lab/PROTOCOL.md).

- CĂ¡c chuáº©n: [lab/standards/](lab/standards/), gá»“m nghiĂªn cá»©u, pháº£n biá»‡n, gá»™p

  dá»¯ liá»‡u vĂ  nÆ¡i Ä‘áº·t file.

- Danh sĂ¡ch domain: [domains/README.md](domains/README.md).

- Quy táº¯c xĂ¢u chuá»—i Ä‘a tĂ i nguyĂªn & tá»± do cá»¥c bá»™: [lab/protocols/04_cross_asset_pipeline.md](lab/protocols/04_cross_asset_pipeline.md).



## Báº¯t Ä‘áº§u



1. Äáº§u nghiĂªn cá»©u má»›i nháº¥t Ä‘Ă£ Ä‘Æ°á»£c gá»™p lĂªn `main`.

2. Äá»c theo thá»© tá»± `AGENTS.md`, `lab/CHARTER.md`, `lab/PROTOCOL.md`, rá»“i tháº»

   domain cá»§a báº¡n (`domains/<domain>/DOMAIN.md`).

3. Cháº¡y `python -m unittest discover -s tests` vĂ 

   `python lab/tools/check_layout.py`. (Äáº£m báº£o táº¥t cáº£ tests pass 100%).

4. Láº¥y mĂ£ káº¿ tiáº¿p trong `research/tasks/INDEX.md` (hiá»‡n lĂ  **T047**). TiĂªu Ä‘á»

   ghi domain trong ngoáº·c, vĂ­ dá»¥ `[pptx]`, `[video]`, `[3d]`, `[cad]`, `[docx]`, `[xlsx]`.



## Tráº¡ng thĂ¡i tá»«ng domain



| Domain | Tráº¡ng thĂ¡i |

|---|---|

| `cross` | Protocols 00â€“04 (Intent Decoder, Capability Gate, Delegation DAG, Red-team Rubric, **Cross-Asset Pre-processing Pipeline & Local Autonomy Charter** - T044). Validator `scripts/cross_pipeline.py`. ToĂ n quyá»n táº£i font/model vĂ  cĂ i Ä‘áº·t thÆ° viá»‡n cá»¥c bá»™ sáº¡ch sáº½. |

| `pptx` | TrÆ°á»Ÿng thĂ nh: Director, Morph Studio, Forge, há»‡ thiáº¿t káº¿ Bento/Asymmetric grids, Critic, vĂ  **Dynamic Theme Engine (T043)**: Area-weighted reference teardown, Composite Background Architecture (Layered translucent PNGs, alpha stats, shape opacity), Need-based semantic synthesizer (5 archetypes), OKLCH 60-30-10, AI Image visual harmonizer. |

| `video` | Ná»n táº£ng (T042): SMPTE RP 2046-2 / EBU R95 safe areas (Action 3.5%, Title 5.0%), 9:16 mobile UI dead zones, ASL shot pacing, J/L-cuts asynchrony, EBU R128 audio mastering (-14 LUFS, ducking -14 dB). Native bridges: `filmcraft_bridge.py` & `soundcraft_bridge.py`. |

| `svg` | Nền tảng (T042): 24x24 icon grid (20x20 live area), optical trim boxes, non-linear stroke scaling $W(S)=W_0(S/S_0)^{0.75}$, Bézier circle handle $\kappa \approx 0.55228$. Native bridge: `vectorcraft_bridge.py`. **T053** semantic reconstruction (16 groups, 101 paths) merged; **T054** comparison-first match: 0.806 W/H vs photo 0.800, six landmark deltas 0.000–0.001, 16 groups / 117 paths / 6 texts, front split 0.40, VectorCraft 0 warnings; `work/T054-opencode-vector-match`; **review requested**. Chưa có perspective camera, print/Illustrator/Inkscape, human rung 6. |

| `3d` | Ná»n táº£ng (T042): Metric scale (mm, Y-up glTF), No-Sharp-Edge Law (micro-bevel $0.2-0.5	ext{ mm}$), concentric fillets, True Isometric camera ($35.264^\circ$ elev), 3-point studio lighting, PBR albedo clamp. Native bridge: `solidcraft_bridge.py`. |

| `cad` | Ná»n táº£ng (T042): ISO 5457 sheet dimensions (A4â€“A0, 20mm left margin), ISO 128 line weight hierarchy (0.50mm group: 0.50, 0.25, 0.18mm), ISO 129 dimensioning geometry (10mm/7mm offsets, 3:1 arrowheads), ISO 7200 title block (180mm). Native bridge: `cadcraft_bridge.py`. |

| `docx` | T039/T045/T047 on `main`; **T052** configurable standard profiles (HUST 2017, VNU-UET, ISO 7144, annual/GRI) + Vietnamese scientific report: `hust-datn-2017` 34 body pages/48 total, `vnu-uet-kl-2024` 35 body/45 total, conformance 23/23 and 24/24, Word PDFs inspected; Argon **approve T052** (round 2), đã merge `main` (`306f5f2`). Chưa có PDF/UA, PDF/A, LibreOffice rung 3, human rung 6. |

| `xlsx` | T041/T046/T048 on `main`; **T050** VBA UserForm (22 controls, `frmEntry` + `FormTools`) + 12-column dashboard (4 native charts, 4 KPI, 3 buttons, 1-page A4), macro execution blocked by host policy `work/T050-opencode-userform-dashboard`, audit clean; Argon **approve T050** (round 2), đã merge `main` (`90695a9`). Waterfall/treemap/histogram/box/funnel vẫn là recipe OOXML. |



## Viá»‡c tiáº¿p theo (xáº¿p háº¡ng)



1. **Pháº£n biá»‡n chĂ©o (Peer Review)**, theo `lab/standards/REVIEW.md`, do agent khĂ¡c tĂ¡c giáº£ viáº¿t:

   - T044 (Cross-Asset Pipeline & Local Autonomy, review requested);

   - T043 (Dynamic Theme Engine & Teardown, review requested);

   - T042 (Multi-domain canons & bridges, review requested);

   - T039 & T041 (docx / xlsx round 2);

   - T038 (pptx canon);

   - T035 (DeckCraft);

   - T036â€“T037 (cross protocols vĂ  multi-craft bridges).

2. **Äá»“ng bá»™ hĂ³a vá»›i OpenCode:**

   - Sá»­ dá»¥ng `scripts/cross_pipeline.py` Ä‘á»ƒ tiá»n xá»­ lĂ½ biá»ƒu Ä‘á»“ (`validate_chart_data_for_presentation`) vĂ  áº£nh (`validate_image_for_embedding`) trÆ°á»›c khi chĂ¨n chĂ©o vĂ o Word vĂ  Excel.

3. **TĂ­ch há»£p Theme Engine vĂ o Slide Forge (`slide_forge.py`):**

   - Há»— trá»£ cá» `--ref-deck <file.pptx>` Ä‘á»ƒ tá»± Ä‘á»™ng clone theme tá»« file máº«u báº¥t ká»³.

   - Há»— trá»£ cá» `--need "<chuá»—i mĂ´ táº£>"` Ä‘á»ƒ tá»± Ä‘á»™ng tá»•ng há»£p theme Ä‘á»™c báº£n theo nhu cáº§u.



## Prompt giao viá»‡c



```text

Join the design research lab at https://github.com/togcoder/skill-for-pptx, branch

main. Read AGENTS.md, lab/CHARTER.md, lab/PROTOCOL.md and

domains/<your domain>/DOMAIN.md. Run the tests and lab/tools/check_layout.py.

Take the next free ID in research/tasks/INDEX.md with the domain in brackets and

push the claim. Frame your question from the domain's native canon before

building. Follow lab/protocols/04_cross_asset_pipeline.md to pre-process assets

before embedding. Put every output into experiments/<ID>-<date>-<agent>-<slug>/ (never the

repo root). Tag claims with evidence rungs. Ask another agent to review per

lab/standards/REVIEW.md before anything enters a product path.

```

