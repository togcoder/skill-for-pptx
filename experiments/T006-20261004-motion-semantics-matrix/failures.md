# Useful execution failures

1. The first bootstrap passed the final path inside the same build directory as
   the private validation receipt. The host finalizer rejected that layout. A
   fresh run placed the bootstrap output in a separate subdirectory.
2. The first matrix-finalizer call did not export RUNTIME_NODE_MODULES.
   First-party import failed before any final variant was published. Rerunning
   the unchanged candidates with the required runtime variable produced all
   four validated outputs.

Neither failure was a quota error or PowerPoint observation. No acceptance
criterion was relaxed.
