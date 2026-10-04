"""Freeze a new long-label application of the three-slot focus recipe."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEF = ('Tạo đúng 3 slide sơ đồ giới thiệu đề xuất thành phố đáng sống. '
         'Ba khối Không gian cộng đồng, Giao thông bền vững, Hạ tầng thích ứng '
         'lần lượt ở vị trí lớn phía trên giữa, hai khối còn lại ở hai bên phía dưới. '
         'Giữ đủ tên, chữ dễ đọc, màu nổi bật và các đối tượng native với Morph.')

def frame(cx, cy, w, h):
    return dict(x=(cx-w/2)/1280, y=(cy-h/2)/720, w=w/1280, h=h/720,
                rotation_deg=0, opacity=1)

def create():
    names = [('community', 'Không gian\ncộng đồng', '#54E7FF'),
             ('transport', 'Giao thông\nbền vững', '#BAFA64'),
             ('infrastructure', 'Hạ tầng\nthích ứng', '#FF659D')]
    objects = []
    for key, label, color in names:
        objects.append(dict(id=key+'-block', kind='shape', persistent=True,
            morph_name='!!'+key+'-block', geometry='rect', fill='#211F27',
            stroke=color, stroke_width=3))
    for key, label, color in names:
        objects.append(dict(id=key+'-label', kind='text', persistent=True,
            morph_name='!!'+key+'-label', geometry='textbox', fill='none',
            stroke='none', stroke_width=0, text=label, font_size=36,
            text_color=color, bold=True))
    for key, text, size, color in [('title', 'Thành phố đáng sống', 50, '#FFFFFF'),
                                 ('footer', 'Đề xuất minh họa', 22, '#C1BACD')]:
        objects.append(dict(id=key, kind='text', persistent=True, morph_name='!!'+key,
            geometry='textbox', fill='none', stroke='none', stroke_width=0,
            text=text, font_size=size, text_color=color, bold=key=='title'))
    states = []
    orders = [['transport','community','infrastructure'],
              ['infrastructure','transport','community'],
              ['community','infrastructure','transport']]
    slots = [(220,520),(640,320),(1060,520)]
    for focus, order in zip([x[0] for x in names], orders):
        poses = dict(title=frame(640,70,1120,80), footer=frame(640,682,600,36))
        for key, (cx,cy) in zip(order,slots):
            poses[key+'-block'] = frame(cx,cy,480 if key==focus else 400,200 if key==focus else 150)
            poses[key+'-label'] = frame(cx,cy,360,96)
        states.append(dict(id=focus+'-focus',message='Sơ đồ đề xuất minh họa, không phải dữ liệu hay cam kết thực tế.',objects=poses))
    return dict(version='0.1', brief=BRIEF, canvas=dict(width=16,height=9,units='normalized'),
        data_provenance='synthetic', objects=objects, states=states,
        transitions=[{'from':a['id'],'to':b['id'],'kind':'morph','duration_ms':1100,
                      'track':[o['id'] for o in objects]}
                     for a,b in zip(states,states[1:])],
        research_metadata=dict(experiment='H003', prior_recipe='E003 cyclic focus',
            independent_agent=False, references=[],
            limitations=['New prompt, same researcher. This is a transfer stress test, not an independent blind holdout.']))

if __name__ == '__main__':
    (HERE/'plan.json').write_text(json.dumps(create(),ensure_ascii=False,indent=2)+'\n')
