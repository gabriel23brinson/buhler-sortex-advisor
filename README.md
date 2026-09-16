# SORTEX Z+R Bichro Setup Advisor — V1

A Streamlit prototype that analyzes a photographed/screenshot colour map, fits the dominant product distribution, projects an Accept ovoid, and returns machine-specific guidance based on the supplied SORTEX Z+R Bichro manual pages.

## Deploy on Streamlit Community Cloud

1. Create a new GitHub repository.
2. Upload `app.py`, `knowledge.py`, and `requirements.txt` to the repository root.
3. In Streamlit Community Cloud, create a new app from that repo and set the main file to `app.py`.
4. Deploy.

## Use

1. Photograph the current SORTEX Colour Map / Histogram screen as straight-on as possible.
2. Upload the image.
3. Use the four crop sliders to tightly crop the histogram graph.
4. Fill in Front/Rear, Position, Combined/Independent, AND/OR when known.
5. Describe known good product and known defects.
6. Review the projected ovoid and the detailed correction plan.
7. Make only incremental machine changes, capture a new representative frame, and verify sort performance.

## Important V1 limitation

The app can infer histogram geometry from pixels, but a screenshot alone cannot establish which secondary cluster is acceptable product versus defect. The operator must supply/verify product context. This is deliberate: the app should not manufacture certainty about production settings.

## Next upgrade

V2 should add screen auto-detection, OCR of visible settings, explicit detection of current ovoid/perimeters/rectangles, side-by-side CURRENT vs PROPOSED maps, saved product profiles, and comparison of before/after screenshots.
