# Autonomous-Optimizer-
My packages.
- uses: actions/checkout@v3
  with:
    fetch-depth: 0           # Fetch complete history and tags
    submodules: recursive    # Handle nested submodules
    lfs: true               # Fetch Git LFS objects
    persist-credentials: true # Enable git operations in subsequent steps
