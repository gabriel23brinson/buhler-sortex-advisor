MANUAL_RULES = {
    "axes": [
        "Colour 1 is plotted on the horizontal axis and Colour 2 on the vertical axis.",
        "Colour 1 is the lower-frequency camera channel; Colour 2 is the higher-frequency channel.",
        "The channels may be visible-spectrum or infrared; do not interpret Colour 1/2 as literal product colours without camera context.",
    ],
    "histogram": [
        "Histogram position represents Colour 1/Colour 2 response, not chute position.",
        "Histogram display colour/shading represents frequency of occurrence, not the physical colour of the product.",
        "The acceptable product is normally the most frequently recorded group.",
        "A bright compact region near the background response may be background rather than product and should not automatically drive the Accept space.",
    ],
    "classes": [
        "Accept Class represents acceptable product. It may extend toward background to include acceptable edge pixels.",
        "General Defect Class is the normal flexible defect class; up to four may be defined.",
        "Spot Defect Class behaves similarly but has a maximum defect-size limitation; up to two spot classes may be defined.",
        "FM Defect Class covers colour-map areas outside operator-defined colour spaces and background colour space.",
        "Configuration may use one Accept + two Spot classes or two Accept + one Spot class.",
    ],
    "geometry": [
        "Accept product is commonly enclosed by an ovoid around the dominant good-product distribution.",
        "Perimeters extend from an ovoid to identify defect regions and may be separated from Accept depending on colour separation and defect size.",
        "Sensitivity changes the effective size/range of a defect colour space; do not use sensitivity as a substitute for correcting a badly placed base colour space.",
    ],
    "views": [
        "OR sorting rejects when a configured defect is seen by either Front or Rear camera.",
        "AND sorting can require selected classes to be seen by Front and Rear simultaneously before rejection.",
        "Combined view uses identical front/rear mode parameters; Independent view allows them to be set separately.",
    ],
    "capture": [
        "Quick Frame captures immediately.",
        "Line Triggered waits for a trigger condition on a scan line.",
        "Block Triggered evaluates a 64-line region and, when triggered, capture continues to 512 lines.",
        "Product Only captures scans containing presence/product rather than background.",
        "A scan comprises 1024 pixels. Trigger Threshold is a pixel count; an excessively high threshold can prevent capture.",
        "Triggered capture times out after 120 seconds if the selected condition does not occur.",
    ],
    "prefilter": [
        "Object Separation pre-filter options include None, Separation, Erosion, Sieve and Secondary Stalk.",
        "Separation, Erosion and Sieve may use disc or square erosion filters; Secondary Stalk uses a square erosion filter.",
        "Frame Capture can be used to inspect the simulated effect of object-separation processing on real product.",
    ],
    "workflow": [
        "Colour Map Setup, Sensitivity, Defect Size, Defect Propagation and Ejector Delay are closely related; diagnose the subsystem before changing parameters.",
        "Use a representative sample containing normal product and expected defects before validating a setup.",
        "After a proposed adjustment, capture another representative frame and verify accept/reject separation before production use.",
    ],
}


def flattened_rules():
    out = []
    for section, rules in MANUAL_RULES.items():
        for rule in rules:
            out.append((section, rule))
    return out
