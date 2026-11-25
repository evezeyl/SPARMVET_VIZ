# Platforms: what happens when new data or a new recipe arrives

Study only (D-0428). Nothing is decided or built. Date of the reading: 2026-11-21.
Labels: SOURCE (with URL) / READ (file:line) / REASONED.
Posit Connect pages read were "Version 2026.11.1". Quotes come from the pages as returned by a fetch tool that summarises the page; the quotes are the tool's quotes of the page, not a copy I checked by eye.

## Her sentence and the direct answer

Her sentence: "We might need a system for static deployment when new data arrived automatically and when a reload with new recipe arrives. But i think that would be case of webserver , eg Connect -.and i think it has a mechanism to redeploy app when changes (data, recipes arrive)."

Does Connect redeploy by itself when data or recipes arrive on disk? **No. Only in one way: git-backed content.**

- Connect does NOT watch files. I found no sentence that says it restarts a running app when files change. (Process Management page: "The page does not say whether Connect restarts a process when files change"; it only says "A deployment creates a new application directory containing only the deployed content." Not verified that nothing else exists: absence of a sentence is not proof.)
- Connect DOES redeploy by itself when the content is git-backed and the branch (and path prefix) changed in the repository. SOURCE (https://docs.posit.co/connect/admin/content-management/git-backed/index.html, "Git-Backed Content", Connect 2026.11.1): "Periodic Git fetches are automatically performed at ~15 minute intervals for each Git backed application." and "The decision to trigger a new deployment is made after a periodic fetch of the source repository, and only occurs if the specified branch and path prefix have changed since the last fetched commit." Interval setting: "`Git.PollingFrequency`"; "To turn off automatic Git fetches entirely, set the value to `0`."
- So "new data arrives" can mean a redeploy only if the data is committed to the git repository (data in git). "New recipe arrives" the same. A file dropped in a folder on the server does not trigger anything.
- Other ways in: a manual or scripted redeploy (CI job calling the Connect deploy action), or reading data from a place outside the bundle that changes without a redeploy (shared mount, pin, database). See below.

Her guess is half right: Connect has a redeploy mechanism, but it is driven by a git commit (or a CI job), not by arrival of files.

## Table

| platform | does it restart or redeploy the app by itself when files change? | ways new data or a new recipe can reach a running page | what the operator must set up | source (title, URL, quoted sentence) |
|---|---|---|---|---|
| Posit Connect | Not on file change (no source says it does). Yes on a git commit, for git-backed content, polled about every 15 min. | (1) git-backed content: commit data/recipe to the repo, Connect redeploys. (2) CI job: deploy action updates an existing content item. (3) manual redeploy from the publishing tools. (4) data outside the bundle read at run time: shared files on the server, a pin, a database. (5) scheduling does not apply to apps. | Git-backed content set up, or a CI job with an API key; for (4) a path or mount that the administrator makes visible to content, or a pin board. | Git-Backed Content, https://docs.posit.co/connect/admin/content-management/git-backed/index.html: "Periodic Git fetches are automatically performed at ~15 minute intervals for each Git backed application." / From GitHub Actions, https://docs.posit.co/connect/user/publishing-github-actions/index.html: "The `deploy` action updates an existing content item; it does not create one." / Structuring Content and Sharing Resources, https://docs.posit.co/connect/user/structuring-content/index.html: "Content on Connect can access shared resources stored on the Connect server." |
| Shiny Server (open source or Pro) | No for data and other files: an explicit restart signal is needed. Only `ui.R`/`server.R` changes are picked up without it (R apps; not relevant to Python). | Replace files in the app folder and `touch restart.txt`; or restart the server. | The folder layout; whoever delivers data must touch the file. | Shiny Server Pro Admin Guide 1.5.24, https://docs.posit.co/shiny-server/: "An application can be restarted by altering the 'modified time' on a file named `restart.txt`"; changes to data files "read-only at startup" also need a restart; `app_idle_timeout` "Defines the amount of time (in seconds) an R process with no active connections should remain open." Default 5 s. NOTE: this guide is for R apps and for the Pro product; I did not find an official page for Python apps on Shiny Server. |
| `shiny run` / uvicorn behind a reverse proxy | No by default. `--reload` exists ("Enable auto-reload."), shown as a development option; the page does not say anything about production. | Restart the process (systemd, supervisor, container restart). | A process supervisor; the reverse proxy. | run_app, https://shiny.posit.co/py/api/core/run_app.html: `reload` "Enable auto-reload."; "The page doesn't address" development vs production. Create and Run page (https://shiny.posit.co/py/get-started/create-run.html) shows `shiny run --reload --launch-browser app_dir/app.py` as an example (seen only in a search summary: not verified: no source read in full). |
| Container (docker, podman, Kubernetes) | No. A restart policy only restarts a container that exited; a new image needs a new container. A bind-mounted folder shows the new file to the running process at once, but the process decides when it reads it. | New image and new container; or a bind mount / volume the operator updates. | Image build and rollout; or the mount. | Docker, Start containers automatically, https://docs.docker.com/engine/containers/start-containers-automatically/: "A restart policy only takes effect after a container starts successfully." Bind mounts, https://docs.docker.com/engine/storage/bind-mounts/: "a file or directory on the host machine is mounted from the host into a container"; "you want the container to get access to a new build each time you build the source on your development host." Kubernetes and podman pages: not verified: no source read. |
| Galaxy interactive tools | Not verified: no source states it. | Not verified. The pages say tools run as containers under the job system; whether inputs can be refreshed in a running tool: no statement found. | Admin: enable interactive tools, container job destination. | Galaxy InteractiveTools, https://docs.galaxyproject.org/en/master/admin/special_topics/interactivetools.html: they "typically run as software (e.g. Docker) containers in an isolated environment." The page "makes no statement about refreshing inputs." The "per user, per job, new job to refresh" idea comes from a search summary only: not verified. |
| shinyapps.io | No git trigger found. Redeploy is `deployApp()` (also from a CI job, inferred). A redeploy destroys the old instances and local data written by the app. | `rsconnect` redeploy; CI job. | Account, token. | Search summary of the rsconnect and shinyapps.io guide (https://docs.posit.co/shinyapps.io/guide/applications/index.html): "data written by an application to the local filesystem of an instance will be lost when you re-deploy". Page not read in full: not verified. |
| Posit Connect Cloud | Yes on a git push, if "Automatically publish on push" is on (GitHub app). | Push to the branch; manual Republish. | GitHub app access to the repo. | "From GitHub", https://docs.posit.co/connect-cloud/user/publish/github.html and "Deploy a Shiny for Python app to Connect Cloud", https://docs.posit.co/connect-cloud/how-to/python/shiny-python.html: the option text "Automatically publish on push" comes from a search summary only: not verified: page not fetched (one fetch failed with 404 on another URL). |

### More detail on Posit Connect (the main question)

- (a) By itself on file change: no source says so. See above.
- (b) Mechanisms:
  - Manual redeploy of a new bundle: creates a new application directory. SOURCE (Process Management, https://docs.posit.co/connect/admin/process-management/index.html): "A deployment creates a new application directory containing only the deployed content."
  - Git-backed content: polled about every 15 min, redeploys only when the branch and path prefix changed (quotes above). Manual check: an "Update Now" button in the Info panel (search summary only: not verified). Git-backed content "cannot be re-deployed or updated via other means" (search summary only: not verified).
  - API / CI: SOURCE (From GitHub Actions page above): the step `uses: posit-dev/connect-actions/deploy@main`, key passed as `connect-api-key: ${{ secrets.CONNECT_API_KEY }}`; "For Python content, include a `requirements.txt` or a `uv.lock` file." The page does not say whether Shiny for Python is covered by the action (not verified).
  - Scheduling: SOURCE (Scheduling page, https://docs.posit.co/connect/user/scheduling/index.html): "Reports that are published with source code can be scheduled to execute by Posit Connect." Interactive apps "cannot be scheduled" because "These interactive frameworks show the latest data each time they are refreshed." Shiny for Python is not named on the page (it names Shiny R Markdown, Shiny with Quarto, Voila): not verified for our app. A scheduled report on Connect could refresh a pin or a file that an app reads.
- (c) Data that changes without a redeploy:
  - Working directory is replaced. SOURCE (Structuring Content, page above): "Each bundle deployment creates a new directory on disk, so the working directory always reflects the active bundle."; "Deploying a new bundle removes any files written to the working directory."; "However, the working directory is not suitable for persistent data storage."
  - Shared files on the server: "Content on Connect can access shared resources stored on the Connect server." Which path and who allows it on a plain (non-Kubernetes) Connect: not verified (the Persistent Storage support article returned 403; the Files & Directories admin page does not cover it).
  - Volume mounts (Kubernetes execution environments): SOURCE (https://docs.posit.co/connect/admin/appendix/off-host/execution-environment-volume-mounts/): "This allows content to access data on shared filesystems, like NFS, without exposing that data to other content."; "Changes apply the next time the environment launches."
  - Pins: SOURCE (https://docs.posit.co/connect/user/pins/index.html): "Rather than redeploying the content each time the data changes, use a pinned resource and update only the data." and "Your content reads the newest data on each run." (the page's use is for R Markdown, Quarto, Jupyter; our Python app reading a pin: not verified).
  - Database or object store: the Structuring Content page recommends "external databases" (summary: not verified word for word).
- (d) Processes: SOURCE (Process Management page): "Posit Connect launches a process tied to a live application when the first request arrives for that application."; "That process will continue to service requests until it becomes idle and is eventually terminated." Settings: SOURCE (Content Settings, https://docs.posit.co/connect/user/content-settings/index.html) "Min processes: Minimum processes kept running"; "Idle timeout: Minimum number of seconds a worker process will remain alive after it becomes idle - i.e. no active connections."; "Max processes: Maximum simultaneous processes per Connect node". Default values: not verified (a search summary says max 3, min 0: not verified, no page quoted). Meaning for us: with min 0, "read at start" happens again after every idle stop, so a visitor after a quiet period gets a new process that reads the files as they are at that moment. REASONED. With min above 0, a process can live a long time and keeps old data (it does not read files again, see "Today" below).
- (e) Environment variables: SOURCE (Content Settings page): "Alternatively, set environment variables on the Runtime tab."; "Once a variable is added, the value is obscured."; "Environment variables are encrypted on-disk and in-memory." So a path or a token can be given there (the first sentence says "alternatively": the other way was not seen: not verified).

## What the app does today when files change (five lines)

1. Recipe list is read once at start (READ `app/src/bootloader.py:404-417`); a recipe file change is noticed by a 2 s poll (READ `app/handlers/recipe_gate_handlers.py:25`, `bootloader.py:497-532`). FACTS.md E.
2. A data file replaced under a running app: an open page keeps the old picture; a click on another tab shows a yellow notice "reload the page (F5)"; after F5 or for a new visitor the new data is read and only the dependent stored tables are rebuilt (RUN, RUN_FACTS case 5).
3. A refreshed file with a changed column: the next opening is refused with a page that blames the recipe; it recovers by itself within 5 s when a good file is put back (RUN, cases 6, 6r).
4. A half-written file that cuts a line: no message and a wrong table of fewer rows is shown; a cut inside a character is refused (RUN, cases 7a, 7b). There is no lock on source files (READ FACTS.md E, search for locks).
5. No data date or hash is shown on the page (RUN, case 5d); a missing data file at start stops the process with a console text (RUN, case 8; D-0427).

So the app itself already reads the files again at every opening; it needs no restart for new data. A redeploy is needed only for platform reasons (the data is inside the bundle).

## What this means for a static page of this app (options, none chosen)

Visitor effect = what the person sees during the change.

**Option 1. Data outside the bundle, read at each opening (no redeploy).** The weekly job writes into a directory that the platform lets the app read; the app reads it at each opening (RUN case 5).
- Pro: no redeploy, no restart; the app already does this (RUN). No downtime.
- Con: on Connect the operator must have a shared path or mount (not verified for plain Connect; SOURCE for Kubernetes mounts). A page already open keeps the old picture until F5 (RUN case 5). Half-written files can be read (RUN 7a shows a silent wrong table) unless the delivery is atomic. Visitor sees: old picture until reload, then new (about 22-31 s for the first visitor, RUN).
- Half-delivered: the job writes to a new folder or temp name and renames at the end (a rename on one filesystem is atomic: REASONED); the app then never sees a half file. Needs the job to be written that way.

**Option 2. Redeploy per refresh by git (git-backed content).** The weekly job commits new data/recipe to the repository; Connect polls (~15 min) and redeploys.
- Pro: the platform's own mechanism; the deployed bundle is a whole, versioned unit (REASONED); old bundles can be re-activated (Structuring Content page: "Activating an older bundle restores that bundle's original directory state").
- Con: data must live in git (size, privacy: REASONED); delay up to ~15 min; the working directory (and the stored tables written there) is replaced at each deploy, so the first visitor rebuilds tables (REASONED from the 22-31 s RUN). Visitor sees: a short interruption at the switch (what happens to open sessions: not verified).
- Half-delivered: a commit is atomic, so the bundle is whole (REASONED).

**Option 3. Redeploy per refresh by a scheduled CI job through the platform API.** A scheduled job (outside the platform) runs the deploy action.
- Pro: no polling delay; works with data that is not in git if the job builds the bundle (REASONED). The deploy action is documented (SOURCE).
- Con: the job needs an API key; deploy for Shiny for Python through the action is not confirmed on the page (not verified). Same working-directory and rebuild effect as option 2. Visitor sees: as option 2.
- Half-delivered: the job deploys only after its own checks (for example run the recipe check before deploy); a failed deploy leaves the old content (Connect behaviour on failed deploy: not verified).

**Option 4. A restart signal (Shiny Server `restart.txt`, or a process restart on a plain server / container).**
- Pro: simple on a plain server (SOURCE for `restart.txt` on Shiny Server R apps; for Python apps: not verified).
- Con: not needed by this app (it rereads files); a restart cuts open sessions (Shiny Server: "open connections will remain active and valid until the last connection closes itself", SOURCE, so there it is soft). In a container a restart policy is not a redeploy (SOURCE). Visitor sees: a short break on a hard restart.
- Half-delivered: restart after the data is complete only (job order).

**Option 5. Data in a database or a pin read at run time.** SOURCE for pins (reads "newest data on each run"). For this app the data reading is file based (READ FACTS.md D); a database or pin would need a new reader (REASONED). Not judged further: it changes the app, not only the deployment.

## Not verified

- That Connect never restarts an app on a file change (only: no sentence found in Process Management, Git-Backed, Structuring Content).
- Default values of Connect min processes, max processes and idle timeout (no page quoted).
- Where a plain (non-Kubernetes) Connect lets content read a shared directory and who sets it (Persistent Storage article gave 403; Files & Directories page silent).
- Connect "Update Now" button and the claim that git-backed content "cannot be re-deployed or updated via other means" (search summary only).
- Whether the Connect deploy action or API handles Shiny for Python (page silent).
- What an open visitor session sees when Connect switches to a new bundle, and what happens after a failed deploy.
- Shiny Server for Python apps (the guide read is Shiny Server Pro 1.5.24 for R; only the first 100000 characters of 225510 were read).
- `shiny run --reload` being development only (the page is silent on production; the "development" wording is from a search summary).
- Galaxy: whether an interactive tool can refresh inputs, and the "new job" model (no page states it; only container and runner statements read).
- shinyapps.io and Connect Cloud push-to-publish (search summaries only; Connect Cloud publishing page fetch failed with 404).
- Kubernetes and podman behaviour for a changed mounted file or ConfigMap (no source read).
- Atomic rename claims for specific filesystems (REASONED only).
