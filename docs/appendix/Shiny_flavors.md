## A reminder note on the different Shiny flavors 

| Flavor | Architecture | Pros (Advantages) | Cons (Inconveniences) | Best Use Case |
| --- | --- | --- | --- | --- |
| **Standard Shiny (Server)** | **Client-Server:** Python runs on a remote server/container. | High performance for large genomic data; keeps source code/data secure on server. | Requires a live server or Docker container (GxIT) running 24/7. | **Large datasets** or BioBlend integrations. |
| **Shinylive (WASM)** | **Serverless:** Python is compiled to WASM and runs in the user's browser. | No server needed; can be shared as a single static HTML file or via GitHub Pages. | Slow initial load (downloads Python runtime); limited by user's RAM/CPU. | **Lightweight reports** or "frozen" results for a paper. |
| **Shiny Express** | **Developer API:** A streamlined way to write either of the above. | Fastest way to build; very little boilerplate code; highly readable. | Less "fine-grained" control over complex nested layouts compared to "Core." | **Walking Skeletons** and rapid prototyping. |