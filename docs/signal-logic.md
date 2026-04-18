# Signal Logic — Per Category

## Food
| Signal | Method | Detects |
|--------|--------|---------|
| Vision | Gemini 2.0 Flash | Damage, mould, open containers, contamination |
| OCR | EasyOCR | Expiry date — flags if expired or within 48h |
| Weight | Open Food Facts API | Anomaly if actual weight 20%+ off expected |

**Routing:** Safe + not expired + no anomaly → Reuse. Any failure → Recycle. <70% confidence → FLAG.

## Clothing
| Signal | Method | Detects |
|--------|--------|---------|
| Vision | Gemini 2.0 Flash | Condition score 0–100, tears, stains, brand, completeness |

**Routing:** Score ≥70 → Resale. Score 40–69 → Reuse. Score <40 → Recycle. <70% confidence → FLAG.

## Electronics
| Signal | Method | Detects |
|--------|--------|---------|
| Vision | Gemini 2.0 Flash | Screens, burn marks, water damage, functional probability |
| OCR | EasyOCR | Model number from label |
| Recall | CPSC public API | Recalled or hazardous products |

**Routing:** Recalled → Recycle (always). Functional ≥75% → Resale. 40–74% → Reuse. <40% → Recycle.
