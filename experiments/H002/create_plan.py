import json
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parent
W,H=1280,720

def frame(x,y,w,h,text=None):
    value=dict(x=x/W,y=y/H,w=w/W,h=h/H,rotation_deg=0,opacity=1)
    if text is not None:value['text']=text
    return value

def obj(id,kind,geometry,**kw):
    return dict(id=id,kind=kind,persistent=True,morph_name='!!'+id,geometry=geometry,**kw)

objects=[
 obj('lamp-stem','shape','rect',fill='#9E97AC',stroke='none',stroke_width=0),
 obj('lamp-base','shape','ellipse',fill='#9E97AC',stroke='none',stroke_width=0),
]
colors={'read':'#54E7FF','relax':'#BAFA64','create':'#FF659D'}
for mode,color in colors.items():
    objects.append(obj(mode+'-ring','shape','ellipse',fill='none',stroke=color,stroke_width=14))
for mode,color in colors.items():
    objects.append(obj(mode+'-label','text','textbox',fill='none',stroke='none',stroke_width=0,text=mode.title(),font_size=38,text_color=color,bold=True))
objects.extend([
 obj('brand','text','textbox',fill='none',stroke='none',stroke_width=0,text='ORBIT',font_size=64,text_color='#FFFFFF',bold=True),
 obj('product-kind','text','textbox',fill='none',stroke='none',stroke_width=0,text='Đèn bàn giả tưởng',font_size=24,text_color='#C1BACD',bold=False),
 obj('mode-caption','text','textbox',fill='none',stroke='none',stroke_width=0,text='Tập trung',font_size=40,text_color='#FFFFFF',bold=False),
])
positions=[{'read':'center','relax':'left','create':'right'}, {'read':'left','relax':'center','create':'right'}, {'read':'left','relax':'right','create':'center'}]
slots={'center':(640,320,360),'left':(220,350,180),'right':(1060,350,180)}
active=['read','relax','create']
captions=['Tập trung','Thư giãn','Sáng tạo']
states=[]
for i,placement in enumerate(positions):
    frames={
      'lamp-stem':frame(633,501,14,89),
      'lamp-base':frame(530,582,220,22),
      'brand':frame(56,34,260,76),
      'product-kind':frame(884,55,340,38),
      'mode-caption':frame(380,632,520,60,captions[i]),
    }
    for mode,slot in placement.items():
        cx,cy,d=slots[slot]
        frames[mode+'-ring']=frame(cx-d/2,cy-d/2,d,d)
        frames[mode+'-label']=frame(cx-100,cy-32,200,64)
    states.append(dict(id=active[i]+'-focus',message=f'ORBIT là đèn bàn giả tưởng. {active[i].title()} ở trung tâm, vòng sáng đường kính gấp đôi hai vòng còn lại ở hai bên. Dữ liệu và hình dáng minh họa.',objects=frames))
plan=dict(version='0.1',brief='Tạo 3 slide giới thiệu đèn bàn giả tưởng ORBIT. Ba vòng sáng Read, Relax, Create lần lượt phóng lớn ở trung tâm; hai vòng còn lại vẫn hiện ở hai bên. Ít chữ, màu nổi bật, dùng Morph và các đối tượng PowerPoint native.',canvas=dict(width=16,height=9,units='normalized'),data_provenance='synthetic',objects=objects,states=states,transitions=[dict(**{'from':states[i]['id'],'to':states[i+1]['id']},kind='morph',duration_ms=1100,track=[o['id'] for o in objects]) for i in range(2)],research_metadata=dict(experiment='H002',recipe='Overview to detail',original_composition=True,references=[dict(author='Microsoft Support',title='Morph transition: Tips and tricks',url='https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks',access_date='2026-10-04',evidence='Official page text inspected for forced !! object matching and zoom by resizing; no reference media used.',reuse='Technical principle only; no text, template or media copied into slide artwork.')]))
(ROOT/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rubric=dict(experiment='H002',frozen_at_utc=datetime.now(timezone.utc).isoformat(),evaluation_source='skills/pptx-motion/references/evaluation.md',objective_criteria=dict(slides=3,state_order=['Read','Relax','Create'],ring_labels_per_slide=['Read','Relax','Create'],central_ring_diameter_px=360,side_ring_diameter_px=180,central_x_px=640,two_side_rings_visible=True,objects_per_slide=11,native_textboxes_per_slide=6,native_ellipses_per_slide=4,native_rectangles_per_slide=1,pictures=0,videos=0,morph_destination_slides=[2,3],duration_ms=1100,unique_forced_names_per_slide=11,exact_forced_name_match=True,final_package_rendered=True,every_final_slide_visually_inspected=True),ratings=dict(brief_coverage={'range':[0,5],'evidence':'Exact count/state/label inventory plus human reading.'},static_readability={'range':[0,5],'evidence':'Full-size final PPTX renders, no clipped labels or unintended static overlap.'},creative_quality={'range':[0,5],'evidence':'Reviewer judgment of static composition only.'},native_motion={'range':[0,5],'value':None,'evidence':'Remain null until exact-hash playback in named PowerPoint version.'},real_application_editing={'value':None,'evidence':'Remain null until editing exact deck in PowerPoint.'}),composite_percentage=None)
(ROOT/'rubric.json').write_text(json.dumps(rubric,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'BRIEF.md').write_text('''# H002 frozen brief

> Tạo 3 slide giới thiệu đèn bàn giả tưởng ORBIT. Ba vòng sáng Read, Relax, Create lần lượt phóng lớn ở trung tâm; hai vòng còn lại vẫn hiện ở hai bên. Ít chữ, màu nổi bật, dùng Morph và các đối tượng PowerPoint native.

## Decisions made before authoring

- Exactly three 16:9 states: Read focus, Relax focus, Create focus.
- Original composition: a stationary stem and base establish a desk lamp. Three open native ellipse rings retain cyan, lime and pink identities. The selected ring has twice the diameter of the two side rings.
- Sparse text: brand, fictional-product descriptor, three mode names and one short active-mode caption.
- Six independent native textboxes stay separate from the five shape carriers.
- Two consecutive 1100 ms Morph transitions, declared on slides 2 and 3. All 11 objects have unique stable !! names.
- No external image, product claim, measurement, gradient, glow filter or unsupported field. Requested native PowerPoint graphics take precedence over the host skill's default image-asset workflow.
- Three slides provide three endpoint states. Read starts enlarged on slide 1; there is no additional small-to-large entry state for Read.
- The plan implies reciprocal ring swaps. Whether rings or labels remain clear during the transition is unobserved until native playback; static endpoints alone cannot settle it.

## Evaluation frozen before build

Use rubric.json together with the unchanged source evaluation.md. Keep objective counts distinct from subjective 0–5 ratings. Native motion and real-application editing remain null without captured PowerPoint evidence. Do not produce a composite quality percentage.

## Source and isolation

Recipe: overview to detail, applied to an original three-mode product composition. Technical reference: Microsoft Support, https://support.microsoft.com/en-us/powerpoint/morph-transition-tips-and-tricks, accessed 2026-10-04. Page text about stable !! names and resized objects was inspected. No source media or template objects were reused.

No previous experiment plan or artifact was opened. Generic source guidance itself contains prior experiment summaries. The H001/E002 history section in plan-contract.md was not read. All H002 artifacts stay in experiments/H002, build/h002 and the requested output file. Source and docs/STATUS.md remain untouched.
''',encoding='utf-8')
print('Wrote H002 plan, brief and frozen rubric')
