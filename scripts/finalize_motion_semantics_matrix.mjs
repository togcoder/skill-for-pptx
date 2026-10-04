import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [candidateArg,outputArg,receiptArg,workspaceArg]=process.argv.slice(2);
if(!workspaceArg) throw new Error('Usage: finalize_motion_semantics_matrix.mjs CANDIDATE_DIR OUTPUT_DIR RECEIPT_DIR WORKSPACE');
const candidateDir=path.resolve(candidateArg);
const outputDir=path.resolve(outputArg);
const receiptDir=path.resolve(receiptArg);
const workspace=path.resolve(workspaceArg);
const skill='/root/.codex/skills/builtins/presentations';
const python=process.env.CODEX_PRIMARY_RUNTIME_PYTHON;
if(!python) throw new Error('CODEX_PRIMARY_RUNTIME_PYTHON is required');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const variants=['local-remove','local-hold','anchored-remove','anchored-hold'];
await fs.mkdir(outputDir,{recursive:true});
await fs.mkdir(receiptDir,{recursive:true});
const results=[];
for(const name of variants){
  const candidatePath=path.join(candidateDir,name+'.pptx');
  const finalPath=path.join(outputDir,'T006_motion_semantics_'+name.replaceAll('-','_')+'.pptx');
  await fs.access(finalPath).then(()=>{throw new Error('Refuse to overwrite '+finalPath);},error=>{if(error.code!=='ENOENT')throw error;});
  await finalizePresentation({
    workspaceDir:workspace,
    candidatePath,
    finalPath,
    pythonExecutable:python,
    integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
    explicitTotalSlideCount:1,
    layoutArgs:['--expected-slide-size-emu','12192000,6858000'],
    fontPolicy:{basis:'design',families:['Bitstream Charter']},
    verifyArtifactToolImport:true,
    receiptPath:path.join(receiptDir,name+'.validation.json')
  });
  results.push({variant:name,finalPath});
}
console.log(JSON.stringify({results,powerpoint_playback_verified:false},null,2));
