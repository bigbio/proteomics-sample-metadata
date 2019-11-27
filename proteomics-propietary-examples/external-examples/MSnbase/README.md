The [`MSnbase`](http://lgatto.github.io/MSnbase/) data, whether raw or
quantitative, is rouglhy composed of 3 main sub-parts, namely

- an assay, that contains the actual data as spectra or chromatograms
  (for raw data) or a matrix with quantitative values (for
  quantitative data);

- a feature metadata table that contains annotation for each feature
  in the assay data;

- a sample metadata table that contain annotations for each sample in
  the assay data. This typically corresponds to the **experimental
  design**. (The strict definition of sample whan it comes to raw data
  is less well defined, as it might correspond to the number of files,
  or 6, 10, ... or isobaric labelling).

The figure below illustrated this in the case for quantitative data
for the [`MSnSet`
class](http://lgatto.github.io/MSnbase/reference/MSnSet-class.html):

![MSnSet class (simplified)](./msnset.png)

- There's alse **processing log** slot that records all the processing
  steps. For example:

```
> processingData(e)
- - - Processing information - - -
Subset [771,4][483,4] Wed Nov 27 17:41:15 2019
Removed features with more than 0 NAs: Wed Nov 27 17:41:15 2019
Dropped featureData's levels Wed Nov 27 17:41:15 2019
Log transformed (base 2) Wed Nov 27 17:41:15 2019
Normalised (quantiles): Wed Nov 27 17:41:34 2019
 MSnbase version: 2.12.0
```

- MS-specific parameters can be stored in the
  [MIAPE](http://lgatto.github.io/MSnbase/reference/MIAPE-class.html)
  slot.

For more details, please visit the `MSnbase` web page
(http://lgatto.github.io/MSnbase/index.html) or ask questions opening
an issue in this repo.
