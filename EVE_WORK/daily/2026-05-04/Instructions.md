
EXPORT-HASH-2 — read decision_hash values from Parquet metadata at export time. Self-contained, touches only export handlers.



STATIC-VIEW-1c — sidebar for static view. What did colleagues expect to see? Hide entirely, or keep manifest selector?
UI - Persona scoping block — you added several items but they're still fuzzy ("TODO Define exactly"). Worth 10 minutes of scoping before touching code.



SESSION-PERSONA-1 — gate ghost_save on t3_sandbox_enabled. Small guard in session_manager.
STATIC-VIEW-1a/1b — hide view-title banner + default T2 for static personas. You now have feedback from the mini-demo: did anyone react to the static view? That informs 1c (sidebar treatment).
Need your input first:

---

So : I reviewed the scoping and the personalities configuration definitions. Note that it is important, the scoping only define what MUST function together. Otherwise we actually allow on/off by config. Thus allowing developers to choose what their user needs, so they can write alternate persona configuration files. For us, the most important is that we can test, and that it can fit my use cases. 

I am thinking functionalities : user side - And then for you one functionality might associated to diffently to my view. So you will certainly need to trace back some of what you call functionalities. 



Here our pesonalites definitions are more functional examples what I was more interested in is which functionalities need to work together or not bit eg I could have a project-independent-advanced	
Here the whole point of defining group is that we allow flexibility of things that are can be activated independently to adjust for usage / while ensuring a desired usage do not lack the proper functionality	
A13	
yes	functionality on
- 	functionality off
*	will depends at time of implementation ¨
some people might want to have small variations of those configurations, my main goal is to see what should be grouped and what should need to be independent / active deactivate	
    
Web-demo TODO : I do not really think need to work on this right now we can remove	existing
    
Definitions: and all those need to be able to be turned on/off via persona profile – Here I define the groups that work together / independently from each other	
PASSIVE_INTERACT	passive interaction (filter, drops) but do not modify data
DEFAULT_TIER	always T2
ACTIVE_INTERACT (T3) + CMP_MODE + AUTOSAVE + HASHES_EXPORT (link to audit)	always associated with T3 functionality : T3_SAND + CMP_MODE + AUD_RPT + SESS_MGT
EXP_BNDL (export bundle)	For now not associated BUT need to decide if on/off by persona configuration file
EXP_GRF (export individual graph)	
META_ING – allow metadata update 	#TO REVIEW → should we bundle with the import ? BUT sometimes I do not want users to add other data than metadata – but we could have a dependent mapping of the import possibility if only user authorized to import metadata or if would be authorized to import all data, would allow to remove one import field.
IMP_HLP – allow import data (corresponding to manifest schema)	# TO REVIEW : (see META_ING) – we need to allow import in several steps, eg from several location, if we keep META_ING as separate import then wen need to remove the metadata from the automatic mapping 
Note : META_ING , IMP_HELP → DATA_ING always on (so DATA_ING is not a user functionality is a app functionality) – IMP_PNL must be visible if DATA_ING is on, but as we will discuss with the correct functionalities either BOTH META_ING / OR both META_ING and IMP_HLP depending on our discussion	
REVIEW : This one I would like actually to have activation individual for now – becacuse we might detail functionalites (so DEV_MODE is not really a scoping is what I have defined now that I wanted to see when I develop)	actually this one I would like 
BLUEPRINT ARCHITECT	We will probably split activation component, right now  `WRNG_STU` on
    
TEST LAB	yes eg different functionalities starting to put in place
DATA PREP	exporter to help transform xlsx to individual tsv dataset – including export of those
CREATE_TEST_DATA	allows generating dummy data for testing purposes (eg. from real data, using ranges/levels, creating dummy ids, introducing errors, defining  how much data eg. number of lines, introducing mismatches between ids, …. to help developers test and improve pipeline – also export function (for developers)
CREATE_MANIFEST_BROILER_PLATE (prefill as much as possible from dummy test data) (for developers)	creates manifest broiler plate from dummy data sets
    
AUTOSAVE #REVIEW → would the cache be calculated even if autosave not enabled , eg If a user cant modify but wants to return to the pipeline results eg saving time instead of the whole pipeline recalculating the whole wranging + plots (making more responsive ? ) - could be on/off depending on deployement possibilities eg for caching ? Autosave at apply in T3 ? 	
HASH functionality will be on I think all the time, see also above autosave BUT the export (aka get the all 3 hashses – need to be activated on/off – when we need to have T3 activated need to allow fetching hash for T3 data)	
PRS_BADGE : note that this is more for me when developping, might be hidden in production (eg. a person test all the functionality with this shown and then deactivate it for production)	
MAN_SEL (if MAN_FIX then no selector = opposite actions)	
UI_TITLE	# REVIEW : discuss Note : could be added via a field in the manifest for example – so could be read directly from the manifest if MAN_SEL is active, so that would mean but would be nice to be able to decide if want to show or not – then shown / not shown (or other info from persona config)
UI_SUBT	# REVIEW : discuss Note : could be added via a field in the manifest for example – so could be read directly from the manifest if MAN_SEL is active, so that would mean but would be nice to be able to decide if want to show or not – then shown / not shown (or other info from persona config)
SHOW_NAV	
