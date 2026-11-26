# Author manifest: how to write who made a recipe and who to ask

Date 2026-11-17. Research and proposal only. No repository file was changed.
Labels: **WEB** = read on the page (URL given), **CODE** = read in the repository (file:line), **MEMORY** = from memory, not verified.

## 1. What you see first

- Your idea (separate fields, a common standard) is sound. A common standard exists and it is YAML-friendly: **Citation File Format (CFF)**.
- Today `info.contact` is one text. In 7 shipped pipelines it looks like a name and an email (the value has an "@"). CODE: `config/data_analysis_recipes/pipelines/*.yaml` line 7 (line 20 in `2_test_data_ST22_dummy.yaml`).
- Making `contact` a set of fields **changes the recipe format**. The spec says any change of meaning of a key changes the version number (`recipe_format_spec.md` section 4.1). So this is a decision about format version 2, not a small edit. See section 7.
- Old one-line texts **cannot be split safely** by a tool. A person must do the split. See section 5.
- Privacy: an email and an address in a recipe go into every export and into git. Make only the name required, and warn about private addresses.

## 2. The standards (what each one says)

All "required" statements are what the page says. Where a page was cut or silent, it says "not stated".

| Standard | Person fields | Institution fields | Required | Roles | Identifiers | Several people | Licence | YAML form |
|---|---|---|---|---|---|---|---|---|
| **CFF** (CITATION.cff) | `family-names`, `given-names`, `name-particle`, `name-suffix`, `alias`, `affiliation`, `orcid`, `email`, `tel`, `fax`, `website`, `address`, `city`, `region`, `post-code`, `country`. None required. | `name` (required), `address`, `city`, `region`, `post-code`, `country`, `alias`, `date-start`, `date-end`, `email`, `tel`, `fax`, `website`, `location`, `orcid` | File needs `authors`, `cff-version`, `message`, `title`. `contact` optional. | Only two: `authors` and `contact` (both are lists of person or entity). No free role field in the person object. | `orcid` (a field). No ROR field in the list read. | Yes: both `authors` and `contact` are arrays | CC-BY-4.0 | Yes in practice (GitHub, Zenodo, Zotero read it; the pages say "plain text", I did not see the word YAML, MEMORY: it is YAML) |
| **CodeMeta** (on schema.org terms) | `givenName`, `familyName`, `name`, `email`, `address`, `affiliation`, `identifier` (ideally ORCID), `contactPoint` (v4) | `name`, `url`, `identifier`, `description`, `alternateName`, `sameAs` | not stated | `author`, `contributor`, `maintainer`, `producer`, `copyrightHolder`, `funder` | `identifier` URL | lists | CC-BY (page footer) | JSON-LD (the canonical files are `.jsonld`); no YAML form seen |
| **schema.org Person / Organization / ContactPoint** | Person: `name`, `givenName`, `familyName`, `email`, `telephone`, `address`, `affiliation`, `worksFor`, `jobTitle`, `identifier`, `sameAs`, `contactPoint`. ContactPoint: `contactType`, `email`, `telephone`, `availableLanguage`, `hoursAvailable`, `areaServed` | Organization uses the same Thing terms (`name`, `url`, `identifier`) | none | via the property that points to the person (`author`, `maintainer`...) | `identifier`, `sameAs` | lists | CC BY-SA 3.0 (terms page) | JSON-LD / microdata; no YAML |
| **RO-Crate 1.2** | Person: `@id` (an ORCID URI is preferred), `name`; examples also `givenName`, `familyName`, `affiliation`, `email`, `contactPoint` | Organization: `@id` (ROR URI in examples), `name`, `url` | minimum for a Person: `@type`, `@id`, `name` | `author`, `publisher`; contact goes through a Person or Organization with `contactPoint` | ORCID, ROR | lists | not stated on the page read | JSON-LD only (a JSON file) |
| **DataCite 4.6** | `creatorName` (one, "Family, Given"), `nameType` (Personal/Organizational), `givenName`, `familyName`, `nameIdentifier` + scheme (ORCID, ROR, ISNI), `affiliation` (+ ROR id) | same fields with `nameType` Organizational | `creator` (1 to n) and `creatorName` | `contributorType` has 22 values; **ContactPerson** is one: "Person with knowledge of how to access, troubleshoot, or otherwise field issues related to the resource." | ORCID, ROR | repeat the property | not stated on the pages read | XML / JSON; no YAML form |
| **Dublin Core terms** | none: no name parts, no email. Values are a URI or a text | none | none | `creator`, `contributor`, `publisher`, `rightsHolder` | URI | repeatable | not stated on the page read | RDF; no YAML form |
| **Frictionless Data Package** | `contributors[]`: `title` (name, required), `path`, `email`, `role`, `organization` | same object (title = organisation name) | `title` | `author`, `publisher`, `maintainer`, `wrangler`, `contributor` (recommended values) | none | array | spec licence not stated | Yes (JSON, YAML is common, MEMORY) |
| **Nextflow `manifest.contributors`** (since 24.10) | `name`, `affiliation`, `email`, `github`, `orcid`, `contribution` | none separate | not stated | `contribution`: list of `author`, `maintainer`, `contributor` | `orcid` URL | list of maps | not checked | Nextflow config (Groovy-like), not YAML |
| **Galaxy tool XML `creator`** | `person`: `givenName`, `familyName`, `name`, `honorificPrefix`, `honorificSuffix`, `jobTitle`, `url`, `identifier`, `image`, `alternateName`, `description`, `address`, `email`, `telephone`, `faxNumber` | `organization`: `name`, `url`, `identifier`, `image`, `alternateName`, `description`, `address`, `email`, `telephone`, `faxNumber` | both optional | one element: `creator` (no contact role) | `identifier` | several `person` / `organization` | not checked | XML; the page says it is modelled on schema.org |
| **R `Authors@R`** | `given`, `family`, `role`, `email`, `comment` (ORCID goes in `comment`) | use `cph` (copyright holder) with the legal name | each author needs a role | `aut`, `cre` (creator and maintainer), `ctb`, `cph` | ORCID, ROR "strongly encouraged" | several `person()` joined | not checked | R code, not YAML |

URLs read:
- CFF: https://raw.githubusercontent.com/citation-file-format/citation-file-format/main/schema-guide.md ; https://github.com/citation-file-format/citation-file-format (licence) ; https://citation-file-format.github.io/ (GitHub, Zenodo, Zotero use it)
- CodeMeta: https://codemeta.github.io/terms/
- schema.org: https://schema.org/Person , https://schema.org/ContactPoint , https://schema.org/docs/terms.html
- RO-Crate: https://www.researchobject.org/ro-crate/specification/1.2/contextual-entities.html
- DataCite: https://datacite-metadata-schema.readthedocs.io/en/4.6/properties/creator/ , https://datacite-metadata-schema.readthedocs.io/en/4.6/appendices/appendix-1/contributorType/
- Dublin Core: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/
- Frictionless: https://specs.frictionlessdata.io/data-package/
- Nextflow: https://docs.seqera.io/nextflow/reference/config/manifest
- Galaxy: https://docs.galaxyproject.org/en/latest/dev/schema.html
- R: https://cran.r-project.org/doc/manuals/r-release/R-exts.html#The-DESCRIPTION-file

Limits of this table (WEB fetch tool summaries, long pages were cut): for CFF I read the first 100000 of 107773 characters, so a field at the very end could be missing. I did not open a CFF YAML example, so the hyphenated key spelling comes from the schema guide text only.

## 3. Which fits best

**CFF** fits best, for four reasons.
1. It is a plain key-value file, meant to be written by hand (WEB, citation-file-format.github.io). The others are JSON-LD, XML, RDF or R code.
2. It has the three things you named: a person (name parts, `affiliation`, `address`, `email`, `orcid`), an institution (an `entity` with `name`, `address`, `email`), and a separate **`contact`** list next to **`authors`**. No other standard I read has "authors" and "contact" as two lists of the same person shape.
3. GitHub, Zenodo and Zotero read a `CITATION.cff` (WEB). So the export could later write one file and the citation is done.
4. Licence CC-BY-4.0 (WEB): we may reuse its key names with credit.

What I would take from the others:
- **DataCite**: the idea that "contact person" is a role (`ContactPerson`), and ROR for an institution. Useful if a recipe is deposited with a DOI later (MEMORY: Zenodo is built on DataCite; not verified).
- **Frictionless / Nextflow**: a role list (`author`, `maintainer`, `contributor`). CFF has no such field. We do not need it if we keep two lists (`authors`, `contact`).
- **Galaxy / schema.org**: nothing to take. Galaxy writes `creator` in XML in the tool, not in our recipe, and it has no contact role. Suggestion: if a recipe runs inside Galaxy, a later converter can map our person fields to its `person` (`givenName`, `familyName`, `email`), because both come from the same name parts.

CFF gaps: no ROR field in what I read; no role beyond authors and contact. Both can wait.

## 4. What exists in the code today

| Place | What it does | Evidence |
|---|---|---|
| Spec | `contact` is optional text, "who to call when the recipe fails; the load gate shows it (ADR-094)". `info` is the only free-form block. DEC20 keeps `info` free-form (project, contact, any key). | `.claude/design/recipe_format_spec.md:112`, `:337` (section 7.1), `:228` |
| Checker | `info` allows `label` (required) and optional `description, subtitle, contact, version, comment`; `free_form: true` | `libs/utils/src/utils/recipe_spec.yaml:12-15` |
| Checker advice | I02: advice (never blocks) when `info.description` or `info.contact` is missing. It only tests "empty or not". | `libs/utils/src/utils/recipe_check.py:235-237` |
| Read the header | `read_data_analysis_recipe_header` reads `id` and `info` with `yaml.safe_load`, survives a broken body | `app/modules/data_analysis_recipe_validator.py:~406-425` |
| Resolve | `resolve_contact`: recipe `info.contact`, else deployment contact, else None; returns `str(...)` | `data_analysis_recipe_validator.py:428-435` |
| Clean | `_clean_contact`: a blank text is absent | `:438-443` |
| Export record | `export_contact_record` gives `{contact, contact_source}`; `export_contact_readme_line` writes one README line, whitespace collapsed | `:446-466` |
| HOME refusal | message ends with "Contact: ..." from one string | `data_analysis_recipe_validator.py:~469-479`; HOME panel `app/handlers/recipe_gate_handlers.py:101` |
| Load gate | contact kept per rejected recipe: `resolve_contact(info, self.get_contact())` | `app/src/bootloader.py:404`, `:424`, `:485`; fatal message at `:538`; fallback `get_contact()` at `:497-499` |
| Export | `effective_run.yaml` gets `contact` and `contact_source`; README gets the line | `app/handlers/export_handlers.py:1449-1451`, `:1472-1473`, `:1996` |
| Info panel | any nested mapping in `info` is already shown with indentation | `app/modules/data_analysis_recipe_info.py:18-28` |
| Docs | export doc says contact is the `info.contact` text, else `branding.contact` | `docs/user_guide/understanding_your_export.qmd:47-49`; also `docs/appendix/Terminology.qmd:8`, `docs/foundations/data_contracts_adr.qmd:21`, `docs/UML/data_contract_and_failures.md:68-71`, `docs/user_guide/system_transparency.qmd:44` |
| Deployment | `branding.contact` is free text: demo = a role email, local = an issue tracker URL, template = a team email | `config/deployment/demo/demo-vetinst.yaml:26`, `local/local.yaml:11`, `templates/deployment_template.yaml:49` |
| Tests naming contact | `app/tests/test_export_contact.py` (8 tests, all use a text), plus 13 more test files: `test_data_analysis_recipe_info`, `test_blueprint_failed_load`, `test_export_refusal`, `test_checker_names_what_a_component_is`, `test_advice_one_sentence`, `test_export_download`, `test_export_download_path`, `test_recipe_gate_handlers`, `test_join_key_one_pin`, `test_seed_refusal_text`, `test_data_analysis_recipe_load_gate`, `test_gate_gap`, `libs/utils/tests/test_recipe_check.py`, `test_recipe_loader.py` ; four recipes in `app/tests/equality/recipes/` carry it too | grep, not each line read |

Shipped recipes that set `info.contact` (CODE, shape only): 7 pipelines (a text with an "@", probably a name and an email: `1_Abromics_general_pipeline`, `1_test_data_ST22_dummy`, `2_test_data_ST22_dummy`, `3_test_no_joins`, `demo_abromics`, `figshare_integration`, `stress_test_master`) and 1 template `left_join_lesson.yaml` (a role text with no person and no email). No gallery bundle (`assets/gallery_data`) sets it (grep found none). Not counted: the test-equality recipes, the transformer test recipes, copies in `.claude/worktrees/`.

Noted: `info_lines` already shows nested mappings, so HOME's Info panel would show a mapping with no change.

## 5. Options

Made-up data in every example: DEMO CREATOR, institution "Claude & Eve", demo_bogus@email.com.

### Option A: CFF shape (`authors` list + `contact` list)

```yaml
info:
  label: "Demo recipe"
  authors:
    - given-names: DEMO
      family-names: CREATOR
      affiliation: "Claude & Eve"
      orcid: "https://orcid.org/0000-0000-0000-0000"
  contact:
    - given-names: DEMO
      family-names: CREATOR
      affiliation: "Claude & Eve"
      email: demo_bogus@email.com
      address: "1 Demo Street"
      city: Demoville
      country: NO
    - name: "Claude & Eve data office"     # an institution: CFF entity
      email: demo_bogus@email.com
```

- Required: nothing in CFF's person. My suggestion for us: every entry needs a name (`family-names` or `name`); `email`, `address`, `orcid` optional.
- One contact against several authors: yes, two lists. `contact` is the person to ask when the recipe fails (D-0208). `authors` is for credit.
- Migration: the old text goes to a person by hand. Mechanical only when the text is exactly an email (becomes `contact: [{email: ...}]` with no name, which fails the "name needed" rule) or exactly a URL. "Name and email" text: a tool can propose a split (text before `<` or before the email) but a wrong guess is silent; I would print a list and let a person write the fields (no guessing, principle 1).
- HOME refusal: "Contact: DEMO CREATOR, Claude & Eve, demo_bogus@email.com" (one line built from the first contact; name, institution, email only. Address not shown).
- Export: `effective_run.yaml` writes `contact:` as a list of mappings and `authors:`; README gets one line; a later `CITATION.cff` is a near copy.
- `branding.contact`: stays one text (it is a role address or a URL, not a person). `contact_source` stays.
- For: closest to a real standard, citation-ready, YAML native. Against: hyphenated keys (`family-names`) differ from our snake_case style; the two lists are more to write; the recipe author must know "name part" rules.
- Effort (estimate): spec and checker data 0.5 day; resolve/format/export code and HOME text 1 day; migration of 8 files by hand 0.5 day; tests (15 files touched) 1 day; docs 0.5 day.

### Option B: flat fields, one contact only

```yaml
info:
  label: "Demo recipe"
  contact:
    name: "DEMO CREATOR"
    institution: "Claude & Eve"
    address: "1 Demo Street, Demoville"
    email: demo_bogus@email.com
```

- Required: `name`. Names are ours (`institution`), not a standard's. Several people: not possible without inventing a list.
- Migration: same as A.
- HOME and export: simplest; one line.
- For: smallest change, easy to write. Against: **invented**, which you asked not to do; not citation-ready; no authors; a later move to a standard is a second format change.
- Effort (estimate): about 2.5 days.

### Option C: schema.org / CodeMeta names

```yaml
info:
  label: "Demo recipe"
  author:
    - "@type": Person
      givenName: DEMO
      familyName: CREATOR
      affiliation: { "@type": Organization, name: "Claude & Eve" }
      email: demo_bogus@email.com
  maintainer: ...
```

- The names are camelCase and need `@type` to be correct; the YAML would mimic JSON-LD. A CodeMeta file is JSON-LD, not YAML (WEB), and CodeMeta has `maintainer` but no "contact" role as a list of its own.
- For: the widest vocabulary; Galaxy's `person` uses the same names. Against: heavy for a hand-written YAML; no YAML tool reads it directly; no ready citation path.
- Effort (estimate): 3 days or more.

| | A: CFF shape | B: flat, own names | C: schema.org |
|---|---|---|---|
| Common standard | yes | no (invented) | yes, but JSON-LD |
| Hand-writable in YAML | yes | yes | clumsy |
| Contact apart from authors | yes | contact only | needs a role |
| Several people | yes | no | yes |
| Citation later | yes (CITATION.cff) | no | via CodeMeta, extra step |
| Size of change | largest | smallest | large |

## 6. Privacy

- An address and an email written in a recipe are copied into every export bundle and into git history. A person cannot take it back from git. WEB: GDPR Art. 6 says processing needs one lawful basis such as consent, contract, legal obligation, public task or legitimate interests (https://gdpr-info.eu/art-6-gdpr/). I did **not** check which basis fits a research recipe, nor how GDPR treats a work email. Ask the institute's data protection officer.
- MEMORY, not verified: institutes usually publish a role address (for example a group or data-office mailbox) and an ORCID, not a private email or a home address.
- Suggestion: `email`, `address`, `tel`, `orcid` all optional. Only a name is needed. Prefer an `entity` (institution or group) as the contact.
- Suggestion: checker advice (never a block): "this recipe has a street address or a telephone: it goes into every export and into git". Also an advice if the email is on a free-mail domain (gmail, outlook...), and an advice if an old one-line text is still there.
- Suggestion: HOME shows name, institution and email only; the address and phone are kept for the export, not shown to every user.

## 7. Is it a format change?

Yes, as the spec is written. Section 4.1 says "Any change of structure changes the number: a key added, removed or renamed, a change of required-ness or meaning". Changing `contact` from text to a list or mapping is a change of meaning. Adding `authors` is a key added. The app reads one version only. So all recipes would need `spec_version: 2` and the migration tool `migrate_recipe_format.py` would need a new run (spec 4.1 describes Run A and Run B for 0 to 1).

Two points that are not clear and need your word:
1. `info` is `free_form: true` (`recipe_spec.yaml:15`). A new key under `info` is not refused today. So `authors` might not need a new version. But 4.1 says a new optional key breaks an older checker; for `info` that is not true. This is an interpretation: I do not decide it.
2. A tool that accepts **both** the old text and the new mapping would be a shim. Principle 4 and `rules_legacy_management.md` forbid it ("do it properly or do not do it at all"). So the choice is: version 2 with all recipes migrated at once, or a new key (`authors`/`contacts`) beside a contact that stays text for now (two ways at once, which the same rule also dislikes).

## 8. The agent's recommendation, not a decision

Option A, CFF shape: `info.authors` (optional) and `info.contact` (a list of person or entity, name needed, all else optional), as recipe format 2, with the 8 shipped files migrated by hand and the migration tool printing a list of old texts to fix. `branding.contact` stays one text.

Why: it is a real standard, YAML-native, citation-ready, and it separates the person to ask from the people to credit.

Suggestion: if you want less work now, take A but write only `contact` first (a list) and add `authors` in the version that adds the citation file. That is still format 2.

## 9. Questions for you

1. Which option: A (CFF shape), B (flat), or C (schema.org)?
2. Do you want `authors` now, or only `contact` first?
3. Is `contact` one person or several? (A allows a list.)
4. Is a change of `info.contact` from text to fields a new format version (`spec_version: 2`), or is `info` free enough to add fields without a new version?
5. Which fields are required? My suggestion: only a name. Is an email required for a contact (a contact with no way to reach it is useless)?
6. Should `branding.contact` of the deployment stay one text?
7. Do you want a `CITATION.cff` written into the export later? (It would need `authors`, a `title` and a `message`.)
8. Should the checker warn about an address, a phone, or a free-mail email?
9. The 7 pipelines hold your own contact text: do you fix them by hand, or may a tool propose a split that you confirm?

## 10. Not checked

- The last 7773 characters of the CFF schema guide; whether CFF has a ROR field; the CFF YAML spelling in a real example file.
- Contributor property page of DataCite (whether `contributorType` is required, whether a contributor can be a ContactPerson without a type); DataCite, RO-Crate, Dublin Core, Frictionless, Nextflow and Galaxy licences.
- Whether `contact` for Galaxy workflow files (not tool XML) has a different field; the Galaxy page read was 100000 of 392565 characters.
- R: only the first 100000 of 616419 characters; I did not check that a maintainer needs an email (the page does not say it in the part read).
- Which GDPR basis applies; any national law; what an institute's policy says.
- The exact values of the 8 recipes' contacts (I checked only that they contain an "@"); the four recipes in `app/tests/equality/recipes/` (only that they name contact); which test lines would break.
- `docs/UML/app.mdj` and ADR-094 text (the UML and ADR sync law applies to a build, not read here); the decision ledger beyond lines D-0101, D-0165, D-0208.
- All effort figures are my estimates, not measured.
