# H001 frozen brief

Tạo hai slide PowerPoint mô tả một quy trình ba bước bằng các khối và chữ chỉnh sửa được: Collect, Inspect, Decide. Cảnh đầu là tổng quan cả ba bước; cảnh sau phóng lớn Inspect ở giữa, vẫn giữ Collect và Decide ở hai bên để người xem không mất bối cảnh. Chuyển cảnh bằng Morph.

Frozen 2026-10-03 UTC, before authoring or evaluating the candidate.

## Assumptions and intended construction

- Exactly two 16:9 slides. No cover.
- The three user-supplied step names remain in English. The shared title is Vietnamese.
- Original layout: equal-size blocks in the first scene; Inspect grows at the center while Collect and Decide become smaller visible side anchors.
- Persistent native rectangles, native textboxes and two rectangular connecting lines. All semantic objects have distinct `!!h001-` names reused in both states.
- The carrier and label are separate identities so labels remain horizontal and readable. The backend fixes font size per object across states. The focus comes from carrier resizing and space allocation, not font-size animation.
- One 1600 ms Morph into the second slide. No rotation, opacity change or camera movement.
- The current renderer background and font resolution are accepted.
- This plan was independently drafted from the prompt and contract. The E001 plan was not read or copied.
- Use the existing renderer and patcher without H001 source changes. Do not update docs/STATUS.md, install a skill, upload or publish.
- Native PowerPoint playback and in-application editing remain separate unobserved gates.

## Recipe

Overview to detail from skills/pptx-motion/references/recipes.md. The specific positions, color assignments, proportions, names and timing were newly designed for H001. Microsoft documentation supplies the unique-name matching and destination-slide resize mechanism.
