import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const [planArg, buildArg, finalArg, projectArg] = process.argv.slice(2);
if (!projectArg) throw new Error('Usage: render_timeline.mjs PLAN BUILD_DIR FINAL_PPTX PROJECT_DIR');
const [planPath, build, final, project] = [planArg,buildArg,finalArg,projectArg].map(x=>path.resolve(x));
const python=process.env.CODEX_PRIMARY_RUNTIME_PYTHON;
const skill='/root/.codex/skills/builtins/presentations';
const {resolvePresentationFont,finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);

execFileSync(python,[path.join(project,'scripts/validate_timeline.py'),planPath],{stdio:'inherit'});
const plan=JSON.parse(await fs.readFile(planPath,'utf8'));
if(plan.kind!=='native-timeline-plan') throw new Error('Expected native-timeline-plan');
if(Math.abs(plan.canvas.width/plan.canvas.height-16/9)>1e-6) throw new Error('Experimental renderer supports only 16:9');

const permitted={shape:new Set(['rect','ellipse']),text:new Set(['textbox'])};
const allowedObject=new Set(['id','kind','persistent','morph_name','geometry','fill','stroke','stroke_width','text','font_size','text_color','bold']);
const allowedFrame=new Set(['x','y','w','h','rotation_deg','opacity','off_canvas','text']);
const color=v=>v==='none'||/^#[0-9A-Fa-f]{6}$/.test(v);

for(const obj of plan.objects){
  if(!permitted[obj.kind]?.has(obj.geometry)) throw new Error(`Unsupported kind/geometry: ${obj.id}`);
  for(const key of Object.keys(obj)) if(!allowedObject.has(key)) throw new Error(`Unsupported object field: ${obj.id}.${key}`);
  for(const key of ['fill','stroke','text_color']) if(obj[key]!==undefined&&!color(obj[key])) throw new Error(`Invalid color: ${obj.id}.${key}`);
  for(const key of ['font_size','stroke_width']) if(obj[key]!==undefined&&(!Number.isFinite(obj[key])||obj[key]<0)) throw new Error(`Invalid number: ${obj.id}.${key}`);
  if(obj.font_size===0) throw new Error(`font_size must be positive: ${obj.id}`);
  if(obj.bold!==undefined&&typeof obj.bold!=='boolean') throw new Error(`bold must be boolean: ${obj.id}`);
  if(obj.text!==undefined&&typeof obj.text!=='string') throw new Error(`text must be a string: ${obj.id}`);
}

for(const slide of plan.slides) for(const [id,frame] of Object.entries(slide.initial_objects)){
  for(const key of Object.keys(frame)) if(!allowedFrame.has(key)) throw new Error(`Unsupported frame field: ${id}.${key}`);
  if(frame.opacity!==1) throw new Error(`Partial opacity unsupported: ${id}`);
  if(frame.text!==undefined&&typeof frame.text!=='string') throw new Error(`Frame text must be a string: ${id}`);
}

await fs.access(final).then(()=>{throw new Error('Refuse to overwrite final output');},e=>{if(e.code!=='ENOENT')throw e;});
await fs.mkdir(build,{recursive:true});
await fs.mkdir(path.dirname(final),{recursive:true});

const W=1280,H=720,font=resolvePresentationFont();
const p=Presentation.create({slideSize:{width:W,height:H}});
for(const [i,slidePlan] of plan.slides.entries()){
  const s=p.slides.add();
  s.background.fill='#161419';
  for(const obj of plan.objects){
    const f=slidePlan.initial_objects[obj.id];
    if(!f) continue;
    const sh=s.shapes.add({
      geometry:obj.geometry,
      name:obj.morph_name,
      position:{left:f.x*W,top:f.y*H,width:f.w*W,height:f.h*H,rotation:f.rotation_deg},
      fill:obj.fill??'none',
      line:{fill:obj.stroke??'none',width:obj.stroke_width??0}
    });
    const txt=f.text??obj.text;
    if(txt){
      sh.text=txt;
      sh.text.style={
        typeface:font,
        fontSize:obj.font_size??28,
        bold:obj.bold??true,
        color:obj.text_color??'#FFFFFF',
        alignment:'center',
        verticalAlignment:'middle',
        autoFit:'none'
      };
    }
  }
  const metadata=plan.research_metadata??{};
  const references=metadata.references??(metadata.reference?[metadata.reference]:[]);
  const urls=references.map(ref=>typeof ref==='string'?ref:ref?.url).filter(url=>typeof url==='string'&&/^https?:\/\//.test(url));
  s.speakerNotes.textFrame.setText([slidePlan.message,...urls.map(url=>'Reference: '+url)].join('\n'));
  await fs.writeFile(path.join(build,`initial-${i+1}.png`),new Uint8Array(await(await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
}

const raw=path.join(build,'raw.pptx');
const native=path.join(build,'native.pptx');
const motion=path.join(build,'timeline.pptx');
await(await PresentationFile.exportPptx(p)).save(raw);

const normalization=execFileSync(python,[path.join(project,'scripts/normalize_timeline_textboxes.py'),raw,planPath,native],{encoding:'utf8'});
await fs.writeFile(path.join(build,'native-normalization.json'),normalization);

const timingReport=execFileSync(python,[path.join(project,'scripts/add_timeline.py'),native,planPath,motion],{encoding:'utf8'});
await fs.writeFile(path.join(build,'timeline-insertion.json'),timingReport);

await finalizePresentation({
  workspaceDir:project,
  candidatePath:motion,
  finalPath:final,
  pythonExecutable:python,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:plan.slides.length,
  layoutArgs:['--expected-slide-size-emu','12192000,6858000'],
  fontPolicy:{basis:'design',families:[font]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(build,'validation.json')
});

await fs.writeFile(path.join(build,'renderer.json'),JSON.stringify({
  font,
  canvas:[W,H],
  slides:plan.slides.length,
  renderer:'artifact-tool-native-timeline',
  timeline_writer:'scripts/add_timeline.py',
  native_playback_verified:false
},null,2));
console.log(JSON.stringify({font,slides:plan.slides.length,output:final,native_playback_verified:false}));
