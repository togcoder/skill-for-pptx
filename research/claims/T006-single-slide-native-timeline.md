# T006 source note — single-slide native timeline

Date: 2026-10-04.

## Question

Can PowerPoint natively hold many motion effects on one slide so shared resources
do not need one slide per movement?

## Evidence inspected

1. Microsoft Learn, Working with animation:
   https://learn.microsoft.com/en-us/office/open-xml/presentation/working-with-animation

   It describes slide animation as time-based and stored inside the slide XML
   timing element.

2. Microsoft Support, Apply multiple animation effects to one object:
   https://support.microsoft.com/en-us/powerpoint/apply-multiple-animation-effects-to-one-object

   It documents multiple effects on one object and Start choices including
   On Click, With Previous, and After Previous.

3. Microsoft Support, Add a motion path animation effect:
   https://support.microsoft.com/en-us/powerpoint/add-a-motion-path-animation-effect

   It documents custom/editable motion paths.

4. Microsoft Open Specifications, animMotion:
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/498c3cfa-652c-49b3-a82c-33fd94468af8

   It documents PowerPoint interpretation of animation motion paths.

5. Microsoft Open Specifications, spTgt:
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/894705b6-9655-49e3-a6c6-54600f99f7f4

   It states that PowerPoint animation shape targets refer to an object on the
   current slide.

6. Microsoft Open Specifications, tnLst:
   https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oi29500/55167345-00ff-4d39-b4a8-6ca61d86227a

   It records PowerPoint-specific timing-tree constraints that a backend must
   respect rather than writing arbitrary schema-valid timing XML.

## Conclusion

The user's requested architecture is supported in principle: multiple effects can
be sequenced/synchronized on one slide and motion paths can target the same slide
objects. T005's waypoint-per-slide pattern is therefore an implementation
limitation of the Morph baseline, not an inherent PowerPoint requirement.

This note does **not** prove our generated XML works in PowerPoint. T006 must still
author the timing tree, inspect the package, and pass exact-hash native playback.
