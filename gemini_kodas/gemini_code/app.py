from flask import Flask, render_template_string, request, send_file
from google import genai
from google.genai.types import HttpOptions
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from reportlab.lib.utils import simpleSplit



app = Flask(__name__)

# Įterpk savo Gemini API raktą čia
API_KEY = ""

client = genai.Client(api_key=API_KEY, http_options=HttpOptions(api_version="v1"))

# Paprastas HTML su forma ir rezultatu
HTML = """
<!doctype html>
<html lang="lt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vitaminų rekomendacijos</title>
  <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
  <style>
    body {
      font-family: 'Roboto', sans-serif;
      background: #f4f6f8;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .container {
      background: #ffffff;
      padding: 2rem;
      margin-top: 3rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      border-radius: 12px;
      max-width: 700px;
      width: 90%;
    }

    .logo {
      text-align: center;
      font-size: 1.8rem;
      font-weight: bold;
      color: #007BFF;
      margin-bottom: 1rem;
    }

    h2, h3 {
      color: #333;
    }

    textarea, select {
      width: 100%;
      padding: 0.8rem;
      margin-top: 0.5rem;
      margin-bottom: 1rem;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 1rem;
      font-family: inherit;
    }

    button {
      margin-top: 1rem;
      padding: 0.7rem 1.5rem;
      border: none;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.3s;
    }

    #submitBtn:disabled {
      background-color: #cccccc;
      color: #666666;
      cursor: not-allowed;
    }

    #submitBtn:enabled {
      background-color: #007BFF;
      color: white;
    }

    #submitBtn:enabled:hover {
      background-color: #0056b3;
    }

    .result-box {
      background: #e9f7ef;
      padding: 1rem;
      border-radius: 8px;
      margin-top: 1rem;
      border-left: 6px solid #28a745;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 1rem;
      line-height: 1.5;
      color: #333;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">
      <img src="{{ url_for('static', filename='vitaminai.jpg') }}" alt="Vitaminų logotipas" style="max-width: 360px; height: auto; display: block; margin: 0 auto;">
    </div>

    <h2>Įvesk simptomus:</h2>
    <form method="POST" id="recommendationForm">
      <label for="age">Amžius:</label>
      <select name="age" id="age">
        <option disabled {% if not age %}selected{% endif %}>Pasirinkite amžių</option>
        <option value="child" {% if age == "child" %}selected{% endif %}>Vaikas</option>
        <option value="adult" {% if age == "adult" %}selected{% endif %}>Suaugęs</option>
        <option value="senior" {% if age == "senior" %}selected{% endif %}>Senjoras</option>
      </select>

      <label for="gender">Lytis:</label>
      <select name="gender" id="gender">
        <option disabled {% if not gender %}selected{% endif %}>Pasirinkite lytį</option>
        <option value="male" {% if gender == "male" %}selected{% endif %}>Vyras</option>
        <option value="female" {% if gender == "female" %}selected{% endif %}>Moteris</option>
        <option value="other" {% if gender == "other" %}selected{% endif %}>Kita</option>
      </select>

      <label for="lifestyle">Gyvenimo būdas:</label>
      <select name="lifestyle" id="lifestyle">
        <option disabled {% if not lifestyle %}selected{% endif %}>Pasirinkite</option>
        <option value="active" {% if lifestyle == "active" %}selected{% endif %}>Aktyvus</option>
        <option value="sedentary" {% if lifestyle == "sedentary" %}selected{% endif %}>Sėslus</option>
        <option value="average" {% if lifestyle == "average" %}selected{% endif %}>Vidutinis</option>
      </select>

      <textarea name="symptoms" id="symptoms" rows="6" placeholder="Aprašyk simptomus...">{{ symptoms }}</textarea>
      <button type="submit" id="submitBtn" disabled>Gauti rekomendacijas</button>
    </form>

    {% if result %}
      <h3>Rekomendacijos:</h3>
      <div class="result-box">{{ result }}</div>
      <form method="POST" action="/download" target="_blank">
        <input type="hidden" name="pdf_content" value="{{ result }}">
        <button type="submit">Atsisiųsti PDF</button>
      </form>
    {% endif %}
  </div>

  <script>
    const age = document.getElementById('age');
    const gender = document.getElementById('gender');
    const lifestyle = document.getElementById('lifestyle');
    const symptoms = document.getElementById('symptoms');
    const submitBtn = document.getElementById('submitBtn');

    function checkFormValidity() {
      const isValid = age.value && gender.value && lifestyle.value && symptoms.value.trim().length > 0;
      submitBtn.disabled = !isValid;
    }

    age.addEventListener('change', checkFormValidity);
    gender.addEventListener('change', checkFormValidity);
    lifestyle.addEventListener('change', checkFormValidity);
    symptoms.addEventListener('input', checkFormValidity);
  </script>
</body>
</html>
"""




@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    symptoms = ""
    age = ""
    gender = ""
    lifestyle = ""

    if request.method == "POST":
        symptoms = request.form.get("symptoms", "")
        age = request.form.get("age", "")
        gender = request.form.get("gender", "")
        lifestyle = request.form.get("lifestyle", "")

        if symptoms.strip():
            age_text = {"child": "Vaikas", "adult": "Suaugęs", "senior": "Senjoras"}.get(age, "")
            gender_text = {"male": "Vyras", "female": "Moteris", "other": "Kita"}.get(gender, "")
            lifestyle_text = {"active": "Aktyvus", "sedentary": "Sėslus", "average": "Vidutinis"}.get(lifestyle, "")

            prompt = (
                f"Pateik sąrašą ir trumpai, kodėl ir kokio vitamino žmogui galimai trūksta, keliais punktais, "
                f"nereikia apibendrinimo, tik punktai.\n"
                f"Jei simptomai nesusiję su vitaminų trūkumu arba užklausa nesąmoninga, atsakyk tik: 'Bandykite iš naujo'.\n"
                f"Paciento amžius: {age_text}.\n"
                f"Lytis: {gender_text}.\n"
                f"Gyvenimo būdas: {lifestyle_text}.\n"
                f"Simptomai: {symptoms}."
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=prompt,
            )
            result = response.text

    return render_template_string(HTML, result=result, symptoms=symptoms,
                                  age=age, gender=gender, lifestyle=lifestyle)



@app.route("/download", methods=["POST"])
def download_pdf():
    result = request.form.get("pdf_content", "")
    if not result.strip():
        return "Nėra duomenų", 400

    buffer = BytesIO()

    pdfmetrics.registerFont(TTFont("DejaVu", os.path.join("fonts", "DejaVuSans.ttf")))

    p = canvas.Canvas(buffer, pagesize=A4)
    p.setFont("DejaVu", 12)

    width, height = A4
    margin_left = 50
    margin_top = 50
    line_height = 15
    max_width = width - 2 * margin_left
    y = height - margin_top

    for paragraph in result.split('\n'):
        lines = simpleSplit(paragraph, "DejaVu", 12, max_width)
        for line in lines:
            if y < margin_top:
                p.showPage()
                p.setFont("DejaVu", 12)
                y = height - margin_top
            p.drawString(margin_left, y, line)
            y -= line_height

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="rekomendacijos.pdf",
        mimetype="application/pdf"
    )






if __name__ == "__main__":
    app.run(debug=True)
