import path from 'node:path';
import { pathToFileURL } from 'node:url';
const root=path.resolve(process.argv[2]);
const skill='/root/.codex/skills/builtins/presentations';
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
await finalizePresentation({workspaceDir:root,candidatePath:path.join(root,'build/e002/normalized.pptx'),
  finalPath:path.join(root,'output/PPTX_Motion_Lab_E002.pptx'),
  pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  explicitTotalSlideCount:2,layoutArgs:['--expected-slide-size-emu','12192000,6858000'],
  fontPolicy:{basis:'reference',families:['Bitstream Charter'],referencePath:path.join(root,'output/PPTX_Motion_Lab_H001.pptx'),referenceSha256:'3d59b50afbc2c084e560e0b5d04d990b4f6890a66afca86dc6b951156a436e96'},
  verifyArtifactToolImport:true,receiptPath:path.join(root,'experiments/E002/finalizer-validation.json')});
