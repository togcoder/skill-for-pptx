# T067 — beat sheet for *Triết học Mác – Lênin, Chương 1*

- **Deck:** `motion/artifacts/T066-deck-directed.pptx` (directed copy of T066).
- **Date:** 2026-11-04. **Base:** `7d3d9b8`.
- **Purpose:** the spoken line, the visual beat and the click are one unit.
  Nothing on screen moves unless the sentence needs it.
- **Evidence:** the shape-level state of every beat is in
  `motion-plan.json`; the before/after frames are in `motion/before/`,
  `motion/after/` and `motion/evidence-sheet.png`.

## 0. The motion grammar

| Rule | Choice | Why |
|---|---|---|
| Base plate | title + kicker + key image + margin rule are **visible at t=0**; no entrance on them | the audience must be able to read the claim before the first click |
| Reading order | top → bottom, left → right; a label appears only after its carrier | the eye should never have to search for what the voice just named |
| Verbs | text = `fade`; panels = `wipe-up`; rules/lines = `wipe-left`; one `zoom`/`float-in` for a hero | one motion language, no effect salad |
| Tempo | 150–350 ms for a detail, 350–500 ms for a hero, 600 ms for the timeline | 27 beats, not 51; each beat is a sentence |
| Movers | **≤ 2** animated targets at any instant | the owner's rule; a card and its label are one object |
| Click | one click = one stable idea; no click whose only job is a decoration | `motion-audit.md` §2.5 lists the removed clicks |
| Morph | **0 of 9 kept**; 350 ms Fade between slides | no adjacent pair has an object or idea that survives the cut |
| Images | key portraits/objects at t=0; labels build | the face is the evidence, not the finale |
| Payoff | the last click is the synthesis, not a detail | conclusions last |

The **four roles** used below:

- **anchor** — already on the base plate; the thing the sentence is about;
- **evidence** — the detail the click adds to prove the sentence;
- **turn** — the one move that changes the meaning of the frame;
- **payoff** — the line/mark that lands after the turn.

## 1. Cover — “Ba chân dung, một dòng”

**Base at t=0:** `bg`, `panel`, `kicker` “CHƯƠNG 1 · KHÁI LUẬN”, `title`
“TRIẾT HỌC MÁC – LÊNIN”, `subtitle` “Từ thế giới quan đến phương pháp luận”,
`caption`, the three portraits, the gold rule under the title, the margin rule
and dot. The cover is fully readable before any click; the gold rings are the
only thing that has not arrived yet.

**Beat A — auto, 1.5 s, 0 presenter clicks**

- **Spoken:** “Chương 1 mở bằng ba chân dung, không phải ba biểu tượng: ba mốc
  của một dòng lý luận gắn với thực tiễn.”
- **Visual:** the three gold rings draw around the already-visible portraits,
  one after another. Nothing is hidden; the rings are a frame, not a reveal.
- **Roles:** anchor = title + three portraits; evidence = subtitle + caption;
  turn = the ring draw; payoff = the cover as a whole.
- **State:** visible at entry; rings finish at 1.5 s.
- **Hero:** the three rings are one slow gesture — the only movement on the
  cover. The faces are already there, so the gesture cannot upstage them.

**Reading order:** title → subtitle → three faces → rings. The next click is
the slide advance.

## 2. Triết học là gì? — definition and three functions

**Base at t=0:** `bg`, `kicker` “CÂU HỎI MỞ”, `title` “Triết học là gì?”,
Plato and its red disc, the caption, the margin rule. The question and the
image are readable; the definitions and labels wait.

**Beat 1 — click, 350 ms**

- **Spoken:** “Triết học không phải một định nghĩa để học thuộc: nó là hệ thống
  tri thức lý luận chung nhất về thế giới và vị trí con người trong đó.”
- **Visual:** `def1` fades in under the question.
- **Roles:** anchor = title + Plato; evidence = `def1`; turn = —; payoff = —.
- **State:** on click 1; stable after 350 ms.
- **Hero:** none — this is a line of text, and it should read as a line.

**Beat 2 — click, 350 ms**

- **Spoken:** “Định nghĩa thứ hai hẹp hơn: khoa học về những quy luật chung nhất
  của tự nhiên, xã hội và tư duy.”
- **Visual:** `def2` fades in below the first.
- **Roles:** anchor = title + Plato; evidence = `def2`; turn = —; payoff = —.
- **State:** on click 2.
- **Hero:** none.

**Beat 3 — click, 753 ms**

- **Spoken:** “Ba việc triết học làm: cho ta một thế giới quan, một phương pháp
  luận, và một logic để không tự lừa mình.”
- **Visual:** `l0-rule`, `l1-rule`, `l2-rule` draw left-to-right in sequence;
  each label appears immediately after its rule. One mover at a time.
- **Roles:** anchor = title + Plato; evidence = the three rules; turn = the
  third rule; payoff = “LOGIC BIỆN CHỨNG”.
- **State:** on click 3; three micro-beats of 250 ms.
- **Hero:** the three underlines are one “01–02–03” gesture, not a group fade.

**Reading order:** question → definition 1 → definition 2 → three functions.
Plato is present from the first frame, so the image never arrives as a prize.

## 3. Vật chất hay ý thức? — the basic question

**Base at t=0:** `bg`, `kicker` “VẤN ĐỀ CƠ BẢN”, `title` “VẬT CHẤT HAY Ý
THỨC?”, the margin rule. The question is the whole plate; the two answers and
the question mark wait.

**Beat 1 — click, 551 ms**

- **Spoken:** “Mặt thứ nhất là bản thể luận: vật chất có trước, quyết định ý
  thức.”
- **Visual:** the left card `left` wipes up; `left-title` fades; `left-body`
  and `left-foot` appear as the panel lands. The card is one object.
- **Roles:** anchor = title; evidence = left card; turn = —; payoff =
  “BẢN THỂ LUẬN”.
- **State:** on click 1; 2 movers at most, sequentially.
- **Hero:** the left card is laid down like a page; it is the thesis.

**Beat 2 — click, 551 ms**

- **Spoken:** “Mặt thứ hai là nhận thức luận: ý thức có sau, phản ánh vật
  chất.”
- **Visual:** the right card wipes down, mirroring the left.
- **Roles:** anchor = title; evidence = right card; turn = —; payoff =
  “NHẬN THỨC LUẬN”.
- **State:** on click 2.
- **Hero:** the same gesture, mirrored. No new effect language.

**Beat 3 — click, 850 ms**

- **Spoken:** “Câu hỏi còn lại nằm giữa hai câu trả lời: cái nào có trước?”
- **Visual:** the gold `?` zooms into the gap, the short rule draws, the caption
  fades. The question mark is the turn.
- **Roles:** anchor = title; evidence = both cards; turn = `qmark`; payoff =
  “CÁI NÀO TRƯỚC?”.
- **State:** on click 3; 350 + 250 + 250 ms.
- **Hero:** the question mark lands **after** both answers; it is the point of
  the slide, not a decoration between two empty cards.

**Reading order:** question → thesis → antithesis → the question again.

## 4. Biện chứng hay siêu hình? — two ways of seeing

**Base at t=0:** `bg`, `kicker` “HAI CÁCH NHÌN”, `title`, the full dialectical
diagram (`dialectic-circle`, `dialectic-core`, `dialectic-arrow`), the margin
rule. The title and the first diagram are readable; the right-hand contrast and
the two explanatory cards wait.

**Beat 1 — click, 551 ms**

- **Spoken:** “Biện chứng nhìn sự vật trong liên hệ, vận động, mâu thuẫn — vòng
  tròn đã ở đó, nhưng ý nghĩa chưa được gọi tên.”
- **Visual:** `dialectic-card` wipes up under the circle; `dialectic-name`
  fades; `dialectic-desc` appears.
- **Roles:** anchor = title + circle/core/arrow; evidence = the card; turn = —;
  payoff = the description.
- **State:** on click 1; 2 movers, sequential.
- **Hero:** the card is the only thing that moves; the circle stands still as
  the point of reference.

**Beat 2 — click, 751 ms**

- **Spoken:** “Siêu hình nhìn sự vật tách rời, tĩnh tại, phiến diện — một đường
  thẳng có ba điểm dừng.”
- **Visual:** `straight-line` draws left-to-right; the three dots appear at its
  end; `straight-label` fades.
- **Roles:** anchor = title + left diagram; evidence = the line and dots;
  turn = the line; payoff = “TÁCH RỜI / BẤT BIẾN”.
- **State:** on click 2; 450 + 300 ms.
- **Hero:** the straight line is the contrast: it moves, but it never turns
  back; it stops at three fixed points.

**Beat 3 — click, 551 ms**

- **Spoken:** “Cùng một sự vật, hai cách nhìn; chọn cách nào là chọn cái gì
  được thấy.”
- **Visual:** `meta-card` wipes up; name and description follow.
- **Roles:** anchor = title; evidence = meta card; turn = —; payoff = the
  description.
- **State:** on click 3.
- **Hero:** none — the two sides are now balanced; the last card only closes
  the frame.

**Reading order:** question → dialectic diagram → dialectic definition →
metaphysical line → metaphysical definition. The base is intentionally
left-heavy: the empty right half is the question the title asks.

## 5. Điều kiện ra đời — three conditions, one date

**Base at t=0:** `bg`, `kicker` “BỐI CẢNH”, `title` “ĐIỀU KIỆN RA ĐỜI”, `sub`
“Những năm 1840 · Tây Âu”, the margin rule. The claim and the period are
readable; the three cards and the timeline wait.

**Beat 1 — click, 551 ms**

- **Spoken:** “Điều kiện kinh tế – xã hội: chủ nghĩa tư bản phát triển mạnh,
  giai cấp vô sản xuất hiện.”
- **Visual:** `card0` wipes up; heading fades; number and body appear.
- **Roles:** anchor = title + sub; evidence = card 01; turn = —; payoff = —.
- **State:** on click 1; 2 movers, sequential.
- **Hero:** the first card is laid down alone; it establishes the column.

**Beat 2 — click, 551 ms**

- **Spoken:** “Điều kiện khoa học tự nhiên: tế bào, bảo toàn năng lượng, tiến
  hóa — ba phát hiện đổi cách nhìn thế giới.”
- **Visual:** `card1` wipes up, same rhythm.
- **Roles:** anchor = title + sub; evidence = card 02; turn = —; payoff = —.
- **State:** on click 2.
- **Hero:** none; the repetition is the point (three conditions, one grammar).

**Beat 3 — click, 551 ms**

- **Spoken:** “Điều kiện tư tưởng: Hegel, Feuerbach và chủ nghĩa xã hội không
  tưởng — một dòng để phê phán và kế thừa.”
- **Visual:** `card2` wipes up; the row is complete.
- **Roles:** anchor = title + sub; evidence = card 03; turn = —; payoff = —.
- **State:** on click 3.
- **Hero:** none; the third card closes the row.

**Beat 4 — click, 1000 ms**

- **Spoken:** “Ba điều kiện gặp nhau ở một mốc: 1848, Tuyên ngôn Đảng Cộng
  sản.”
- **Visual:** the timeline draws left-to-right; the dot zooms; the 1848 label
  fades.
- **Roles:** anchor = the three cards; evidence = the timeline; turn = the
  line; payoff = “1848 · Tuyên ngôn Đảng Cộng sản”.
- **State:** on click 4; 500 + 250 + 250 ms.
- **Hero:** the timeline is the synthesis: three conditions become one
  historical date.

**Reading order:** claim → condition 01 → 02 → 03 → the date they meet.

## 6. Ba bộ phận — one whole, three parts

**Base at t=0:** `bg`, `kicker` “CẤU TRÚC”, `title` “BA BỘ PHẬN”, `sub`
“Cấu thành triết học Mác – Lênin”, the margin rule. The claim is readable; the
three cards, the two connectors and the closing note wait.

**Beat 1 — click, 1653 ms**

- **Spoken:** “Ba bộ phận không phải ba môn học rời: triết học cho phương pháp,
  kinh tế chính trị chỉ ra quan hệ sản xuất, chủ nghĩa xã hội khoa học nói về
  con đường.”
- **Visual:** `part0`, `part1`, `part2` wipe up in a wave, left to right; each
  card's heading and text finish before the next card starts. One mover at a
  time.
- **Roles:** anchor = title + sub; evidence = the three cards; turn = the
  wave; payoff = the complete row.
- **State:** on click 1; 3 × 551 ms, sequential.
- **Hero:** the wave is the argument: three parts, one movement, one whole.
  This is why there is only one click, not three.

**Beat 2 — click, 550 ms**

- **Spoken:** “Ba bộ phận nối với nhau, và cả hệ thống là một chỉnh thể: triết
  học là nền tảng phương pháp; kinh tế chính trị là giải phẫu xã hội; CNXH
  khoa học là mục tiêu và con đường.”
- **Visual:** `arrow1` and `arrow2` fade together between the cards; `note`
  fades below.
- **Roles:** anchor = the three cards; evidence = the two connectors; turn =
  the connectors; payoff = the note.
- **State:** on click 2; 2 movers + 1 sequential.
- **Hero:** the two connectors turn three cards into a system; the note states
  the system in words.

**Reading order:** claim → three cards as a wave → connectors → the note.

## 7. Một dòng chảy — three people, one project

**Base at t=0:** `bg`, `kicker` “BA MỐC”, `title` “MỘT DÒNG CHẢY”, `sub` “Từ
lý luận đến cách mạng”, the three portraits and rings, the margin rule. The
faces are visible; the names, dates and timeline wait.

**Beat 1 — click, 251 ms**

- **Spoken:** “C. Mác, 1818–1883: Tư bản, 1867.”
- **Visual:** `marx-name` fades under the already-visible portrait; date and
  work appear with it.
- **Roles:** anchor = the three faces; evidence = Marx's label; turn = —;
  payoff = —.
- **State:** on click 1.
- **Hero:** none — the face is already there; the click only names it.

**Beat 2 — click, 251 ms**

- **Spoken:** “Ph. Ăngghen, 1820–1895: Tuyên ngôn, 1848.”
- **Visual:** Engels' label appears, same rhythm.
- **Roles:** anchor = the three faces; evidence = Engels' label; turn = —;
  payoff = —.
- **State:** on click 2.
- **Hero:** none.

**Beat 3 — click, 251 ms**

- **Spoken:** “V.I. Lênin, 1870–1924: Cách mạng, 1917.”
- **Visual:** Lenin's label appears; all three are named.
- **Roles:** anchor = the three faces; evidence = Lenin's label; turn = —;
  payoff = —.
- **State:** on click 3.
- **Hero:** none; the third label closes the cast.

**Beat 4 — click, 1350 ms**

- **Spoken:** “Ba người, ba thời điểm, một dự án: dòng chảy từ lý luận đến
  cách mạng.”
- **Visual:** the timeline draws; the three dots zoom in sequence; the year
  labels appear with each dot.
- **Roles:** anchor = the three faces + names; evidence = the timeline; turn =
  the line; payoff = “1917”.
- **State:** on click 4; 600 + 3 × 250 ms.
- **Hero:** the timeline is the only thing that moves across the slide; it
  turns three portraits into one history.

**Reading order:** title → three faces → Marx → Engels → Lenin → the timeline.
The portraits are never a final reveal; they are the first thing the audience
sees.

## 8. Đối tượng & chức năng — four tools

**Base at t=0:** `bg`, `kicker` “CÔNG CỤ”, `title` “ĐỐI TƯỢNG & CHỨC NĂNG”,
the margin rule. The claim is readable; the 2×2 grid waits.

**Beat 1 — click, 552 ms**

- **Spoken:** “Hai chức năng đầu: thế giới quan — nhìn thế giới như một chỉnh
  thể có quy luật; phương pháp luận — cách đặt vấn đề và hành động trong thực
  tiễn.”
- **Visual:** `tile0` and `tile1` wipe up together; their headings fade
  together; numbers and bodies appear.
- **Roles:** anchor = title; evidence = tiles 01/02; turn = the pair; payoff =
  —.
- **State:** on click 1; 2 movers at the panel beat, 2 at the heading beat.
- **Hero:** the pair is the hero: two tools of thought land as one row.

**Beat 2 — click, 552 ms**

- **Spoken:** “Hai chức năng sau: phê phán cái lỗi thời, mở đường cho cái mới;
  và không đứng trên khoa học — là phương pháp của khoa học.”
- **Visual:** `tile2` and `tile3` wipe up together; headings and text follow.
- **Roles:** anchor = title; evidence = tiles 03/04; turn = the pair; payoff =
  “KHOA HỌC”.
- **State:** on click 2.
- **Hero:** the second row closes the 2×2 and turns four items into one set.

**Reading order:** claim → row 1 (worldview, method) → row 2 (social function,
science). Two clicks, not four; the pair is the unit.

## 9. Luận cương — the quote is the plate

**Base at t=0:** `bg`, `kicker` “LUẬN CƯƠNG”, the giant quote mark, all three
quote lines, the margin rule. The whole quotation is readable before any click;
the attribution waits.

**Beat 1 — click, 700 ms**

- **Spoken:** “Câu này thường bị trích như một khẩu hiệu; tên tác giả và năm
  mới biến nó thành một phát ngôn có nguồn.”
- **Visual:** `quote-rule` draws left-to-right under the quote; `author` fades.
- **Roles:** anchor = quote mark + three lines; evidence = the author line;
  turn = the rule; payoff = “C. Mác · Luận cương về Phoiơbắc, 1845”.
- **State:** on click 1; 400 + 300 ms.
- **Hero:** the attribution is the only move; it turns a floating quotation into
  a sourced argument.

**Reading order:** quote (all of it) → attribution. No line-by-line build;
the claim is never hidden.

## 10. Mang theo — three things and a question

**Base at t=0:** `bg`, `kicker` “KẾT”, `title` “MANG THEO”, the source credits,
the margin rule. The closing frame is readable; the three rows and the final
sentence wait.

**Beat 1 — click, 251 ms**

- **Spoken:** “Mang theo câu hỏi nền tảng: cái nào có trước, vật chất hay ý
  thức?”
- **Visual:** `take0-h` fades; number, body and rule appear with it.
- **Roles:** anchor = title; evidence = row 01; turn = —; payoff = —.
- **State:** on click 1.
- **Hero:** one row, one line; no motion theatre.

**Beat 2 — click, 251 ms**

- **Spoken:** “Mang theo cách nhìn biện chứng: sự vật trong liên hệ, vận động,
  mâu thuẫn.”
- **Visual:** row 02, same rhythm.
- **Roles:** anchor = title; evidence = row 02; turn = —; payoff = —.
- **State:** on click 2.
- **Hero:** none.

**Beat 3 — click, 251 ms**

- **Spoken:** “Mang theo lý luận gắn thực tiễn: giải thích thế giới để cải tạo
  thế giới.”
- **Visual:** row 03; the list is complete.
- **Roles:** anchor = title; evidence = row 03; turn = —; payoff = —.
- **State:** on click 3.
- **Hero:** none.

**Beat 4 — click, 500 ms**

- **Spoken:** “Kết bằng câu hỏi: trong ba cách nhìn này, cách nào bạn đang thiếu
  nhất khi phân tích một vấn đề thật?”
- **Visual:** `closing` floats up from below the list; the credits are already
  visible.
- **Roles:** anchor = three rows; evidence = the list; turn = the closing;
  payoff = “Học triết học là học cách đặt câu hỏi đúng.”
- **State:** on click 4.
- **Hero:** the closing line is the one object that rises; it leaves the list
  and becomes the last thing on screen.

**Reading order:** title → row 01 → 02 → 03 → the closing question. The credits
are static provenance, not a click.

## 11. Global rhythm

| Slide | Base readable? | Presenter clicks | Hero | Max simultaneous movers |
|---:|---|---:|---|---:|
| 1 | yes — title, faces | 0 (1 auto) | three rings | 1 |
| 2 | yes — title, Plato | 3 | three underlines | 1 |
| 3 | yes — title | 3 | question mark | 1 |
| 4 | yes — title, diagram | 3 | straight line | 1 |
| 5 | yes — title, period | 4 | timeline | 1 |
| 6 | yes — title, structure | 2 | three-card wave | 2 |
| 7 | yes — title, faces | 4 | timeline | 1 |
| 8 | yes — title | 2 | paired rows | 2 |
| 9 | yes — full quote | 1 | attribution rule | 1 |
| 10 | yes — title, credits | 4 | closing line | 1 |

## 12. The nine Morphs: 0 kept

The audit in `motion-audit.md` §2.4 has the object-by-object table. The one-line
reason for each:

| Transition | Reason to drop |
|---|---|
| 1 → 2 | the only shared objects are the background and the margin rule; the cover's faces do not continue |
| 2 → 3 | Plato disappears; the definition's question is not the same object as the basic question |
| 3 → 4 | two cards and two diagrams are not the same idea; the Morph would imply materialism = dialectics |
| 4 → 5 | the circle/line do not continue into three historical conditions |
| 5 → 6 | three conditions are not three components; same count, false equivalence |
| 6 → 7 | three parts are not three people; false equivalence |
| 7 → 8 | three portraits do not continue into four functions |
| 8 → 9 | four tools do not continue into a quotation |
| 9 → 10 | the quote's last idea recurs in takeaway 03, but as a different object and hidden at entry |

All nine become a **350 ms Fade**. The fade is a page turn, not a claim of
continuity. The only object that could have continued — the gold thread — was
decoration; it is now a static margin rule and is no longer named `!!thread`.

## 13. What is deliberately still

- Titles, kickers, margin rules, the cover portraits, Plato, the three
  portraits on slide 7, the quote on slide 9 and the credits on slide 10.
- No Ken Burns on the portraits: three portraits would be three movers, and
  the faces are evidence, not ambient wallpaper. The timeline carries the
  motion on slide 7.
- No object lifecycles (enter → move → dim → exit): the argument is additive;
  a dim or exit would hide content the presenter may still need. This is the
  main open question for a second pass.
