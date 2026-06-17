from flask import Flask, request, jsonify, send_from_directory
import os
import base64
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM = """You are ArchSci — the world's most advanced AI assistant for archaeological science. You have deep expert knowledge in ALL areas of archaeology:
- Archaeometry: pXRF, XRF, ICP-MS, SEM-EDS, XRD, FTIR, isotope analysis, ceramic petrology, provenance
- Dating: radiocarbon C14, TL, OSL, dendrochronology, archaeomagnetism
- Zooarchaeology: NISP, MNI, taphonomy, mortality profiles, seasonality, butchery
- Archaeobotany: seeds, pollen, phytoliths, charcoal, crop processing
- Geoarchaeology: sediments, micromorphology, soil formation
- Lithics: reduction sequences, raw materials, use-wear, typology
- Ceramics: typology, fabric, production technology, trade networks
- Archaeometallurgy: smelting, alloy composition, slag analysis, bloomery iron, cast iron, forge welding
- Stratigraphy: Harris Matrix, context interpretation, phasing
- GIS and spatial analysis
- South Asian archaeology: Gandharan, Kushan, Taxila, Pakistan, Hazara region
- Statistics: PCA, cluster analysis, discriminant analysis, Random Forest
When given data — analyse immediately, identify patterns, flag errors, give expert interpretation. When given images — describe what you see archaeologically in full technical detail. Always respond as the world's leading archaeological expert."""

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    history = data.get("history", [])
    image = data.get("image", None)
    if not message and not image:
        return jsonify({"error": "No input"}), 400
    try:
        if image:
            response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role":"system","content":SYSTEM},{"role":"user","content":[{"type":"image_url","image_url":{"url":image}},{"type":"text","text":message or "Analyse this archaeological image in full technical detail."}]}],
                max_tokens=2000
            )
        else:
            messages = [{"role":"system","content":SYSTEM}] + history + [{"role":"user","content":message}]
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=2000
            )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
