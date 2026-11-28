# Users 
## what and how it can be used for : GOALS, VISION, Feature development
SPARMVET-VIZ is shiny app designed to allow visualisation of different datasets that are obtained on a regulary basis, in a consistent manner. eg. produced from pipelines. 

SPARMVET-VIZ is aimed to be data agnostic (thus can be used with any kind of data - currently only tabular data) - but here I provide examples applied to bioinformatics analysis of bacterial pathogens. 

SPARMVET-VIZ differs from traditional shiny app in the way that it can be adapted to visualisation of different datasets - by building its visuals according to a data analysis recipe - when it reads the data analysis recipe. Thus the app needs only to installed once on a system to be employed to visualise different datasets. This allow reusability of the app - bypassing the need to install a new app everytime a modification needs to be done to visualise a specific dataset.

Thus SPARMVET-VIZ can : 
- be implemented in different compute systems eg. in galaxy, server, home computer.
- data analyses recipes can be tailored to the needs of different analyses - and thus the app can be reused for different purposes. 
- different launch commands - pass a deployement configuration file - which allows the app to be started giving different properties - which allows it to be able to be used as: 
    - static webpage to display the results of a specific data set - which can eg. be updated at different intervals or used to statistically visualise the results at the end of a pipeline
    - showing both visualisation and tables with a minimum exploration possibilities of the data
    - an interative mode (interative dashboard) allows minimal modification of the results where eg. a bad sample can be kept in the quality insurance results but removed from the other analyses - this in a transparent and reproducible way - beacause those removed steps are registered with a reason and writen in a copy of the recipe - which can then exported. This ensures transparency, reproducibility and repeatability. 
- data analyses results can be build in such a way that it allows combiing the results of different pipeline into one visualisation - thus it allows combining the results of different pipelines and tailory all the analysis steps to one spec (eg. specific filters adjusted to one type of data) and grouping of disparate results in one place. As long as the analyses are done on the same set of samples. 

SPARMVET GOALS IDEALS are: 
- to provide tools to do **good data science** and results (plot and tables) you can trust. 
- **transparency and reproducibility** are critical - because it should allow detecting and thus correcting errors that are detected (still in development)
- **allowing audits** (minor modifications of the data analysis) - that remain transparent and reproducible and where choices are documented, thus eg. allowing small corrections eg. removal of observations of poor quality. 
- provide the possibility of **Clear choices** (allowing the user to take informed decisions) by explaining choices and providing the information needed to choose well.
- **The app does not choose for the user:** the app gives the tool, the reproducibility, the transparency and the reliability BUT the choice remain the person who build the data analysis recipes and the users that perform the audit. Choices might depend on context thus it is impossible for the app to prevent bad choices - thus the app cannot decide for the user.

MAJOR RULES enforcing thoses goals: 
- **No silent errors**
- **Inform** - do not decide for the user
- Enforce one source of truth for rules/code. 

OUR VISION:
- make one tool that is reusable and available to the community. 
- make one tool that can be improved and adjusted to other requirements of different types of data analysis (the app must be able to growth) 

**WARNING**
SPARMVET-VIZ is still in the developpment process - and there still might be some bugs. 

SPARMVET-VIZ user modules:
- HOME panel - where the data and visualisation can be viewed, explored and audited - depending on options given in the deployement configuration
- GALLERY - inspiration and shows what visualisations the app can currently do - including filter mechanisms (taxonomy) to find what you are looking . 
- BLUEPRINT (need re-design) - a visual IDE helper that is designed to help developping recipes (manual - AI - Claude assisted) 
- LAB (need re-design) - a set of tools to help preparing data for analysis. Convertion to tsv, simple data and metadata - making synthetic datasets from real data (which can thus be used to allow usage to help build tests) ... 

SPARMVET-VIZ architecture
- shiny layer: (UI) - python shiny express
- layered - modular with separation of concern (libraries separated by roles - with one util library that allow shared functionality)
- Other Important layers
    - layer transformer : 
      - current wrangling tidy-ing engine : python polars
    - layer viz-factory (visualisation): 
      - current visualisation engine : python plotnine (close to ggplot2)

UNDER the Hood: 
- data analysis recipes are designed so they can use wrapper actions around the implemented engines. Engine choice is indicated in the recipe so the correct actions are used. 
- security & limitations: some complex actions must be blocked (for now at least) to avoid the possibility of injecting dangerous code via the recipe (as at the end - a recipe is code)

EXPECTED Feature developments: 
- refactoring layers to allow then to functionne correctly when stwitching to different engines (some code is still not totally sorted out by engine)
- improvement of visualisation layer: 
  - implementation of R: ggplot2 libraries (and other ggplot2 derived libraries to allow more complex visualisations using ploting on) 
  - maps
  - time series
  - alluvial plots
- improvement of the transformation layer (eventually)
  - R tidyverse (dplyr)
- allowing for non-tabular data
  - eg. phylogenetic trees (but that is more complex and scope needs to be defined)

## Demos 
> I think we can leverage the example of my colleage to make short demo videos on the different themes - his example demo (ggindex) is here: <https://discindo.org/posts/2026-11-16-ggindex-video-showcase/> 


### One installed app: different deployements scenari via specific deployement configuration files - for different use cases.

Main panel: HOME
- [ ] Goals and material:  create a cgMLST results recipe [This part will be moved in cgMLST_recipe_description - to keep overview of the demo clearer]
  - data: one table: hamming distances + "metadata file"
    - rename : "metadata file" it is not a real metadata file but supplementary information that should be added - repeateadly  : 3 columns to the data in T1 (we have no real metadata yet for this recipe)
    - We have 2 datasets - same structure - different number of rows. We will build the recipe using the small dataset and verify it works for both datasets. **Showing how a same recipe can be reused for different datasets is part of the demo**
  - [ ] Steps (for each data sets): convertion data set - format : LAB script (current script needs to be updated to support those kind of conversions)
    - input files : 
      - <*.metadata.txt> -> text file needs to be transformed to tabular format with tsv extension. rows contain <columns: content> - the Species : must become part of the file name (also in next file - with "_" in the name for the space) - filename in tabular format: <date>_<species>_additional_information.tsv> table : "Additional information" 
      - <*.cgmlst_hamming_dist*.tabulear> -> Table "Hamming distance" -> current format : tsv BUT with .tabular extension  -> reformat to <date>_<species>_hamming_distance.tsv> -> this will be "Hamming distance table" under data schema in the recipe. species is
    - steps: 
      - T1
        - input : All Columns - display on table/plots in ui "_" becomes space (more redeable) - text remains step all numbers are integer types (straightforward)
        - on import table: if empty row: delete - means extra line
        - missing data : I do not think they are but no id is missing, and 0 means 0 -  
        - combine Hamming distance table to "Additional information" so that the 2 tables have complete information on all rows
         
      - T2 (a) : table T1 must be reformated:
        - remove columns indicative compared pair : hamming, compared_alleles_pair, typed_alleles_pair, missing_alleles_pair
        - Then for corresponding rows - we transform so the rows of 2 columns are concatenated under one column
          - Isolate1 and Isolate2 -> must be merged under -> Isolate -> [Isolate is now ID ]
          - typed_alleles_isolate1 typed_alleles_isolate2 -> Typed alleles Isolate   
          - missing_alleles_isolate1, missing_alleles_isolate2 -> Missing alleles Isolate
        - then filter so only unique Isolate are reported 
        - then crosss join; Schema Size : Typed alleles Isolate + Missing alleles Isolate (should be the same for all isolates - Pairs isolate to the additional table)
      - T3a
        - Create categories for countig rows where we say to which category an Isolate has missing alleles - Categories an Isolate belong (of Missing Alleles Isolate) are:  0-10, 11-20, 21-30, 31+
      - Plot a1 (from T3a) : y -> Missing alleles Isolate x -> count of missing values by categories 0
      - Question: Assuming we would want to use T3a or T2a to find out eg which Isolates to remove and have efficient plotting we could either - T3a aggregate and keep only the counts table and filter manually in T2a by Missing Alleles Isolate for those eg. > 30 then the table will show of Isolates that are bad and need to remove from analysis - Or We could keep T3a steps and filter by 31+ category to have same list of ids from T3a. 
      - T2 (b) 
  
      

Showcase: from static webpage to full home with audit, gallery, lab and blueprint. 
- static web-page (HOME): use case : display results from datasets that receive regular updates and must be analysed in the same manner using a unique data analysis recipe. [ex - server show data, static visualisation of pipeline results]
- static web-page customized (HOME): It is possible to "brand" the app without major changes: eg. logo and css configuration. 
- exploration (HOME) : it is possible to explore the results using simple filters while not applying changes - it allows to understand the data and problems without any results modifications. 
- audit (HOME): in addition to exploration - it is possible to remove add some steps that will allow adapting the visuals to publication ready. Eg. poor quality samples can be kept in quality analysis tables but removed from the results because we do not want to use poor quality samples in the results. Eg. removing ponctual outliers or adapting views with sufficient case repeats to remove cases where the results are not representative because of poor sampling design. All audit steps must be justified - and are tracked in a reproducible and transparent maner - so they can be reproduced later on
  
Additional panels: 
- GALLERY : inspiration source and show case of the current capabilities of visualisations of the app. 
- BLUEPRINT (development ongoing): a graphical IDE with options to have AI assisted recipe development.    
- LAB (development ongoing) : a set of utilities to assist preparation of data (format transformation, anonymisation, fake data making based on real data) to assist preparing data analysis and allow recipes making using non-real data for testing purposes. 

Functionalities gated by the specific deployement configuration file. 


### Scientific workplace : HOME and its different functionalities 
- all functionalities activated : showing all possibilities - reminder: functionalities gated by deployement configuration files 

Show case of the different components and possibilities:
- recipe choice - choosing different recipes rebuild the UI - showing the rebuild. eg. choose figshare and explain the different components of the central panel - show how to navigate in the central panel
- then choose one recipe: 1_ST22 ..
  - show that the different components the central panel have been rebuilt
  - show how to navigate in the central panel - beween groups and plots and tables
  - show how to navigate in the left panel (info, alerts, data set upload, filters, export ... ) one at the time and explain what the different components do 
    - show how the recipe can be reused to analyze another dataset
  - explain the audit mechanism and right panel usage - show the lineage and how to use it for audit (might still be a bit buggy)
    - explain the usage case of the audit and its limit - and the reason of why not to attempt complicated cases 
    - - show how the export work - explain what is inside - to ensure transparency and reproducibiity.

### Mechanisms under the hood - to ensure transparency and reproducibility
- recipes specifications
  - how it forces you to treat missing data - you have to decide what missind data means in each case
  - how controls and warning help you verify that the recipe does what it is supposed to do
  - rules and good practices - enforced actions 

- refused actions, guidelines and warnings
  - security - until the need appears (complex cases)- then options to introduce those possibilities can be evaluated and eventually added. 
  - placement of actions and join - why
  - join types allowed and recommended
  - consequences evaluated and warnings (along the lineage)

- Mechanisms to ensure integrity 
  - hashes and their different usages - the hash chain
  - Ui efficiency 
  - Prevention of changes and data corruption 
 
- Mechanisms to ensure transparency and reproducibility 
    - audit export 
    - original recipe is never changed 
 
- sessions usage 
  - unfinished work
  - Ui efficiency 



