---
trigger: always_on
deps:
  provides: [rule:agent_channel]
  documents: [tmpAI/agent_channel.md]
  consumed_by: [CLAUDE.md, .claude/rules/workspace_standard.md]
---

# Agent Channel (rules_agent_channel.md)

**Authority:** Eve, 2026-11-13. **Scope: this repository only.**
**Status:** ACTIVE. New rule; Eve asked for it so that sessions that work at the same time do not step on each other.

## 1. What it is

Several Claude sessions can work in this repository at the same time, on **one working tree**. The channel is the file
**`tmpAI/agent_channel.md`**: a short, shared note where each session says what it is doing **now** and leaves messages for
the other sessions. `tmpAI/` is git-ignored, so the channel is **not in git**, and it is the agents' own scratch space
(`rules_verification_testing.md` section 6), so no consent is needed to write there.

| | Agent channel | Handoff (`.claude/logs/handoffs/handoff_active.md`) | `SendMessage` |
|---|---|---|---|
| For | what is happening **now**, between sessions | resuming a session; the state at the start of a day | a live nudge |
| Lives | until read and deleted | appended, kept | only while both sessions are open |
| In git | no | yes | no |

## 2. When a session uses it

1. **At the start** of the session: read the channel (after the three always-read files of `CLAUDE.md` 3.1).
2. **Before editing** a file that may be someone else's: read the "Working on now" table. A file claimed by another session is not edited; ask in a message.
3. **At a change of focus** (a new package, new files): update your row of "Working on now".
4. **When something affects another session** (a renamed file, a changed rule, a fix it waits for, a question): post a message.
5. **Before a commit**: re-read the table, and commit only your own files (section 4).
6. **When you finish** (or stop): delete your row, delete the messages you handled, post what the others must know.

## 3. The protocol: post, read, delete, add

1. **Post.** Add a block at the end of "Messages": `### M<number> from <session name> (<session id>) to <session name, role or all>, <date time>`, then 2 to 10 lines: what happened or what you need, in words that need no chat context. A number is the next free one; numbers are not reused while the file exists.
2. **Read.** A session reads the whole file and finds the blocks addressed to it (`to:` its name, its role, or `all`).
3. **Do, then delete.** When a message has been acted on (or answered), the receiver **deletes the block**. A done message is never left as a record: the record is git, the issues and the handoff. If an answer is needed, the receiver posts a new message to the sender.
4. **Add.** Then add your own messages and update your row.
5. A message to `all` is deleted by the session that **posted** it once everyone had time to read it (the next time the poster reads the file and finds no open question), or by Eve.
6. **Never rewrite another session's block**; the only exception is deleting a message addressed to you that is done.
7. **Edit with exact-string edits**, never by overwriting the whole file, and **read the file again just before the edit**: another session may have changed it a moment ago. If an edit fails, read and retry.
8. **Keep it short:** a message is as long as it needs to be to be understood without the chat (about 25 lines is a good size; Eve lifted the 10-line limit on 2026-11-13), the file at most about 300 lines. A session that finds the file longer cleans done items (and says so in a message).
9. **No secrets and no personal data** (names of people, e-mail addresses, tokens). File paths, issue numbers, commit hashes and file:line are the right content.

## 4. Sharing one working tree

- **Stage and commit by explicit file name:** `git add -- <files>` then `git commit -- <files>`. Never `git add -A`, `git add .`, `git add <directory>` or `git commit -a`: they take the other session's unfinished files.
- **Before every commit** run `git status --short` and compare with the claims. A modified file that is not yours is another session's: leave it.
- **Shared files** (`.claude/tasks/tasks.md`, `.claude/INDEX.md`, `.claude/logs/handoffs/handoff_active.md`, `CLAUDE.md`, the rule files, `.claude/design/` files of another session): claim before editing, make a small exact edit, commit it at once. Do not re-sort, reformat or rewrite a shared file without a message to the others first.
- **A file has one owner at a time.** The design files `home_*.md` and `spaces/HOME.md` belong to the HOME session; `recipe_format_spec.md` belongs to the recipe session. Others ask by message.
- A session that did not commit a file of another session, and sees it was swept into its own commit by mistake, says so in a message (what, which commit); nothing is rewritten.

## 5. Names and ids

The **session name** is the one printed by `~/Documents/Insync/gdrive/OBSWORK/20_GITS/my-mentoring/bin/sessions.py` (for example `sparmvet-viz-d8`; it changes when a session restarts, `my-mentoring/sessions.md`). The **session id** is the identifier of the session's transcript (the folder name in the session's scratchpad path, a UUID). Both go in every block, because the name changes. If the other session's name is unknown, write its role in `to:` (`HOME session`, `recipe session`).

`SendMessage` may be used for one line only, to say "new message in `tmpAI/agent_channel.md`"; the content goes in the file.

## 6. The file

If `tmpAI/agent_channel.md` does not exist, create it with this skeleton:

```markdown
# Agent channel (not in git). Rule: .claude/rules/rules_agent_channel.md

## Working on now
| Session (name, id) | Doing | Files or areas it edits now | Since |
|---|---|---|---|

## Messages
(none)
```

A row names the files or folders in editing at this moment, not the whole package. Delete the row when the work is committed.
