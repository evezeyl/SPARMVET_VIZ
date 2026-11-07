---
date: {date}
authors: 
    - "Eve Zeyl Fiskebeck
    - "gemini's/antigravity AI"
title: "ST2.2 SOA8 / SPARMVET_VIZ Dashboard"
subtitle: "Concept Visions: problem it solves, and how it works""

audience:
    - Non technical stakeholders: Biologists, veterinarians, Reseacher project managers. No coding experience assumed. No deep technical understanding assumed.
requirements: presentation should be understandable for non technical stakeholders, and should not be too technical. It should be possible to understand the concept and the solution without understanding the technical details.

duration : 10-15 minutes
maximim_number_slides: 15

tags:
    - dashboard
    - presentation
    - concept
    - vision

content: 
    - "Problem to solve: develop visualisation for the project"
        - "Nobody really knows what and how to do it"
        - "Species did not have yet decided what to do / want to see"
        - "Reusability : single case publication ready figure VS **reusable** for everybody (requires prealable agreement)"
        - "Reusability across projects: Means several projects can contribute to the costs and benefit ...) 
    - "Solution proposed for our users: 
        - "Develop a dashboard for the project that is:
            - can be implemented in different systems (architecture is modular)
            - can be used with diffent types of data and produce visualisation for all those
            - reusable for everybody when people know what they want (then it is just a matter of creating the right configuration files - should be faster and easier than starting from scratch)
            - can be used for several purposes: eg. fixed figures at the end of a pipeline
            - can be used for exploration of data: eg. finding and removing poor quality samples and rebuilding the figure, while ensuring that the reasons are tracked (ensuring transparency, reproducibility and factilitating manuscript preparation)
            - provide inspiration (gallery of figures) : ask for a new figure, get a new figure
            - developper mode: help to create own visualisation for non technical users (gallery + developper mode)
    - "techincal solution proposed":
        - an app using several indendent libraries that uses human redeable configurations (step lists) to produce figures (from getting the data, preparing the data to make it ready for analysis, analysis and production of figures)
        - The app will work no matter what the type of data is AS LONG as the data is TABULAR (stage 1) and in the correct format. 
        - an interactive user interface (ca. website) that allows users to view, create and modify examples, search for inspiration (gallery) and produce complex configurations files to produce more figures for different tools and share those with the community! (eg. ST2.2 but also others) 
    - "development status":
        - "we have a working prototype of the app ?
        - interactive visualisation part requires debugging, improvement of functionnalties and outlook. 
        - require testing and implementation in different systems 
    
--- 


