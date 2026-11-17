"""viz_gallery: the gallery of example recipes, as a library with no screen code.

What it serves: the GALLERY user space. It checks the example folders of `assets/gallery_data/`, builds the index the
viewer reads, reads the taxonomy (axes, labels, icons) from the specification data, and writes an example in the
standard recipe form.

Inputs: example folders (recipe, data, teaching text, picture) and `utils/recipe_spec.yaml`.
Outputs: `gallery_index.json`, the filter panels' content, example recipes written as text.

Nothing is exported here on purpose: callers import the module they need (`viz_gallery.gallery_manager`,
`viz_gallery.taxonomy`, `viz_gallery.example_recipe`). No Shiny import.

If this file is deleted: the package turns into a namespace package, which still imports but has no `__file__`, so a
check of where the package was loaded from cannot say which copy of the code it is (D-0234).
"""
