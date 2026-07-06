from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    name = request.form["name"]
    attendance = int(request.form["attendance"])
    marks = int(request.form["marks"])

    if attendance < 75 or marks < 40:
        prediction = "High Risk of Dropout"
    elif attendance < 85:
        prediction = "Medium Risk"
    else:
        prediction = "Low Risk"

    return render_template(
        "result.html",
        name=name,
        attendance=attendance,
        marks=marks,
        prediction=prediction
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)