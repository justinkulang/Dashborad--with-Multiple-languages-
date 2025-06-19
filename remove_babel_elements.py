import re
import os
import shutil

def clean_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove {{ _('...') }} Jinja2 calls
    content = re.sub(r"\{\{\s*_\((['\"])(.*?)(\1)\)\s*\}\}", r"\2", content)
    # Remove data-translate="_js" attributes
    content = re.sub(r'\s*data-translate="_js"', '', content)

    # Remove the _js function definition and its call structure
    # First, remove the function definition itself
    content = re.sub(r"window\.i18n\s*=\s*\{.*?\}\s*;\s*\n+\s*// Translation function\s*function _js\(key, \.\.\.args\) \{[\s\S]*?return translated;\s*}\n", "", content, flags=re.DOTALL | re.MULTILINE)

    # Then, replace calls like _js('key', var1, var2) with formatted strings or simple strings
    # This needs to be done carefully. A simpler approach for now is to replace with the key itself,
    # and handle placeholders manually if they were common.
    # For _js('Some text {0} and {1}', var1, var2) ->
    # For _js('Some text') -> 'Some text'

    # Simpler replacement: _js('key') -> 'key'
    content = re.sub(r"_js\((['\"])([^'{}\"]*?)\1\)", r"'\2'", content)
    # For _js('key {0}', var) ->  (approximate)
    content = re.sub(r"_js\((['\"])([^'{}\"]*?)\{0\}([^'{}\"]*?)\1,\s*([^)]+?)\)", r"", content)
    # For _js('key {0} other {1}', var1, var2) ->
    content = re.sub(r"_js\((['\"])([^'{}\"]*?)\{0\}([^'{}\"]*?)\{1\}([^'{}\"]*?)\1,\s*([^,]+?),\s*([^)]+?)\)", r"", content)


    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Processed {filepath} for Babel removal.")

# Process HTML files
html_files = ["login.html", "templates/mikrotik_userman_dashboard.html"]
for f_path in html_files:
    if os.path.exists(f_path):
        clean_html_file(f_path)
    else:
        print(f"Warning: {f_path} not found.")

# Modify app.py
app_py_path = "app.py"
if os.path.exists(app_py_path):
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove Babel imports
    content = re.sub(r"from flask_babel import Babel, _(, get_locale)?\s*", "", content)
    content = re.sub(r"from flask_babel import gettext\s*", "", content) # Handle if gettext was imported separately

    # Remove Babel initialization and config
    content = re.sub(r"babel = Babel\(\)\s*\n?", "", content)
    content = re.sub(r"app\.config\['LANGUAGES'\] = .*\n", "", content)
    content = re.sub(r"app\.config\['BABEL_DEFAULT_LOCALE'\] = .*\n", "", content)
    content = re.sub(r"app\.config\['BABEL_TRANSLATION_DIRECTORIES'\] = .*\n", "", content)
    content = re.sub(r"babel\.init_app\(app\)\s*\n", "", content)

    # Remove get_locale_func
    content = re.sub(r"# @babel.localeselector[^\n]*\n# def get_locale_func\(\):\s*(\n\s*#.*\s*)*(\n\s*if request:.*)?(\n\s*return app.config\['BABEL_DEFAULT_LOCALE'\] # Fallback)?\n", "", content, flags=re.MULTILINE)

    # Remove _() calls from Python code
    content = re.sub(r"_\((r?\"(?:\\"|[^\"])*\"|r?'(?:\\'|[^'])*')\)", r"\1", content) # For simple strings
    content = re.sub(r"_\(f((\"\"\"(?:.|\n)*?\"\"\")|(\"(?:\\"|[^\"])*\")|('''(?:.|\n)*?''')|('(?:\\'|[^'])*'))\)", r"f\1", content) # For f-strings
    # Remove gettext() calls
    content = re.sub(r"gettext\((r?\"(?:\\"|[^\"])*\"|r?'(?:\\'|[^'])*')\)", r"\1", content)
    content = re.sub(r"gettext\(f((\"\"\"(?:.|\n)*?\"\"\")|(\"(?:\\"|[^\"])*\")|('''(?:.|\n)*?''')|('(?:\\'|[^'])*'))\)", r"f\1", content)


    # Remove /api/translations endpoint
    content = re.sub(r"@app\.route\('/api/translations'\)\s*\ndef get_translations\(\):\s*(\n\s*#.*\s*)*\n\s*translations = \{\s*([\s\S]*?)\s*}\s*return jsonify\(translations\)\n", "", content, flags=re.MULTILINE)

    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Modified {app_py_path} to remove Flask-Babel components.")
else:
    print(f"Warning: {app_py_path} not found.")

# Modify requirements.txt
requirements_path = "requirements.txt"
if os.path.exists(requirements_path):
    with open(requirements_path, 'r') as f:
        lines = f.readlines()
    with open(requirements_path, 'w') as f:
        for line in lines:
            if "Flask-Babel" not in line and "babel" not in line.lower(): # More robust check
                f.write(line)
    print(f"Removed Flask-Babel from {requirements_path}")
else:
    print(f"Warning: {requirements_path} not found.")

# Delete babel.cfg
babel_cfg_path = "babel.cfg"
if os.path.exists(babel_cfg_path):
    os.remove(babel_cfg_path)
    print(f"Deleted {babel_cfg_path}")
else:
    print(f"Warning: {babel_cfg_path} not found.")

# Delete translations directory
translations_dir = "translations"
if os.path.exists(translations_dir):
    shutil.rmtree(translations_dir)
    print(f"Deleted directory {translations_dir}")
else:
    print(f"Warning: {translations_dir} directory not found.")

print("Flask-Babel removal process completed.")
