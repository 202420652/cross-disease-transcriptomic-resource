# Survival data dictionary (TCGA-derived layer)

| field | definition |
|---|---|
| endpoint | overall survival (OS) |
| event | death; `OS_STATUS` containing DECEASED is coded 1, all other values 0 |
| time | `OS_MONTHS`, months from diagnosis to death or last follow-up |
| censoring | patients alive at last follow-up are censored at `OS_MONTHS` |
| exclusions | records with non-finite or non-positive time |
| covariates | age (`AGE`, years, continuous) and pathological stage collapsed to I-IV (`PATH_STAGE`, falling back to `CLINICAL_STAGE`) |
| missing data | multivariable models are fitted on complete cases only (age and stage non-missing); the excluded count is reported in the model table |
| module score | mean over module members of the per-gene z-score across patients within the context (log2(x+1) values, z-scored per gene, averaged per patient, then averaged across members present; at least two members required) |
| feature scaling | each module score is z-scored before model fitting, so hazard ratios are per 1 SD |
| models | univariable Cox; age-plus-stage adjusted Cox; proportional hazards checked with scaled Schoenfeld residuals (cox.zph) |
| software | R 4.4.1 with survival 3.8.3 |
| data version | cBioPortal releases retrieved 2026-09 (luad_tcga_gdc, coadread_tcga_pan_can_atlas_2018, stad_tcga_gdc, paad_tcga_gdc, lihc_tcga_pan_can_atlas_2018, esca_tcga_gdc) |
| oesophageal subset | restricted to squamous histology (96 patients; 94 with survival data); mutation denominator corrected from 185 mixed-histology profiles to the 96 squamous profiles |
