from flask import Flask, render_template, request, send_file
from gemini_api import get_recommendation
from pdf_generator import generate_pdf

app = Flask(__name__)

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

            result = get_recommendation(prompt)

    return render_template("form.html", result=result, symptoms=symptoms,
                           age=age, gender=gender, lifestyle=lifestyle)


@app.route("/download", methods=["POST"])
def download_pdf():
    content = request.form.get("pdf_content", "")
    if not content.strip():
        return "Nėra duomenų", 400

    pdf_buffer = generate_pdf(content)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="rekomendacijos.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)
