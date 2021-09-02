## Customize Makefile settings for bdscratch
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile


JOBS = CCN202002013 #CCN201912131 CCN201810310 CCN201908211 CCN201908210
GENE_FILES = ensmusg
BDS_BASE = http://www.semanticweb.org/brain_data_standards/

OWL_FILES = $(patsubst %, components/%.owl, $(JOBS))
OWL_CLASS_FILES = $(patsubst %, components/%_class.owl, $(JOBS))
OWL_EQUIVALENT_CLASS_FILES = $(patsubst %, components/%_equivalent_class.owl, $(JOBS))
GENE_FILES = $(patsubst %, mirror/%.owl, $(JOBS))
OWL_MIN_MARKER_FILES = $(patsubst %, components/%_minimal_markers.owl, $(JOBS))
OWL_NOMENCLATURE_FILES = $(patsubst %, components/%_non_taxonomy_classification.owl, $(JOBS))

#DEND_FILES = $(patsubst %, ../dendrograms/%.json, $(JOBS))
#TEMPLATE_FILES = $(patsubst %, ../templates/%.tsv, $(JOBS))
#TEMPLATE_CLASS_FILES = $(patsubst %, ../templates/_%class.tsv, $(JOBS))


$(PATTERNDIR)/pattern.owl: pattern_schema_checks update_patterns
	if [ $(PAT) = true ]; then $(DOSDPT) prototype --prefixes=template_prefixes.yaml --obo-prefixes true --template=$(PATTERNDIR)/dosdp-patterns --outfile=$@; fi

individual_patterns_names_default := $(strip $(patsubst %.tsv,%, $(notdir $(wildcard $(PATTERNDIR)/data/default/*.tsv))))
dosdp_patterns_default: $(SRC) all_imports .FORCE
	if [ $(PAT) = true ] && [ "${individual_patterns_names_default}" ]; then $(DOSDPT) generate --prefixes=template_prefixes.yaml --catalog=catalog-v001.xml --infile=$(PATTERNDIR)/data/default/ --template=$(PATTERNDIR)/dosdp-patterns --batch-patterns="$(individual_patterns_names_default)" --ontology=$< --obo-prefixes=true --outfile=$(PATTERNDIR)/data/default; fi

$(PATTERNDIR)/data/default/%.txt: $(PATTERNDIR)/dosdp-patterns/%.yaml $(PATTERNDIR)/data/default/%.tsv .FORCE
	if [ $(PAT) = true ]; then $(DOSDPT) terms --prefixes=template_prefixes.yaml --infile=$(word 2, $^) --template=$< --obo-prefixes=true --outfile=$@; fi

# adding an extra query step to inject version info to imported entities
imports/%_import.owl: mirror/%.owl imports/%_terms_combined.txt
	if [ $(IMP) = true ]; then $(ROBOT) query  -i $< --update ../sparql/inject-version-info.ru --update ../sparql/preprocess-module.ru \
		extract -T imports/$*_terms_combined.txt --force true --copy-ontology-annotations true --individuals exclude --method BOT \
		query --update ../sparql/inject-subset-declaration.ru --update ../sparql/postprocess-module.ru \
		annotate --ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) --output $@.tmp.owl && mv $@.tmp.owl $@; fi

# hard wiring for now.  Work on patsubst later
mirror/ensmusg.owl: ../patterns/data/bds/ensmusg_data.tsv ../patterns/dosdp-patterns/ensmusg.yaml bdscratch-edit.owl
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then $(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=../patterns/dosdp-patterns/ensmusg.yaml \
        --ontology=bdscratch-edit.owl --obo-prefixes=true --outfile=$@; fi

components/all_templates.owl: $(OWL_FILES) $(OWL_CLASS_FILES) $(OWL_EQUIVALENT_CLASS_FILES) $(OWL_MIN_MARKER_FILES) $(OWL_NOMENCLATURE_FILES)
	$(ROBOT) merge $(patsubst %, -i %, $^) \
	 --collapse-import-closure false \
	 annotate --ontology-iri ${BDS_BASE}$@  \
	 convert -f ofn	 -o $@

#(SRC): $(OWL_FILES)
#	$(ROBOT) merge -i pcl-template.owl $(patsubst %, -i %, $^) --collapse-import-closure false -o $@

components/%.owl: ../templates/%.tsv bdscratch-edit.owl
	$(ROBOT) template --input bdscratch-edit.owl --template $< \
    		--add-prefixes template_prefixes.json \
    		annotate --ontology-iri ${BDS_BASE}$@ \
    		convert --format ofn --output $@

components/%_class.owl: ../patterns/data/bds/%_class.tsv bdscratch-edit.owl ../patterns/dosdp-patterns/taxonomy_class.yaml bdscratch-edit.owl
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=../patterns/dosdp-patterns/taxonomy_class.yaml \
        --ontology=bdscratch-edit.owl --obo-prefixes=true --outfile=$@

components/%_equivalent_class.owl: ../patterns/data/bds/%_equivalent_reification.tsv ../patterns/dosdp-patterns/taxonomy_equivalent_class.yaml bdscratch-edit.owl
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=../patterns/dosdp-patterns/taxonomy_equivalent_class.yaml \
        --ontology=bdscratch-edit.owl --obo-prefixes=true --outfile=$@

components/%_minimal_markers.owl: ../patterns/data/bds/%_minimal_markers.tsv ../patterns/dosdp-patterns/taxonomy_minimal_markers.yaml bdscratch-edit.owl
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=../patterns/dosdp-patterns/taxonomy_minimal_markers.yaml \
        --ontology=bdscratch-edit.owl --obo-prefixes=true --outfile=$@

components/%_non_taxonomy_classification.owl: ../patterns/data/bds/%_non_taxonomy_classification.tsv ../patterns/dosdp-patterns/taxonomy_non_taxonomy_classification.yaml bdscratch-edit.owl
	$(DOSDPT) generate --catalog=catalog-v001.xml --prefixes=template_prefixes.yaml \
        --infile=$< --template=../patterns/dosdp-patterns/taxonomy_non_taxonomy_classification.yaml \
        --ontology=bdscratch-edit.owl --obo-prefixes=true --outfile=$@

