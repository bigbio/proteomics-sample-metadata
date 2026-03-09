/**
 * SDRF Interactive Builder
 * Guides users through template selection and generates SDRF files.
 */
(function () {
    'use strict';

    /* ---------------------------------------------------------------
       Constants – step option definitions
       --------------------------------------------------------------- */
    var TECHNOLOGY_OPTIONS = [
        { id: 'ms-proteomics', label: 'MS-based Proteomics', desc: 'Mass spectrometry experiments (DDA, DIA, PRM, SRM)' },
        { id: 'affinity-proteomics', label: 'Affinity-based Proteomics', desc: 'Protein-level assays (Olink, SomaScan)' }
    ];

    var ORGANISM_OPTIONS = [
        { id: 'human', label: 'Human', desc: 'Homo sapiens \u2014 adds ancestry, age, sex columns' },
        { id: 'vertebrates', label: 'Other Vertebrate', desc: 'Mouse, rat, zebrafish, etc. \u2014 adds strain, developmental stage' },
        { id: 'invertebrates', label: 'Invertebrate', desc: 'Drosophila, C. elegans, insects \u2014 adds strain, developmental stage' },
        { id: 'plants', label: 'Plant', desc: 'Arabidopsis, crops \u2014 adds cultivar, growth conditions' },
        { id: null, label: 'Skip', desc: 'No organism-specific columns needed' }
    ];

    var MS_EXPERIMENT_OPTIONS = [
        { id: 'dia-acquisition', label: 'DIA', desc: 'Data-independent acquisition \u2014 adds isolation window columns' },
        { id: 'single-cell', label: 'Single-cell', desc: 'Single-cell proteomics \u2014 adds cell-level annotations' },
        { id: 'crosslinking', label: 'Crosslinking MS', desc: 'XL-MS \u2014 adds crosslinker chemistry columns' },
        { id: 'immunopeptidomics', label: 'Immunopeptidomics', desc: 'MHC-bound peptides \u2014 adds HLA/MHC typing' },
        { id: 'metaproteomics', label: 'Metaproteomics', desc: 'Microbial communities \u2014 adds environment metadata' }
    ];

    var AFFINITY_OPTIONS = [
        { id: 'olink', label: 'Olink', desc: 'Proximity Extension Assay (PEA)' },
        { id: 'somascan', label: 'SomaScan', desc: 'Aptamer-based proteomics' },
        { id: null, label: 'Generic', desc: 'Other affinity platform \u2014 base columns only' }
    ];

    /* ---------------------------------------------------------------
       Application state
       --------------------------------------------------------------- */
    var state = {
        technology: null,
        organism: null,
        experiments: [],
        affinitySubtype: null,
        extraColumns: [],      // columns from sdrf-terms.tsv added by user
        addedOptionals: [],    // optional template columns the user opted into
        removedColumns: [],    // recommended columns the user explicitly removed
        factorValues: []       // characteristics chosen as factor values
    };

    var builderData = null;

    /* ---------------------------------------------------------------
       Helpers
       --------------------------------------------------------------- */

    function classifyColumn(name) {
        if (name === 'source name' || name.indexOf('characteristics[') === 0) {
            return 'sample-col';
        }
        if (name.indexOf('factor value[') === 0) {
            return 'factor-col';
        }
        return 'data-col';
    }

    function showStep(id) {
        var el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
    }

    function hideStep(id) {
        var el = document.getElementById(id);
        if (el) el.classList.add('hidden');
    }

    function scrollTo(id) {
        var el = document.getElementById(id);
        if (el) {
            setTimeout(function () {
                el.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 120);
        }
    }

    /* ---------------------------------------------------------------
       Combination rules
       --------------------------------------------------------------- */

    function isDisabledByRules(templateId) {
        if (!builderData || !builderData.combination_rules) return null;
        var groups = builderData.combination_rules.mutually_exclusive;
        if (!groups) return null;
        for (var i = 0; i < groups.length; i++) {
            var group = groups[i];
            var members = group.templates || group;
            if (members.indexOf(templateId) === -1) continue;
            // check if another member is already selected
            for (var j = 0; j < members.length; j++) {
                var m = members[j];
                if (m === templateId) continue;
                if (state.experiments.indexOf(m) !== -1) {
                    return group.reason || ('Cannot combine with ' + m);
                }
            }
        }
        return null;
    }

    /* ---------------------------------------------------------------
       Organism-specific example overrides
       --------------------------------------------------------------- */
    var ORGANISM_EXAMPLES = {
        'human': {
            'characteristics[organism]': 'Homo sapiens',
            'characteristics[organism part]': 'liver',
            'characteristics[cell type]': 'hepatocyte'
        },
        'vertebrates': {
            'characteristics[organism]': 'Mus musculus',
            'characteristics[organism part]': 'brain',
            'characteristics[cell type]': 'neuron'
        },
        'invertebrates': {
            'characteristics[organism]': 'Drosophila melanogaster',
            'characteristics[organism part]': 'whole organism',
            'characteristics[cell type]': 'not applicable'
        },
        'plants': {
            'characteristics[organism]': 'Arabidopsis thaliana',
            'characteristics[organism part]': 'leaf',
            'characteristics[cell type]': 'not applicable'
        }
    };

    /* ---------------------------------------------------------------
       Column resolution
       --------------------------------------------------------------- */

    function resolveColumns() {
        if (!builderData || !state.technology) return [];

        var templateIds = [state.technology];
        if (state.organism) templateIds.push(state.organism);
        if (state.technology === 'ms-proteomics') {
            for (var i = 0; i < state.experiments.length; i++) {
                templateIds.push(state.experiments[i]);
            }
        }
        if (state.technology === 'affinity-proteomics' && state.affinitySubtype) {
            templateIds.push(state.affinitySubtype);
        }

        // Collect ALL template columns (for picker) and build resolved column set
        var allColMap = {};   // all columns from templates (for picker reference)
        var allColOrder = [];
        for (var t = 0; t < templateIds.length; t++) {
            var tid = templateIds[t];
            var tmpl = builderData.templates[tid];
            if (!tmpl || !tmpl.columns) continue;
            for (var c = 0; c < tmpl.columns.length; c++) {
                var col = tmpl.columns[c];
                if (!allColMap[col.name]) {
                    allColOrder.push(col.name);
                }
                allColMap[col.name] = col;
            }
        }

        // Store full template column map for the picker to use
        resolveColumns._allTemplateColumns = allColMap;
        resolveColumns._allTemplateOrder = allColOrder;

        // Build result: required/recommended by default, optional only if user opted in
        var result = [];
        for (var k = 0; k < allColOrder.length; k++) {
            var colName = allColOrder[k];
            var col2 = allColMap[colName];
            var req = col2.requirement || 'optional';
            if (req === 'optional') {
                // Only include if user explicitly added it
                if (state.addedOptionals.indexOf(colName) === -1) continue;
            } else if (req === 'recommended') {
                // Exclude if user explicitly removed it
                if (state.removedColumns.indexOf(colName) !== -1) continue;
            }
            result.push(col2);
        }

        // Append extra columns from terms
        for (var e = 0; e < state.extraColumns.length; e++) {
            var extraName = state.extraColumns[e];
            var alreadyIn = false;
            for (var r = 0; r < result.length; r++) {
                if (result[r].name === extraName) { alreadyIn = true; break; }
            }
            if (!alreadyIn) {
                var termInfo = findTerm(extraName);
                result.push({
                    name: extraName,
                    description: termInfo ? termInfo.description : '',
                    example_value: termInfo ? (termInfo.example_value || '') : '',
                    requirement: 'optional',
                    source_template: 'user'
                });
            }
        }

        // Apply organism-specific example overrides (shallow copy to avoid mutating JSON)
        var orgExamples = state.organism ? ORGANISM_EXAMPLES[state.organism] : null;
        if (orgExamples) {
            for (var oe = 0; oe < result.length; oe++) {
                if (orgExamples[result[oe].name]) {
                    var copy = {};
                    for (var key in result[oe]) {
                        copy[key] = result[oe][key];
                    }
                    copy.example_value = orgExamples[result[oe].name];
                    result[oe] = copy;
                }
            }
        }

        // Build factor value columns
        var factorCols = [];
        for (var fv = 0; fv < state.factorValues.length; fv++) {
            var charName = state.factorValues[fv]; // e.g. "characteristics[disease]"
            var bare = charName.replace(/^characteristics\[/, '').replace(/\]$/, '');
            var fvName = 'factor value[' + bare + ']';
            // Find matching characteristics column for example value
            var fvExample = '';
            for (var fx = 0; fx < result.length; fx++) {
                if (result[fx].name === charName) {
                    fvExample = result[fx].example_value || '';
                    break;
                }
            }
            factorCols.push({
                name: fvName,
                description: 'Experimental variable: ' + bare,
                example_value: fvExample,
                requirement: 'required',
                source_template: 'factor'
            });
        }

        // Sort into proper SDRF column order:
        // 1. source name
        // 2. characteristics[...] (sample metadata)
        // 3. assay name, technology type
        // 4. comment[...] (data/method)
        // 5. factor value[...]
        function sdrfOrder(col) {
            var n = col.name;
            if (n === 'source name') return 0;
            if (n.indexOf('characteristics[') === 0) return 1;
            if (n === 'assay name') return 2;
            if (n === 'technology type') return 3;
            if (n.indexOf('comment[') === 0) return 4;
            if (n.indexOf('factor value[') === 0) return 6;
            return 5; // other columns (e.g. extras without prefix)
        }

        // Stable sort: preserve relative order within each group
        var indexed = [];
        for (var si = 0; si < result.length; si++) {
            indexed.push({ col: result[si], idx: si });
        }
        // Add factor columns with indices after result
        for (var fi = 0; fi < factorCols.length; fi++) {
            indexed.push({ col: factorCols[fi], idx: result.length + fi });
        }
        indexed.sort(function (a, b) {
            var oa = sdrfOrder(a.col);
            var ob = sdrfOrder(b.col);
            if (oa !== ob) return oa - ob;
            return a.idx - b.idx;
        });

        var sorted = [];
        for (var sj = 0; sj < indexed.length; sj++) {
            sorted.push(indexed[sj].col);
        }

        return sorted;
    }

    function findTerm(name) {
        if (!builderData || !builderData.terms) return null;
        for (var i = 0; i < builderData.terms.length; i++) {
            if (builderData.terms[i].term === name) return builderData.terms[i];
        }
        return null;
    }

    /* ---------------------------------------------------------------
       Rendering – option cards
       --------------------------------------------------------------- */

    function renderOptionGrid(containerId, options, onSelect, isMulti) {
        var container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';

        for (var i = 0; i < options.length; i++) {
            (function (opt) {
                var card = document.createElement('div');
                card.className = 'option-card';
                card.setAttribute('data-id', opt.id === null ? '__null__' : opt.id);

                var h4 = document.createElement('h4');
                h4.textContent = opt.label;
                card.appendChild(h4);

                var p = document.createElement('p');
                p.textContent = opt.desc;
                card.appendChild(p);

                // column count badge
                if (opt.id && builderData && builderData.templates[opt.id]) {
                    var ownCols = builderData.templates[opt.id].own_columns;
                    if (ownCols && ownCols.length > 0) {
                        var badge = document.createElement('span');
                        badge.className = 'column-count';
                        badge.textContent = '+ ' + ownCols.length + ' columns';
                        card.appendChild(badge);
                    }
                }

                // disabled check
                var reason = isDisabledByRules(opt.id);
                if (reason) {
                    card.classList.add('disabled');
                    var reasonDiv = document.createElement('div');
                    reasonDiv.className = 'disabled-reason';
                    reasonDiv.textContent = reason;
                    card.appendChild(reasonDiv);
                }

                card.addEventListener('click', function () {
                    if (card.classList.contains('disabled')) return;
                    onSelect(opt.id, card, container, isMulti);
                });

                container.appendChild(card);
            })(options[i]);
        }
    }

    /* ---------------------------------------------------------------
       Selection logic
       --------------------------------------------------------------- */

    function selectOption(id, card, container, isMulti) {
        if (isMulti) {
            card.classList.toggle('selected');
        } else {
            var cards = container.querySelectorAll('.option-card');
            for (var i = 0; i < cards.length; i++) {
                cards[i].classList.remove('selected');
            }
            card.classList.add('selected');
        }
    }

    function getSelectedIds(container) {
        var ids = [];
        var selected = container.querySelectorAll('.option-card.selected');
        for (var i = 0; i < selected.length; i++) {
            var raw = selected[i].getAttribute('data-id');
            if (raw !== '__null__') ids.push(raw);
        }
        return ids;
    }

    /* ---------------------------------------------------------------
       Step handlers
       --------------------------------------------------------------- */

    function onTechnologySelect(id, card, container) {
        selectOption(id, card, container, false);
        state.technology = id;
        state.experiments = [];
        state.affinitySubtype = null;
        state.addedOptionals = [];
        state.removedColumns = [];
        state.extraColumns = [];
        state.factorValues = [];

        showStep('step-organism');
        renderOptionGrid('organism-options', ORGANISM_OPTIONS, onOrganismSelect, false);

        if (id === 'ms-proteomics') {
            showStep('step-experiment');
            hideStep('step-affinity-subtype');
            renderOptionGrid('experiment-options', MS_EXPERIMENT_OPTIONS, onExperimentSelect, true);
        } else {
            showStep('step-affinity-subtype');
            hideStep('step-experiment');
            renderOptionGrid('affinity-options', AFFINITY_OPTIONS, onAffinitySelect, false);
        }

        scrollTo('step-organism');
        updatePreview();
    }

    function onOrganismSelect(id, card, container) {
        selectOption(id, card, container, false);
        state.organism = id; // null for Skip
        showStep('step-customize');
        showStep('step-factors');
        scrollTo('step-customize');
        updatePreview();
    }

    function onExperimentSelect(id, card, container) {
        selectOption(id, card, container, true);
        state.experiments = getSelectedIds(container);

        // re-render to update disabled states
        var currentSelected = state.experiments.slice();
        renderOptionGrid('experiment-options', MS_EXPERIMENT_OPTIONS, onExperimentSelect, true);
        // restore selections
        var cards = container.querySelectorAll('.option-card');
        for (var i = 0; i < cards.length; i++) {
            var cid = cards[i].getAttribute('data-id');
            if (currentSelected.indexOf(cid) !== -1) {
                cards[i].classList.add('selected');
            }
        }

        showStep('step-customize');
        showStep('step-factors');
        scrollTo('step-customize');
        updatePreview();
    }

    function onAffinitySelect(id, card, container) {
        selectOption(id, card, container, false);
        state.affinitySubtype = id;
        showStep('step-customize');
        showStep('step-factors');
        scrollTo('step-customize');
        updatePreview();
    }

    /* ---------------------------------------------------------------
       Preview table
       --------------------------------------------------------------- */

    function updatePreview() {
        var columns = resolveColumns();
        var downloadBar = document.getElementById('download-bar');
        var previewTable = document.getElementById('preview-table');
        var colStats = document.getElementById('column-stats');
        var downloadInfo = document.getElementById('download-info');

        if (!columns.length) {
            if (downloadBar) downloadBar.classList.add('hidden');
            if (previewTable) previewTable.innerHTML = '';
            if (colStats) colStats.textContent = '';
            return;
        }

        if (downloadBar) downloadBar.classList.remove('hidden');

        // Stats
        var required = 0;
        var optional = 0;
        for (var i = 0; i < columns.length; i++) {
            if (columns[i].requirement === 'required' || columns[i].requirement === 'mandatory') {
                required++;
            } else {
                optional++;
            }
        }
        if (colStats) {
            colStats.textContent = columns.length + ' columns (' + required + ' required, ' + optional + ' optional)';
        }
        if (downloadInfo) {
            downloadInfo.innerHTML = '<strong>Your SDRF template is ready!</strong> ' +
                '<span>' + columns.length + ' columns — download the TSV or open in the editor.</span>';
        }

        // Build table
        if (previewTable) {
            previewTable.innerHTML = '';
            var thead = document.createElement('thead');
            var headerRow = document.createElement('tr');
            headerRow.id = 'preview-header';
            var tbody = document.createElement('tbody');
            var dataRow = document.createElement('tr');
            dataRow.id = 'preview-row';

            for (var j = 0; j < columns.length; j++) {
                var col = columns[j];
                var cls = classifyColumn(col.name);

                var th = document.createElement('th');
                th.className = cls;
                th.textContent = col.name;
                if (col.description) th.title = col.description;
                headerRow.appendChild(th);

                var td = document.createElement('td');
                td.className = cls;
                td.textContent = col.example_value || '';
                dataRow.appendChild(td);
            }

            thead.appendChild(headerRow);
            tbody.appendChild(dataRow);
            previewTable.appendChild(thead);
            previewTable.appendChild(tbody);
        }

        // Enable buttons
        var btnDownload = document.getElementById('btn-download');
        var btnEditor = document.getElementById('btn-editor');
        if (btnDownload) btnDownload.disabled = false;
        if (btnEditor) btnEditor.disabled = false;

        renderColumnPicker(columns);
        renderFactorPicker(columns);
    }

    /* ---------------------------------------------------------------
       Factor value picker
       --------------------------------------------------------------- */

    function renderFactorPicker(columns) {
        var container = document.getElementById('factor-picker');
        if (!container) return;

        // Collect characteristics columns (candidates for factor values)
        var candidates = [];
        for (var i = 0; i < columns.length; i++) {
            var name = columns[i].name;
            if (name.indexOf('characteristics[') === 0 && name.indexOf('factor value[') === -1) {
                candidates.push(columns[i]);
            }
        }

        container.innerHTML = '';

        if (!candidates.length) {
            container.innerHTML = '<p style="color:var(--text-light);font-size:0.9rem;">No characteristics columns available yet.</p>';
            return;
        }

        for (var c = 0; c < candidates.length; c++) {
            (function (col) {
                var bare = col.name.replace(/^characteristics\[/, '').replace(/\]$/, '');
                var chip = document.createElement('button');
                chip.type = 'button';
                chip.className = 'factor-chip';
                if (state.factorValues.indexOf(col.name) !== -1) {
                    chip.classList.add('active');
                }
                chip.textContent = bare;
                if (col.description) chip.title = col.description;

                chip.addEventListener('click', function () {
                    var idx = state.factorValues.indexOf(col.name);
                    if (idx !== -1) {
                        state.factorValues.splice(idx, 1);
                    } else {
                        state.factorValues.push(col.name);
                    }
                    updatePreview();
                });

                container.appendChild(chip);
            })(candidates[c]);
        }
    }

    /* ---------------------------------------------------------------
       Column picker
       --------------------------------------------------------------- */

    function renderColumnPicker(currentColumns) {
        var list = document.getElementById('column-picker-list');
        if (!list || !builderData) return;

        var searchInput = document.getElementById('column-search');
        var filter = searchInput ? searchInput.value.toLowerCase() : '';

        // All template columns (including optionals that aren't in currentColumns)
        var allTmplCols = resolveColumns._allTemplateColumns || {};
        var allTmplOrder = resolveColumns._allTemplateOrder || [];

        // Current included column names
        var includedNames = {};
        for (var i = 0; i < currentColumns.length; i++) {
            includedNames[currentColumns[i].name] = true;
        }

        // Categorize template columns
        var includedGroups = {};   // source_template -> [cols] (required/recommended that are included)
        var includedGroupOrder = [];
        var optionalCols = [];     // optional template columns NOT yet enabled

        for (var o = 0; o < allTmplOrder.length; o++) {
            var colName = allTmplOrder[o];
            var col = allTmplCols[colName];
            var req = col.requirement || 'optional';

            // Apply search filter
            if (filter && colName.toLowerCase().indexOf(filter) === -1 &&
                (!col.description || col.description.toLowerCase().indexOf(filter) === -1)) {
                continue;
            }

            if ((req === 'optional' && !includedNames[colName]) ||
                (req === 'recommended' && state.removedColumns.indexOf(colName) !== -1)) {
                // Optional not enabled, or recommended that user removed -> "optional" section
                optionalCols.push(col);
            } else if (includedNames[colName] && state.extraColumns.indexOf(colName) === -1) {
                // Included from template (not user-added extra)
                var source = col.source_template || 'base';
                if (!includedGroups[source]) {
                    includedGroups[source] = [];
                    includedGroupOrder.push(source);
                }
                includedGroups[source].push(col);
            }
        }

        // Extra columns added by user (from terms, not from template)
        var extraCols = [];
        for (var e = 0; e < state.extraColumns.length; e++) {
            var extraName = state.extraColumns[e];
            if (allTmplCols[extraName]) continue; // It's a template optional, handled above
            if (filter && extraName.toLowerCase().indexOf(filter) === -1) continue;
            for (var ci = 0; ci < currentColumns.length; ci++) {
                if (currentColumns[ci].name === extraName) {
                    extraCols.push(currentColumns[ci]);
                    break;
                }
            }
        }

        // Build a set of bare names from all template columns for dedup
        // e.g. "characteristics[organism]" -> "organism", "comment[data file]" -> "data file"
        var tmplBareNames = {};
        for (var bn = 0; bn < allTmplOrder.length; bn++) {
            var fullName = allTmplOrder[bn];
            tmplBareNames[fullName] = true;
            var match = fullName.match(/^(?:characteristics|comment|factor value)\[(.+)\]$/);
            if (match) tmplBareNames[match[1]] = true;
        }

        // Terms not in any template column (truly new additions)
        var addable = [];
        if (builderData.terms) {
            for (var t = 0; t < builderData.terms.length; t++) {
                var term = builderData.terms[t];
                if (tmplBareNames[term.term]) continue;  // Already a template column (exact or bare name match)
                if (includedNames[term.term]) continue; // Already included as extra
                if (filter && term.term.toLowerCase().indexOf(filter) === -1 &&
                    (!term.description || term.description.toLowerCase().indexOf(filter) === -1)) {
                    continue;
                }
                addable.push(term);
            }
        }

        list.innerHTML = '';

        // ---- Section 1: Included template columns (grouped by source) ----
        for (var g = 0; g < includedGroupOrder.length; g++) {
            var groupName = includedGroupOrder[g];
            var items = includedGroups[groupName];
            if (!items || !items.length) continue;

            var groupDiv = document.createElement('div');
            groupDiv.className = 'column-picker-group';
            var groupTitle = document.createElement('h4');
            groupTitle.textContent = groupName.replace(/-/g, ' ');
            groupDiv.appendChild(groupTitle);

            for (var m = 0; m < items.length; m++) {
                groupDiv.appendChild(renderPickerItem(items[m], true, false));
            }
            list.appendChild(groupDiv);
        }

        // ---- Section 1b: User-added extra columns ----
        if (extraCols.length) {
            var extraDiv = document.createElement('div');
            extraDiv.className = 'column-picker-group';
            var extraTitle = document.createElement('h4');
            extraTitle.textContent = 'Added by you';
            extraDiv.appendChild(extraTitle);
            for (var x = 0; x < extraCols.length; x++) {
                extraDiv.appendChild(renderPickerItem(extraCols[x], false, true));
            }
            list.appendChild(extraDiv);
        }

        // ---- Section 2: Optional template columns (off by default) ----
        if (optionalCols.length) {
            var optDiv = document.createElement('div');
            optDiv.className = 'column-picker-group';
            var optTitle = document.createElement('h4');
            optTitle.textContent = 'Optional template columns';
            optDiv.appendChild(optTitle);

            for (var p = 0; p < optionalCols.length; p++) {
                (function (col) {
                    var item = document.createElement('div');
                    item.className = 'column-picker-item';
                    item.style.cursor = 'pointer';

                    var badge = document.createElement('span');
                    badge.className = 'col-type-badge ' + classifyColumn(col.name);
                    badge.textContent = getColumnTypeLabel(col.name);
                    item.appendChild(badge);

                    var nameSpan = document.createElement('span');
                    nameSpan.className = 'col-name';
                    nameSpan.textContent = col.name;
                    item.appendChild(nameSpan);

                    var srcBadge = document.createElement('span');
                    srcBadge.className = 'col-lock';
                    srcBadge.textContent = col.source_template || '';
                    item.appendChild(srcBadge);

                    var descSpan = document.createElement('span');
                    descSpan.className = 'col-desc';
                    descSpan.textContent = col.description || '';
                    item.appendChild(descSpan);

                    var toggleBtn = document.createElement('button');
                    toggleBtn.className = 'toggle-btn';
                    toggleBtn.type = 'button';
                    item.appendChild(toggleBtn);

                    item.addEventListener('click', function () {
                        var req = col.requirement || 'optional';
                        if (req === 'recommended') {
                            // Re-add: remove from removedColumns
                            var idx = state.removedColumns.indexOf(col.name);
                            if (idx !== -1) state.removedColumns.splice(idx, 1);
                        } else {
                            state.addedOptionals.push(col.name);
                        }
                        updatePreview();
                    });
                    optDiv.appendChild(item);
                })(optionalCols[p]);
            }
            list.appendChild(optDiv);
        }

        // ---- Section 3: Available from sdrf-terms.tsv ----
        if (addable.length) {
            var addDiv = document.createElement('div');
            addDiv.className = 'column-picker-group';
            var addTitle2 = document.createElement('h4');
            addTitle2.textContent = 'Other available columns';
            addDiv.appendChild(addTitle2);

            var showCount = filter ? addable.length : Math.min(addable.length, 20);
            for (var a = 0; a < showCount; a++) {
                (function (term) {
                    var item = document.createElement('div');
                    item.className = 'column-picker-item';
                    item.style.cursor = 'pointer';

                    var badge = document.createElement('span');
                    badge.className = 'col-type-badge ' + classifyColumn(term.term);
                    badge.textContent = getColumnTypeLabel(term.term);
                    item.appendChild(badge);

                    var nameSpan = document.createElement('span');
                    nameSpan.className = 'col-name';
                    nameSpan.textContent = term.term;
                    item.appendChild(nameSpan);

                    var descSpan = document.createElement('span');
                    descSpan.className = 'col-desc';
                    descSpan.textContent = term.description || '';
                    item.appendChild(descSpan);

                    var toggleBtn = document.createElement('button');
                    toggleBtn.className = 'toggle-btn';
                    toggleBtn.type = 'button';
                    item.appendChild(toggleBtn);

                    item.addEventListener('click', function () {
                        state.extraColumns.push(term.term);
                        updatePreview();
                    });
                    addDiv.appendChild(item);
                })(addable[a]);
            }
            if (!filter && addable.length > 20) {
                var moreMsg = document.createElement('p');
                moreMsg.style.cssText = 'font-size:0.8rem;color:var(--text-light);padding:8px 12px;';
                moreMsg.textContent = 'Showing 20 of ' + addable.length + ' — use search to find more';
                addDiv.appendChild(moreMsg);
            }
            list.appendChild(addDiv);
        }
    }

    function renderPickerItem(col, isFromTemplate, isExtra) {
        var isRequired = col.requirement === 'required';
        var isHardLocked = isFromTemplate && isRequired;

        var item = document.createElement('div');
        item.className = 'column-picker-item included' + (isHardLocked ? ' locked' : '');

        var badge = document.createElement('span');
        badge.className = 'col-type-badge ' + classifyColumn(col.name);
        badge.textContent = getColumnTypeLabel(col.name);
        item.appendChild(badge);

        var nameSpan = document.createElement('span');
        nameSpan.className = 'col-name';
        nameSpan.textContent = col.name;
        item.appendChild(nameSpan);

        // Show requirement badge for template columns
        if (isFromTemplate) {
            var reqBadge = document.createElement('span');
            reqBadge.className = 'col-lock';
            reqBadge.textContent = col.requirement || 'optional';
            item.appendChild(reqBadge);
        }

        var descSpan = document.createElement('span');
        descSpan.className = 'col-desc';
        descSpan.textContent = col.description || '';
        item.appendChild(descSpan);

        var toggleBtn = document.createElement('button');
        toggleBtn.className = 'toggle-btn active';
        toggleBtn.type = 'button';

        if (isHardLocked) {
            toggleBtn.disabled = true;
            toggleBtn.style.opacity = '0.4';
            toggleBtn.title = 'Required by template — cannot be removed';
        }
        item.appendChild(toggleBtn);

        // Optional template columns and extra columns can be toggled
        if (!isHardLocked) {
            var colName = col.name;
            item.addEventListener('click', function () {
                if (isExtra) {
                    // Remove from extra
                    var idx = state.extraColumns.indexOf(colName);
                    if (idx !== -1) state.extraColumns.splice(idx, 1);
                } else if (col.requirement === 'recommended') {
                    // Move recommended column to removed list
                    if (state.removedColumns.indexOf(colName) === -1) {
                        state.removedColumns.push(colName);
                    }
                } else {
                    // Toggle optional template column off (remove from addedOptionals)
                    var idx2 = state.addedOptionals.indexOf(colName);
                    if (idx2 !== -1) state.addedOptionals.splice(idx2, 1);
                }
                updatePreview();
            });
            item.style.cursor = 'pointer';
        }

        return item;
    }

    function getColumnTypeLabel(name) {
        if (name === 'source name' || name.startsWith('characteristics[')) return 'sample';
        if (name.startsWith('factor value[')) return 'factor';
        if (name.startsWith('comment[')) return 'method';
        return 'data';
    }

    /* ---------------------------------------------------------------
       Download / Editor
       --------------------------------------------------------------- */

    function downloadTSV() {
        var columns = resolveColumns();
        if (!columns.length) return;

        var headers = [];
        var values = [];
        for (var i = 0; i < columns.length; i++) {
            headers.push(columns[i].name);
            values.push(columns[i].example_value || '');
        }

        var tsv = headers.join('\t') + '\n' + values.join('\t') + '\n';
        var blob = new Blob([tsv], { type: 'text/tab-separated-values;charset=utf-8' });
        var url = URL.createObjectURL(blob);

        var a = document.createElement('a');
        a.href = url;
        a.download = 'sdrf-template.sdrf.tsv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function openInEditor() {
        var columns = resolveColumns();
        if (!columns.length) return;

        var headers = [];
        var values = [];
        for (var i = 0; i < columns.length; i++) {
            headers.push(columns[i].name);
            values.push(columns[i].example_value || '');
        }

        var tsv = headers.join('\t') + '\n' + values.join('\t') + '\n';
        var encoded = btoa(unescape(encodeURIComponent(tsv)));
        window.open('sdrf-editor.html?content=' + encodeURIComponent(encoded));
    }

    /* ---------------------------------------------------------------
       Initialization
       --------------------------------------------------------------- */

    function loadBuilderData() {
        var container = document.getElementById('sdrf-builder');
        if (!container) return;

        fetch('sdrf-builder-data.json')
            .then(function (resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function (data) {
                builderData = data;
                initBuilder();
            })
            .catch(function (err) {
                container.innerHTML =
                    '<p style="color:var(--error);padding:1rem;">Failed to load builder data: ' +
                    err.message + '</p>';
            });
    }

    function initBuilder() {
        renderOptionGrid('technology-options', TECHNOLOGY_OPTIONS, onTechnologySelect, false);

        // Wire up column search
        var searchInput = document.getElementById('column-search');
        if (searchInput) {
            var debounceTimer = null;
            searchInput.addEventListener('input', function () {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function () {
                    var columns = resolveColumns();
                    if (columns.length) renderColumnPicker(columns);
                }, 200);
            });
        }
    }

    /* Expose global handlers for onclick attributes */
    window.downloadTSV = downloadTSV;
    window.openInEditor = openInEditor;

    /* Entry point */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadBuilderData);
    } else {
        loadBuilderData();
    }
})();
