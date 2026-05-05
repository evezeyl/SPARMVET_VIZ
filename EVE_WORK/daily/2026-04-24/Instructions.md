Now we also need to ensure that demo and test manifests in: 
- assets/gallery_data
- libs/transformer/tests/data 
- libs/viz_factory/tests/data 
- libs/viz_gallery/tests/data 
follow the new standard. I guess you can use the script to update those if necessary


----

@agent read @beautifulMention and follow instructions, using @dasharch personality. We need a full review of the state of the work space: developpment and documentation alignment. You need to thouroughly inspect all the files in the workspace (exclusion list bellow) and detect inconsistencies, incompleteness, unfinished tasks, errors : logic / explanations, potential problems (unknonws), rules, workflow, knowledge, tasks completed vs not completed, implementation plans, architecture decisions, code, incomplete and/or legacy. Be extermely thorough. You are to produce a report from this. You will not implement any changes. Excluded list (files and directories : .github,  .claude, .venv, .vscode (root or subdir), .claude/conversations, .claude/embeddings, .claude/logs, EVE_WORK, tmp, tmpAI, .aiignore, .claudeignore, .clinerules, .gitignore, .directory, Mekfile, .manifest.json, *.code-workspace