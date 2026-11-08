# Skill patch — motion fit and composition first

Status: **applied on `work/T091-opencode-rung6-motion-law`** (2026-11-08).
T087 merged as `5976663`; the six blocks below are now in `skills/pptx`. The
text is kept here as the reviewable rationale, not as a pending patch. T090
rebases on this branch (or on `main` after merge) and rebuilds the 7-slide deck.

Evidence: the owner's grades of 2026-11-08 (F20/F21). T087 demo 7/10 ("đơn giản
nhưng rất phù hợp"); T069a 6/10 ("quá gượng gạo", composition also named).

---

## 1. `guides/6-chuyen-dong.md` — room scale

Insert **after** the paragraph under `## Câu hỏi duy nhất` (the paragraph ends
"…một slide chuyển động mà rối.") and **before** `## Luật`:

```markdown
## Chọn mức chuyển động theo phòng

Cùng một slide, mức chuyển động đúng thay đổi theo nơi nói. Hỏi ba điều trước
khi chọn: người xem cách màn hình bao xa, họ đến để hiểu bài hay để xem trình
diễn, và slide này có người nói đứng cạnh hay không.

| Phòng | Mức vừa | Ghi chú |
|---|---|---|
| Lớp học, seminar | fade/rise; 1 Morph ở chỗ ngoặt của lập luận | Người xem đến để hiểu bài. Ít mà rõ là đủ. |
| Bảo vệ luận văn, họp nội bộ | như trên, thêm 1–2 Morph có vật tiếp nối thật | Mạch lập luận quan trọng hơn kỹ thuật. |
| Hội nghị, sân khấu lớn | 2–4 Morph, nhịp chậm và biên độ lớn hơn | Ở xa, cú nhích nhỏ không ai thấy; đừng bù bằng nhiều hiệu ứng. |
| Gửi để đọc một mình | gần như tĩnh | Không có người nói; slide phải tự đứng. |

**Đơn giản không phải là lỗi, gượng gạo mới là lỗi.** Một bộ 5 slide với một
Morph và vài cú fade có thể đạt 7/10 nếu vừa với lớp học. Một bộ 14 slide với
bốn Morph "ngữ nghĩa" có thể chỉ 6/10 nếu cú cắt khiến người xem phải giải mã
và bố cục hai đầu chưa đứng được. Đừng thêm hiệu ứng để chứng minh công phu;
hãy làm cho cú cắt trở nên hiển nhiên.
```

## 2. `guides/6-chuyen-dong.md` — four forced-cut questions

Insert **after** the table under `## Chuyển động theo ý nghĩa` (the table ends
with the row "đưa ra kết luận") and **before** `## Ảnh và slide đứng lâu`:

```markdown
## Bốn câu hỏi để biết một cú cắt là gượng

1. **Bỏ chuyển động đi, hai slide có còn đứng được như hai poster không?**
   Không thì sửa bố cục trước. Morph không che được một bố cục yếu; nó chỉ làm
   bố cục yếu chuyển động.
2. **Có một vật nhìn thấy được đi tiếp từ A sang B không?** Nếu phải chỉ tay
   hoặc giải thích mới thấy, đó là hai vật đổi chỗ, không phải một vật biến đổi.
3. **Không nghe lời nói, cú cắt có tự giải thích không?** Nếu cần một câu chú
   thích mới hiểu, cú cắt đang gượng.
4. **Ở khoảng cách 3 m và trong phòng sáng, cú cắt có còn rõ không?** Nếu chỉ
   đẹp trên màn hình 27 inch, bỏ.
```

## 3. `guides/3-bo-cuc.md` — poster test

Insert **before** `## Nhịp của cả bộ`:

```markdown
## Bài kiểm tra poster (làm trước khi thêm chuyển động)

Xuất slide **đã hiện đủ mọi thứ** ra ảnh, thu nhỏ bằng cửa sổ đang xem, rồi
nhìn như một tấm poster:

- Có đúng một điểm nhấn không? Nheo mắt vẫn thấy nó trước.
- Hai bên trái/phải, trên/dưới có cân không? Có khối nào treo lơ lửng một mình
  không?
- Nếu đây là tấm áp phích dán ở hành lang, người đi qua có hiểu ý chính trong
  ba giây không?

Chưa đạt thì sửa bố cục, đừng thêm chuyển động. Một cú Morph nối hai bố cục yếu
sẽ đọc thành hai bố cục đổi chỗ, không thành một ý đang lớn lên.
```

## 4. `guides/8-tu-kiem-tra.md` — questions

Add to `## Câu hỏi cho từng slide` (after "Nheo mắt nhìn…"):

```markdown
- Nếu chỉ nhìn khung hình đầy đủ như một poster, bố cục có cân và có một điểm
  nhấn không?
```

Add to `## Câu hỏi cho cả bộ` (after the Morph question):

```markdown
- Bỏ hết chuyển động, từng slide có đứng được một mình không?
- Cú Morph nào cần giải thích mới hiểu? Đó là cú gượng (xem guide 6).
- Mức chuyển động có vừa với phòng không? (xem bảng trong guide 6)
```

## 5. `guides/7-morph.md` — two limits

Insert **after** the default table (the row "Mọi chỗ khác | none hoặc Fade") and
**before** the paragraph "Một bộ 15 slide thường chỉ có 2–5 Morph…":

```markdown
**Morph không sửa bố cục.** Cả hai đầu của cú Morph phải là hai poster đứng
được một mình (guide 3). Nếu đầu B chỉ đẹp khi đang chuyển, cú cắt đang che một
bố cục yếu.
```

Insert **after** the audit paragraph at the end of `## Kiểm tra`:

```markdown
Audit chỉ kiểm tra cấu trúc: loại hình, tên, hiệu ứng vào, vị trí ngoài khung.
Nó **không** biết cú cắt có đọc như một ý hay không. Câu đó phải trả lời bằng
mắt, bằng bốn câu hỏi ở guide 6.
```

## 6. `SKILL.md` — one sentence in the working order

Insert **after** the sentence "Chuyển động thêm vào một bố cục xấu không làm nó
đẹp lên. Vì vậy bản tĩnh phải đẹp trước." (step 8 note):

```markdown
Chọn **mức** chuyển động theo phòng, không theo số hiệu ứng: một lớp học cần ít
hơn một sân khấu hội nghị. Đơn giản mà vừa tốt hơn phức tạp mà gượng (guide 6).
```

---

## Why these six and not a code change

The failure the owner named is a judgement failure, not a missing command. The
toolbox already writes the four Morphs and the audit already proves they are
structurally legal. What was missing is a written stop: *is this cut worth
making, and do the two frames stand without it?* D011 says improve the guidance
first; no script is added here.

## What to measure after applying

1. T090 rebuilds the 7-slide Triết học deck against the patched skill; the
   owner grades the Morph on slide 3 again.
2. T071's bench adds two briefs: a classroom talk and a conference talk. The
   same content should choose different motion levels.
3. A blind A/B of T069a vs a patched rebuild would test whether the poster test
   actually changes the owner's score; until then this is a proposal, not a
   proven law.
