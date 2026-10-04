import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';
const [planPath, outputDir] = process.argv.slice(2);
if (!planPath || !outputDir) throw new Error('Usage: render_plan.mjs plan.json output-directory');
const out = path.resolve(outputDir);
await fs.mkdir(out, {recursive:true});
const plan = JSON.parse(await fs.readFile(planPath,'utf8'));
const W=1280, H=720;
const p = Presentation.create({slideSize:{width:W,height:H}});
const skillDir='/root/.codex/skills/builtins/presentations';
const {resolvePresentationFont,finalizePresentation}=await import(pathToFileURL(path.join(skillDir,'container_tools/artifact_tool_utils.mjs')).href);
const font=resolvePresentationFont();
for (const [i,state] of plan.states.entries()) {
  const s=p.slides.add();
  s.background.fill=plan.background??'#101522';
  for(const obj of plan.objects){
    const f=state.objects[obj.id];
    if(!f) continue;
    if(!['shape','text'].includes(obj.kind)) throw new Error(`Unsupported kind: ${obj.kind}`);
    if(f.opacity!==1) throw new Error('Partial opacity is not implemented in this experimental renderer');
    const sh=s.shapes.add({geometry:obj.geometry??(obj.kind==='text'?'textbox':'ellipse'),name:obj.morph_name,
      position:{left:f.x*W,top:f.y*H,width:f.w*W,height:f.h*H,rotation:f.rotation_deg},
      fill:obj.fill??'none',line:{fill:obj.stroke??'none',width:obj.stroke_width??0}});
    const txt=f.text??obj.text;
    if(txt){
      sh.text=txt;
      sh.text.style={typeface:font,fontSize:obj.font_size??28,bold:obj.bold??true,color:obj.text_color??'#FFFFFF',alignment:'center',verticalAlignment:'middle',autoFit:'none'};
    }
  }
  s.speakerNotes.textFrame.setText(`${state.message}\nResearch experiment. Layout generated from a motion plan. Native playback not verified.\nMechanism reference: https://powerpointschool.com/free-animated-powerpoint-presentation-template/`);
  await fs.writeFile(path.join(out,`slide-${i+1}.png`),new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
}
const candidate=path.join(out,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
await finalizePresentation({workspaceDir:path.resolve('..'),candidatePath:candidate,finalPath:path.join(out,'layout.pptx'),
  pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,
  integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:plan.states.length,
  layoutArgs:['--expected-slide-size-emu','12192000,6858000'],fontPolicy:{basis:'design',families:[font]},
  verifyArtifactToolImport:true,receiptPath:path.join(out,'layout-validation.json')});
console.log(JSON.stringify({slides:plan.states.length,font,output:out}));

