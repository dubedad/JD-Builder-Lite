# OaSIS HTML Reference

This file contains the actual HTML from the OaSIS site for reference during UI implementation.

**Source:** https://noc.esdc.gc.ca/OaSIS/OaSISOccProfile?code=21211.00&version=2025.0
**Captured:** 2026-01-24

---

## Key CSS/Framework Dependencies

```html
<!-- Canada.ca Design System (CDTS) -->
<link rel="stylesheet" href="https://www.canada.ca/etc/designs/canada/cdts/gcweb/v5_0_2/cdts/cdts-styles.css">

<!-- WET (Web Experience Toolkit) -->
<script src="https://www.canada.ca/etc/designs/canada/cdts/gcweb/v5_0_2/cdts/compiled/wet-en.js"></script>

<!-- Font Awesome -->
<link href='/_content/LMI-IMT.Applications.RazorComponents/lib/fontawesome/css/all.min.css' rel='stylesheet' />

<!-- OaSIS Custom Styles -->
<link href='/css/Common.css' rel='stylesheet' />
<link href='/css/OaSIS.css?v=1' rel='stylesheet' />
```

---

## SEARCH BAR COMPONENT

### Pill Toggle Buttons (Keyword/Code/Competency)

```html
<ul id="searchSections" role="tablist" class="nav nav-pills noPad oaSISNav ignoreTabStyle"
    style="display:grid;width:100%;height:100%;border:none!important;padding:5px;">

    <li tabindex="0" role="tab" id="tab-keyword"
        class="oasisQuickSearchLiPill tab-buttonSearch ignoreTabStyle SearchByKeywordSection tabpanel-keyword">
        <span class="customNavOasis" id="KeywordSection"
              style="border-radius:25px; cursor: pointer; padding:7px 10px;">
            Keyword
        </span>
    </li>

    <li tabindex="0" role="tab" id="tab-code"
        class="oasisQuickSearchLiPill tab-buttonSearch ignoreTabStyle SearchByKeywordSection tabpanel-code">
        <span class="customNavOasis" id="CodeSection"
              style="border-radius:25px; cursor: pointer; padding:7px 10px;">
            Code
        </span>
    </li>
</ul>
```

**Key Styles:**
- `border-radius: 25px` - pill shape
- `padding: 7px 10px` - internal spacing
- Active state via `tab-button-active` class

### Search Input with Button

```html
<div class="input-group col-xs-12 no-pad">
    <input type="text" class="form-control w100"
           id="KeywordSearchText" name="keywordSearchText"
           placeholder="Example: Judge" value=""
           required="required" minlength="3" maxlength="200" />
    <div class="input-group-btn" style="position: relative; font-size: 0; white-space: nowrap;">
        <button type="submit" class="btn btn-primary w100" value="Search">Search</button>
    </div>
</div>
```

**Key Classes:**
- `input-group` - Bootstrap input group
- `form-control` - Bootstrap form styling
- `btn btn-primary` - Primary action button (dark blue)

### Version Display

```html
<div style="padding:0;display:inline-block;">
    <dl>
        <dt style="float:left">Version:</dt>
        <dd style="float:left;margin-left:15px;">OaSIS 2025 Version 1.0</dd>
    </dl>
</div>
```

---

## PROFILE HEADER (Blue Banner)

```html
<div class="extend-banner blueBG">
    <div class="row wb-eqht-grd">
        <div class="col-md-8 col-sm-12 hght-inhrt">
            <h2 property="name" class="mrgn-bttm-md h1">Data scientists</h2>
            <span class="oasis-code-badge mrgn-bttm-md" aria-label="OaSIS code" role="definition">21211.00</span>
            <p class="mrgn-tp-md mrgn-bttm-lg">
                Data scientists use advanced analytics technologies...
            </p>
        </div>
        <div class="col-md-4 hidden-xs hidden-sm hght-inhrt text-center">
            <span class="fa-9x fas fa-atom" style="margin: auto; color: #CADBF2;"></span>
        </div>
    </div>
</div>
```

**Key Classes:**
- `extend-banner` - Full-width banner
- `blueBG` - Blue background color
- `oasis-code-badge` - NOC code badge styling
- `wb-eqht-grd` - WET equal height grid

---

## TAB NAVIGATION

```html
<ul class="tabs-bar-lg" id="header-Datascientists" role="tablist"
    style="list-style:none;padding:0;margin:0;width:100%;display:flex;flex-wrap:wrap;
           grid-row-gap:5px;grid-column-gap:10px;position:relative;top:1px;">

    <li style="flex-grow:1;" role="tab" aria-selected="false">
        <a style="justify-content:center;padding:0;cursor:pointer;"
           role="none presentation"
           onclick="ResetTab(); SwitchTab('overview');"
           class="tab-button tab-button-active profileTabStyle"
           data-tab-id="overview">
            <span>Overview</span>
        </a>
    </li>

    <li style="flex-grow:1;" role="tab" aria-selected="false">
        <a style="justify-content:center;padding:0;cursor:pointer;"
           class="tab-button profileTabStyle"
           data-tab-id="workCharacteristics">
            <span>Work characteristics</span>
        </a>
    </li>
    <!-- More tabs... -->
</ul>
```

**Tab Names:**
1. Overview
2. Work characteristics
3. Skills and abilities
4. Interests
5. Employment requirements
6. Skills for Success

---

## PANEL CARDS

```html
<div class="panel panel-default panel-vertical" tabindex="0">
    <div class="panel-heading">
        <span class="center-block panel-heading-background-grey"></span>
        <span class="fas fa-project-diagram fa-2x PaddingRight"></span>
        <h3>Also known as</h3>
    </div>
    <div class="panel-body">
        <!-- Content here -->
    </div>
</div>
```

**Key Classes:**
- `panel panel-default panel-vertical` - Card container
- `panel-heading` - Card header with icon
- `panel-body` - Card content area

---

## PROFICIENCY LEVEL CIRCLES

```html
<div class="col-xs-12">
    <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>  <!-- filled -->
    <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>  <!-- filled -->
    <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>  <!-- filled -->
    <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>  <!-- filled -->
    <span class="mrgn-rght-sm scale-option-circle fa-circle far"></span>  <!-- empty -->
    <span>4 - High Level</span>
</div>
```

**Circle Classes:**
- `fa-circle fas` - Filled circle (Font Awesome solid)
- `fa-circle far` - Empty circle (Font Awesome regular/outline)
- `scale-option-circle` - Custom OaSIS styling
- `mrgn-rght-sm` - Right margin spacing

**Level Scale:**
- 1 - Lowest Level: ●○○○○
- 2 - Low Level: ●●○○○
- 3 - Moderate Level: ●●●○○
- 4 - High Level: ●●●●○
- 5 - Highest Level: ●●●●●

---

## NOC HIERARCHY BREAKDOWN

```html
<div class="panel-body mrgn-bttm-lg">
    <h4>NOC version</h4>
    <span>NOC 2021 Version 1.0</span>

    <h4>Broad occupational category</h4>
    <a class="displayBlock" href="/OASIS/OaSISHierarchy?code=2&version=2025.0">
        2 – Natural and applied sciences and related occupations
    </a>

    <h4>TEER</h4>
    <span>1 – Occupations usually require a university degree</span>

    <h4>Major group</h4>
    <a class="displayBlock" href="...">21 – Professional occupations in natural and applied sciences</a>

    <h4>Sub-major group</h4>
    <a class="displayBlock" href="...">212 – Professional occupations in applied sciences</a>

    <h4>Minor group</h4>
    <a class="displayBlock" href="...">2121 – Mathematicians, statisticians, actuaries and data scientists</a>

    <h4>Unit group</h4>
    <a class="displayBlock" href="...">21211 – Data scientists</a>

    <h4>Occupational profile</h4>
    <span>21211.00 – Data scientists</span>
</div>
```

---

## WORK ACTIVITIES TABLE

```html
<div class="col-xs-12 wb-eqht-grd noPad">
    <div class="hght-inhrt pad10 OasisdescriptorRatingCell"></div>
    <div class="hght-inhrt bold pad10 backgroundColorLightBlue OasisdescriptorRatingCell">
        Proficiency or complexity level
    </div>
</div>

<div class="col-xs-12 wb-eqht-grd noPad">
    <div class="pad10 hght-inhrt OasisdescriptorRatingCell">Analyzing Data or Information</div>
    <div class="pad10 hght-inhrt backgroundColorLightBlue OasisdescriptorRatingCell">
        <div class="col-xs-12">
            <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>
            <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>
            <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>
            <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>
            <span class="mrgn-rght-sm scale-option-circle fa-circle fas"></span>
            <span>5 - Highest Level</span>
        </div>
    </div>
</div>
```

**Key Classes:**
- `OasisdescriptorRatingCell` - Table cell styling
- `backgroundColorLightBlue` - Light blue background for level column
- `wb-eqht-grd` - Equal height grid row

---

## SEE MORE / EXPAND BUTTONS

```html
<button class="see-more-btn btn btn-default" type="button" onclick="ToggleAllJobTitles()">
    <span id="IndexTitlesSeeMore">See more</span>
    <span id="IndexTitlesSeeLess" style="display:none">See less</span>
    – Job titles
</button>
```

---

## COLOR PALETTE (from observed styles)

- **Blue Header Background:** `blueBG` class (dark navy blue ~#003366)
- **Light Blue Cell Background:** `backgroundColorLightBlue` class
- **Icon Color in Banner:** `#CADBF2` (light blue)
- **Panel Heading Background:** `panel-heading-background-grey`
- **Primary Button:** `btn-primary` (Bootstrap blue)

---

## UTILITY CLASSES USED

- `mrgn-bttm-md` - Margin bottom medium
- `mrgn-tp-md` - Margin top medium
- `mrgn-lft-md` - Margin left medium
- `mrgn-rght-sm` - Margin right small
- `noPad` / `no-pad` - No padding
- `pad10` - 10px padding
- `hght-inhrt` - Height inherit
- `displayBlock` - Display block
- `w100` - Width 100%
- `col-xs-12`, `col-md-8`, etc. - Bootstrap grid

---

## FONTS

Uses system fonts via Canada.ca Design System (no custom fonts needed).

---

## IMPLEMENTATION NOTES

1. **We can't directly hotlink** to canada.ca CSS/JS - need to recreate styles locally
2. **Font Awesome** is used for icons - we can use this
3. **Bootstrap-based** grid system - compatible with our stack
4. **WET framework** provides accessibility features - we should match the patterns
5. **Pill buttons** use simple border-radius and padding
6. **Proficiency circles** use Font Awesome `fa-circle` with fas/far variants

---

## SEARCH RESULTS PAGE HTML

**Source:** https://noc.esdc.gc.ca/OaSIS/OaSISSearchResult?searchType=Keyword&searchText=pilot&version=2025.0

### Page Title Structure

```html
<h1 property="name" id="wb-cont">OaSIS - Search results
    <span>- Pilot</span>
</h1>
```

### Filter Items Section

```html
<h2 class="h4">Filter items</h2>
<div id="filterOptions" class="form-group">
    <details class="chkbxrdio-grp on">
        <summary class="wb-toggle chkbxrdio-grp" tabindex="0">
            Broad occupational category
        </summary>
        <fieldset>
            <legend style="display: none;"></legend>
            <div class="checkbox BOC">
                <label for="BOC1">
                    <input type="checkbox" name="BOCFilters" value="..." id="BOC1" />
                    Business, finance and administration occupations
                </label>
            </div>
            <!-- More checkboxes... -->
        </fieldset>
    </details>
</div>
```

### Sort By Dropdown

```html
<label for="sortingOptionsSelect" class="h4 mrgn-tp-md">Sort by:</label>
<div id="sortingOptions" class="form-group noPad">
    <div class="col-xs-6 col-sm-6 col-md-6 mrgn-bttm-lg noPad">
        <select id="sortingOptionsSelect" class="form-control" style="width: 100%; height: 46px;">
            <option value="1" data-name="Title" data-direction="asc">Label - A to Z</option>
            <option value="2" data-name="Title" data-direction="desc">Label - Z to A</option>
            <option value="3" data-name="ProfileName" data-direction="asc">Code - Ascending</option>
            <option value="4" data-name="ProfileName" data-direction="desc">Code - Descending</option>
            <option value="5" selected>Matching search criteria</option>
        </select>
    </div>
    <div class="col-xs-6 col-sm-6 col-md-6 noPad">
        <button type="button" id="btToggleDisplay" class="form-control btn-default" title="Grid view">
            <span id="btToggleDisplayLabel">Grid view</span>
            <span id="icon" class="toggleIcon" title="Grid view">
                <i class="fa fa-th-list" aria-hidden="true"></i>
            </span>
        </button>
    </div>
</div>
```

### Results Table Structure (Cards Mode)

```html
<table id="OaSISSearchResultsTable" class="cards wb-tables table draftLayout"
       data-wb-tables='{ "paging":"true", "info":"true", "aaSorting": [],
                         "lengthMenu": [[9, 18, 36, 54, -1], [9, 18, 36, 54, "All"]]}'>
    <thead class="hideTableHeader">
        <tr class="eqht-trgt">
            <th id="AlphaHeader" style="display:none">Alpha</th>
            <th id="TitleHeader" style="display:none">Title</th>
            <th id="ProfileNameHeader" class="col-sm-2">OaSIS profile</th>
            <th id="BOCHeader" class="col-sm-2">Broad occupational category</th>
            <th id="TEERHeader" class="col-sm-3">Training, Education, Experience...</th>
            <th id="LeadHeader" class="col-sm-3">Lead statement</th>
            <th id="SourceHeader" class="col-sm-2">Matching search criteria</th>
            <th id="ScoreHeader" style="display:none">Score</th>
        </tr>
    </thead>
    <tbody class="wb-eqht mrgn-tp-lg no-border">
        <!-- Card rows here -->
    </tbody>
</table>
```

### Single Card Row HTML

```html
<tr class="eqht-trgt cardsTr">
    <!-- Hidden columns for sorting -->
    <td style="display:none;">A</td>
    <td style="display:none;">air pilots</td>

    <!-- OaSIS Profile (clickable link) -->
    <td class="bottomPadding">
        <span class="cardsheader">
            <a href="/OASIS/OASISOccProfile?code=72600.01&version=2025.0">
                72600.01 – Air pilots
            </a>
        </span>
    </td>

    <!-- Broad Occupational Category -->
    <td class="topPadding mrgn-lft-sm mrgn-tp-md">
        <i class="fa fa-truck short OaSISIconTopCorrected" aria-hidden="true"></i>
        <span class="OaSISCardTDTextStyle">
            Trades, transport and equipment operators and related occupations
        </span>
    </td>

    <!-- TEER -->
    <td class="topPadding mrgn-lft-sm mrgn-tp-md">
        <i class="fa fa-bookmark short OaSISIconTopCorrected" aria-hidden="true"></i>
        <span class="noFontStyle OaSISCardTDTextStyle">
            Occupations usually require a college diploma or apprenticeship training...
        </span>
    </td>

    <!-- Lead Statement -->
    <td class="topPadding mrgn-lft-sm mrgn-tp-md mrgn-bttm-lg">
        <i class="fa fa-book short OaSISIconTopCorrected" aria-hidden="true"></i>
        <div class="OaSISCardTDTextStyle">
            <p style="padding-bottom: 20px;">
                Air pilots fly fixed wing aircraft and helicopters to provide air
                transportation and other services such as crop spraying and aerial surveying.
            </p>
        </div>
    </td>

    <!-- Matching Search Criteria -->
    <td class="topBorder mrgn-lft-sm bottomAnchored OaSISCardTDTextStyle">
        <i class="fa fa-search short OaSISIconTopCorrected" aria-hidden="true"></i>
        <span class="noFontStyle OaSISCardTDTextStyle">
            Matching search criteria
            <span style="font-size: smaller"><br />Label, Job titles</span>
        </span>
    </td>

    <!-- Hidden score column -->
    <td style="display:none;">4</td>
</tr>
```

### Card Icons Used

| Icon | Class | Meaning |
|------|-------|---------|
| Truck | `fa fa-truck` | Trades, transport occupations |
| Pen | `fa fa-pen-alt` | Business, finance occupations |
| Handshake | `fa fa-handshake` | Sales and service occupations |
| Bookmark | `fa fa-bookmark` | TEER (education requirements) |
| Book | `fa fa-book` | Lead statement |
| Search | `fa fa-search` | Matching search criteria |

### Key CSS Classes for Cards

- `cards` - Enables card view mode on table
- `cardsTr` - Card row styling
- `cardsheader` - Card title/link styling
- `OaSISCardTDTextStyle` - Card text content styling
- `OaSISIconTopCorrected` - Icon positioning
- `topPadding` - Top padding for sections
- `topBorder` - Border separator
- `bottomAnchored` - Anchors content to bottom
- `eqht-trgt` - Equal height target (WET framework)
- `wb-eqht` - Equal height container
