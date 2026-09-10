# AOT static-coverage recall — SLUS-01040

_How much of the played reference set did the play-free static extractor reproduce, and how much has unverified address overlap with a compiled static interval?_

- Static shard cache: `build/runtime/cache`
- Static manifest entry addresses: **2858**; content-keyed entry+CRC candidates: **4121**

## vs live capture history

- Sources: **verified append-only history**
- FNV-verified immutable snapshots: **465**; invalid records: **0**
- Dispatch entries exercised: **429**
- Discovered by static: **61** (**14.2%** entry-level recall)
- Contained in some compiled static interval (unverified potential): **379** (**88.3%**)
- Outside all overlay static intervals (potential gaps): **50**
- Exact-entry misses (diagnostic; may be interior fragments): **368**
