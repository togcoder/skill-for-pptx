# T105 [pptx] Dọn skill cũ và tài liệu hết hạn

Agent: Claude (trưởng nhóm). Ngày: 2026-11-12. Theo lời chủ dự án: "đã đến bước hoàn thiện cuối, dọn tài
liệu cũ không cần thiết đi".

## Vì sao

Sau T104, skill PPTX dùng được là `skills/pptx/` (model nhỏ đọc `CARD.md`). Nhưng plugin vẫn nạp cả bốn skill
PPTX đời trước (Motion Director, Morph Studio, Slide Forge, Deck Director) và hai lệnh `/animate-deck`,
`/forge-deck`; README vẫn giới thiệu chúng là sản phẩm chính. Agent mới cài plugin sẽ thấy năm skill PPTX
cạnh tranh nhau.

## Đã làm

- Gỡ `skills/deck-director`, `skills/pptx-motion`, `skills/pptx-motion-director`, `skills/slide-forge` và
  thư mục `commands/`. Mã của chúng trong `scripts/` giữ nguyên (đồ nghề, có test); lịch sử còn trong git.
- **Giữ** `skills/script-writer`: mục 1 và 6 của `skills/pptx` dùng nó để viết kịch bản.
- Giữ các skill của lĩnh vực khác (`document-craft`, `sheet-craft`, `vector-craft`, `iso-vector-craft`).
- Cất vào `docs/archive/`: `STATUS.md`, `PRODUCT_TARGET.md` (viết cho các sản phẩm cũ) và
  `BRIEF_TU_BO_SKILL.md` (việc T104 đã xong). Sửa mọi link trỏ tới chúng.
- README: phần PowerPoint viết lại, trỏ về `skills/pptx` và `CARD.md`. Mô tả plugin đổi theo.
- HANDOFF: dòng đầu ghi tình trạng sau T104.

## Chưa làm, để chủ dự án quyết

- `AGENTS.md` và README có khối "Official Owner Mandate" / "Triết lý cốt lõi" do T044 (OpenCode) thêm: cho
  agent "toàn quyền cài mọi thư viện", chuẩn âm thanh -14 LUFS, v.v. Nó trái với luật "không thêm phụ thuộc"
  ngay trong cùng tệp. Không rõ chủ dự án có thật sự nói vậy không, nên chưa gỡ.
- `knowledge/design_system.json` còn một trích dẫn nguồn tới tệp đã gỡ (giữ làm dấu nguồn gốc).
