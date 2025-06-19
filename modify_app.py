import re

def remove_babel_from_app_py(content):
    # Remove Babel imports
    content = re.sub(r"from flask_babel import Babel, _(, get_locale)?\n", "", content)

    # Remove Babel initialization and config
    content = re.sub(r"babel = Babel\(\)\s*\n", "", content)
    content = re.sub(r"app\.config\['LANGUAGES'\] = .*\n", "", content)
    content = re.sub(r"app\.config\['BABEL_DEFAULT_LOCALE'\] = .*\n", "", content)
    content = re.sub(r"app\.config\['BABEL_TRANSLATION_DIRECTORIES'\] = .*\n", "", content)
    content = re.sub(r"babel\.init_app\(app\)\s*\n", "", content)

    # Remove get_locale_func
    content = re.sub(r"# @babel.localeselector[^\n]*\n# def get_locale_func\(\):\n(# .*\n)*#     return app.config\['BABEL_DEFAULT_LOCALE'\] # Fallback\n", "", content, flags=re.MULTILINE)

    # Remove _() calls
    # Simple cases: _('Text') or _("Text")
    # This regex aims to match _("string") or _('string') including escaped quotes within the string
    content = re.sub(r"_\((\s*['\"])(.*?)(\1)\)", r"\1\2\3", content) # Keep the quotes
    # f-string cases: _(f"text {var}") or _(f'text {var}')
    content = re.sub(r"_\(f((\"\"\"(?:.|\n)*?\"\"\")|(\"(?:\\"|[^\"])*\")|('''(?:.|\n)*?''')|('(?:\\'|[^'])*'))\)", r"f\1", content)

    # Remove /api/translations endpoint
    content = re.sub(r"@app\.route\('/api/translations'\)\s*\ndef get_translations\(\):\s*(\n\s*#.*\s*)*\n\s*translations = \{\s*([\s\S]*?)\s*}\s*return jsonify\(translations\)\n", "", content, flags=re.MULTILINE)

    return content

file_path = "app.py"
with open(file_path, 'r') as f:
    original_content = f.read()

modified_content = remove_babel_from_app_py(original_content)

with open(file_path, 'w') as f:
    f.write(modified_content)

print(f"Modified {file_path} to remove Flask-Babel components.")

# Modify mikrotik_userman_dashboard.html
html_file_path = "mikrotik_userman_dashboard.html"
with open(html_file_path, 'r') as f:
    html_content = f.read()

# Remove {{ _('...') }}
html_content = re.sub(r"\{\{\s*_\(['\"](.*?)['\"]\)\s*\}\}", r"\1", html_content)
# Remove data-translate attributes
html_content = re.sub(r'\s*data-translate="_js"', '', html_content)
# Remove the _js function and its calls from script tag in dashboard
html_content = re.sub(r"window\.i18n = {};\s*\n\s*// Translation function\s*function _js\(key, \.\.\.args\) {[^}]*}\n", "", html_content, flags=re.DOTALL)
# Simpler regex for _js, assuming it's always _js('string literal', optional_args)
html_content = re.sub(r"_js\((['\"])(.*?)\1(?:,\s*([^)]+))?\)", lambda m: f"" if m.group(3) else f"'{m.group(2)}'", html_content)


with open(html_file_path, 'w') as f:
    f.write(html_content)
print(f"Modified {html_file_path} to remove Jinja2 translation calls and JS localization.")

# Modify login.html
login_html_path = "login.html"
with open(login_html_path, 'r') as f:
    login_content = f.read()

login_content = re.sub(r"\{\{\s*_\(['\"](.*?)['\"]\)\s*\}\}", r"\1", login_content)
login_content = re.sub(r'\s*data-translate="_js"', '', login_content)
# Simpler regex for _js, assuming it's always _js('string literal', optional_args)
login_content = re.sub(r"_js\((['\"])(.*?)(\1)(?:,\s*([^)]+))?\)", lambda m: f"" if m.group(3) else f"'{m.group(2)}'", login_content)


with open(login_html_path, 'w') as f:
    f.write(login_content)
print(f"Modified {login_html_path} to remove Jinja2 translation calls and JS localization.")


# Modify requirements.txt
requirements_path = "requirements.txt"
with open(requirements_path, 'r') as f:
    lines = f.readlines()

with open(requirements_path, 'w') as f:
    for line in lines:
        if "Flask-Babel" not in line:
            f.write(line)
print(f"Removed Flask-Babel from {requirements_path}")
