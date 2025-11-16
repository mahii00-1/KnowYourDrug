import streamlit as st
import pandas as pd
from itertools import combinations # Used to easily check all pairs

# --- Drug Interaction Database with Severity Levels ---
DRUG_INTERACTIONS = {
    "Aspirin": {"Warfarin": "Major", "Ibuprofen": "Moderate", "Methotrexate": "Major"},
    "Warfarin": {"Aspirin": "Major", "Ibuprofen": "Major", "Clarithromycin": "Major", "Paracetamol (Acetaminophen)": "Moderate"},
    "Ibuprofen": {"Aspirin": "Moderate", "Warfarin": "Major", "Prednisolone": "Moderate"},
    "Paracetamol (Acetaminophen)": {"Warfarin": "Moderate"},
    # Add other interactions here if needed
}

# --- Full Drug List (Consolidated and Sorted) ---
ALL_DRUGS_SET = set(DRUG_INTERACTIONS.keys()) | set(sum([list(v.keys()) for v in DRUG_INTERACTIONS.values()], []))
ALL_DRUGS_SET.update([
    "Naproxen", "Diclofenac", "Mefenamic acid", "Ketorolac", "Aceclofenac", "Etoricoxib", "Cetirizine",
    "Loratadine", "Fexofenadine", "Levocetirizine", "Diphenhydramine",
    "Chlorpheniramine (CPM)", "Montelukast", "Desloratadine", "Azelastine nasal spray",
    "Xylometazoline nasal spray", "Oxymetazoline nasal spray", "Dextromethorphan",
    "Phenylephrine", "Guaifenesin", "Bromhexine", "Ambroxol", "Pseudoephedrine",
    "Omeprazole", "Pantoprazole", "Esomeprazole", "Rabeprazole", "Ranitidine",
    "Famotidine", "Domperidone", "Ondansetron", "Metoclopramide", "Sucralfate",
    "Activated charcoal", "Loperamide", "ORS (Oral Rehydration Salts)", "Digene antacid",
    "Calcium carbonate antacid", "Simethicone", "Lactulose", "Psyllium husk", "Vitamin C",
    "Multivitamin tablets", "Vitamin B-complex", "Vitamin D3", "Calcium + Vitamin D",
    "Zinc supplements", "Iron + Folic acid", "Magnesium supplements", "Omega-3 (Fish oil)",
    "Probiotics", "Hydrocortisone cream", "Clotrimazole cream", "Terbinafine cream",
    "Ketoconazole cream", "Miconazole ointment", "Neomycin cream", "Fusidic acid ointment",
    "Betamethasone cream", "Silver sulfadiazine", "Calamine lotion", "Benzoyl peroxide",
    "Salicylic acid", "Aloe vera gel", "Zinc oxide ointment", "Antiseptic liquid (Dettol/Savlon)",
    "Amoxicillin", "Amoxicillin + Clavulanic acid", "Azithromycin", "Cefixime", "Cephalexin",
    "Ciprofloxacin", "Levofloxacin", "Doxycycline", "Metronidazole", "Erythromycin",
    "Clarithromycin", "Trimethoprim + Sulfamethoxazole", "Nitrofurantoin", "Clindamycin",
    "Linezolid", "Salbutamol inhaler", "Budesonide inhaler", "Fluticasone inhaler",
    "Ipratropium bromide inhaler", "Formoterol", "Tiotropium", "Metformin", "Glimepiride",
    "Gliclazide", "Sitagliptin", "Dapagliflozin", "Insulin (various)", "Pioglitazone",
    "Linagliptin", "Amlodipine", "Telmisartan", "Losartan", "Atenolol", "Metoprolol",
    "Propranolol", "Ramipril", "Enalapril", "Carvedilol", "Hydrochlorothiazide",
    "Furosemide", "Spironolactone", "Clopidogrel", "Atorvastatin", "Rosuvastatin",
    "Levothyroxine", "Carbimazole", "Progesterone", "Estradiol", "Prednisolone",
    "Povidone iodine", "Hydrogen peroxide", "Sterile saline", "Crepe bandages", "Band-aids",
    "Gauze pads", "Burn gel", "Icepacks", "Gloves", "Thermometer strips", "Hot water bag",
    "Cetirizine + Phenylephrine tablets", "Paracetamol + Caffeine", "Oral contraceptive pills",
    "Pregnancy test kit", "Motion sickness tablets (Dimenhydrinate)", "Melatonin",
    "Antacid chewable tablets", "Nicotine gum", "Lidocaine gel", "B-12 injections",
    "Rehydration electrolyte tablets"
])
ALL_DRUGS = sorted(list(ALL_DRUGS_SET))

# --- Interaction Check Function (Handles Bidirectional Search) ---
def get_interaction_severity(d1, d2):
    # Check d1 against d2
    if d1 in DRUG_INTERACTIONS and d2 in DRUG_INTERACTIONS[d1]:
        return DRUG_INTERACTIONS[d1][d2]
    # Check d2 against d1 (bidirectional check)
    if d2 in DRUG_INTERACTIONS and d1 in DRUG_INTERACTIONS[d2]:
        return DRUG_INTERACTIONS[d2][d1]
    return None

def format_severity_markdown(sev):
    if sev == "Major":
        return "🚨 **MAJOR Risk** 🚨"
    elif sev == "Moderate":
        return "⚠️ **Moderate Risk** ⚠️"
    elif sev == "Minor":
        return "ℹ️ **Minor Risk**"
    return sev

def get_advice(severity):
    if severity == "Major":
        return "🛑 **Action:** Immediately consult a doctor or pharmacist. **DO NOT** take this combination without professional guidance. This is a critical interaction."
    elif severity == "Moderate":
        return "💊 **Action:** Consult a healthcare provider. Dose adjustment or close monitoring may be required. Be aware of increased risk."
    elif severity == "Minor":
        return "✅ **Action:** Generally safe, but monitor for symptoms. Always inform your doctor about all medications."
    return ""

# --- Streamlit UI Layout ---
st.set_page_config(
    page_title="KnowYourDrug Checker",
    page_icon="💊",
    layout="centered"
)

st.markdown("""
    <style>
    h1 {color: #047857; font-weight: 900; text-align: center;}
    .stMultiSelect { font-size: 1.1em; }
    </style>
""", unsafe_allow_html=True)

st.title("KnowYourDrug 💊✨ Checker")
st.markdown("### Check Interactions for Multiple Medications with Severity Levels")

# Drug Selection using Streamlit's multiselect
selected_drugs = st.multiselect(
    label="**Select 2 or more drugs to check for interactions:**",
    options=ALL_DRUGS,
    default=[],
    placeholder="Start typing drug names (e.g., Aspirin, Warfarin)...",
)

st.markdown("---")

# Check Button and Result Display
if st.button("Check Interactions Now", use_container_width=True):
    selected_drugs_unique = list(set(selected_drugs))
    
    if len(selected_drugs_unique) < 2:
        st.warning("Please select at least **two different drugs** to check for interactions.")
    else:
        found_interactions = []
        highest_severity = "None"
        severity_order = {"Major": 3, "Moderate": 2, "Minor": 1, "None": 0}

        # Use itertools.combinations to check every unique pair
        for d1, d2 in combinations(selected_drugs_unique, 2):
            severity = get_interaction_severity(d1, d2)
            
            if severity:
                found_interactions.append({
                    'drug1': d1,
                    'drug2': d2,
                    'severity': severity
                })
                
                # Update highest severity found
                if severity_order[severity] > severity_order[highest_severity]:
                    highest_severity = severity

        if found_interactions:
            st.error(f"### {format_severity_markdown(highest_severity)} Found!")
            st.markdown(get_advice(highest_severity))
            st.markdown("---")

            st.markdown("#### Detailed Interactions:")
            for interaction in found_interactions:
                d1 = interaction['drug1']
                d2 = interaction['drug2']
                sev = interaction['severity']
                
                st.markdown(f"**{format_severity_markdown(sev)}** between **{d1}** and **{d2}**.")

        else:
            st.success("### 💚 All Clear! 💚")
            st.markdown("No major or known interactions detected among the selected drugs in our database.")
            st.info("Remember, this checker uses a limited database. Always consult a healthcare professional.")

st.markdown("---")
st.caption("Disclaimer: This tool is for informational purposes only and is not a substitute for professional medical advice. Always consult a healthcare professional.")