#!/bin/bash
export GEMINI_API_KEY="$GEMINI_API_KEY"

# Resuming from Clip 4
python3 marketing/generate_ad.py "Scene 4: Light cyan gradient. A step-by-step checklist generating dynamically on a mobile screen. Green checkmarks physically dropping into place next to 'State License' and 'County Tax'. Text: 'Dynamic Compliance Checklists'. Voiceover: Stay compliant without the headache. Our dynamic checklists map out exactly what licenses and tax registrations you need based on your specific jurisdiction." marketing/hosteva_ad_clip4.mp4

python3 marketing/generate_ad.py "Scene 5: A beautiful dashboard grid showing three different luxury properties (Miami Beach, Aspen, West Hollywood), all displaying a 'Compliant' shield badge. Text: 'Unified Portfolio Management'. Voiceover: Manage your entire portfolio seamlessly. From zoning to final listing, streamline your workflow and maximize your revenue." marketing/hosteva_ad_clip5.mp4

python3 marketing/generate_ad.py "Scene 6: Clean white gradient with the teal Hosteva shield in the center. The 'Get Started' button glows. Text: 'Hosteva: The Intelligent Host. Start Free Today.'. Voiceover: Hosteva. Hosting Compliance, Simplified. Start optimizing your property today." marketing/hosteva_ad_clip6.mp4
