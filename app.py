import os
import markdown
import json
import threading

from flask import Flask, request, render_template, redirect, url_for, flash, session
from markupsafe import Markup
from flask_wtf.csrf import CSRFProtect, generate_csrf


app = Flask(__name__)

app.config["AUTH_TOKEN"] = os.environ.get("HELPER_AUTH_TOKEN")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["FORM_FIELDS"] = os.environ.get("FORM_FIELDS")
app.config["TEXTAREA_FIELDS"] = os.environ.get("TEXTAREA_FORM_FIELDS")

csrf = CSRFProtect(app)

secret_output_file = "/run/secrets/output"


def shutdown():
    print("Shutting down...")
    os._exit(0)


def check_output_file():
    if (
        not os.path.exists("/run/secrets/output")
        or os.path.getsize("/run/secrets/output") == 0
    ):
        start_shutdown_watch()
    else:
        shutdown()


def start_shutdown_watch():
    timer = threading.Timer(5, check_output_file)
    timer.start()


@app.route("/helper", methods=["GET", "POST"])
def index():
    display_content = ""

    if "logged_in" in session and session["logged_in"]:
        if session["token"] != app.config["AUTH_TOKEN"]:
            return redirect(url_for("unauthorized"))

        token = app.config["AUTH_TOKEN"]
    else:
        token = request.args.get("token")
        if token is None:
            return redirect(url_for("unauthorized"))

        # Check if the provided token matches the AUTH_TOKEN
        if token == app.config["AUTH_TOKEN"]:
            # If the token matches, set the session variable to log the user in
            session["logged_in"] = True
            session["token"] = token
        else:
            return redirect(url_for("unauthorized"))

    if request.method == "POST":
        form_data = {}
        form_fields = get_form_keys_by_type()
        for form_field_type in form_fields.keys():
            for field in form_fields[form_field_type]:
                form_data[field] = request.form.get(field)

        output_body = {"type": "opaque", "data": form_data}
        output_json = json.dumps({"secrets": {"output": output_body}})

        try:
            # Write the output to the specified file
            with open("/run/secrets/output", "w") as output_file:
                output_file.write(output_json + "\n")
            start_shutdown_watch()
            return redirect(url_for("success_page"))

        except Exception as e:
            error_message = f"Error writing output to file: {str(e)}"
            flash(error_message, "error")

    try:
        with open("/acorn/instructions.txt", "r") as file:
            markdown_content = file.read()
            display_content = Markup(markdown.markdown(markdown_content))
    except FileNotFoundError:
        flash("Instructions information not found.", "error")

    csrf = generate_csrf()
    form = get_form_keys_by_type()

    return render_template(
        "main_page.html",
        fields=form,
        display_content=display_content,
        csrf_token=csrf,
    )


@app.route("/success")
def success_page():
    return render_template("success_page.html")


@app.route("/unauthorized")
def unauthorized():
    return render_template("unauthorized_page.html")


def get_form_keys_by_type():
    form = {}

    text_field_list = app.config["FORM_FIELDS"].split(",")
    textarea_field_list = app.config["TEXTAREA_FIELDS"].split(",")

    if text_field_list != [""]:
        form["text_fields"] = text_field_list
    if textarea_field_list != [""]:
        form["textarea_fields"] = textarea_field_list

    return form
