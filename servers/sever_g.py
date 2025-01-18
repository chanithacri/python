import os
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def list_html_files():
    # Directory containing HTML files
    html_dir = 'html_files/'

    # Get a list of all HTML files in the directory
    html_files = [file for file in os.listdir(html_dir) if file.endswith('.html')]

    # Initialize a list to store titles
    titles = []

    # Extract titles from HTML files
    for file_name in html_files:
        with open(os.path.join(html_dir, file_name), 'r', encoding='utf-8') as file:
            content = file.read()
            # Find the title tag and extract its content
            start_index = content.find('<title>') + len('<title>')
            end_index = content.find('</title>', start_index)
            title = content[start_index:end_index].strip()
            titles.append((file_name, title))

    # Render the HTML template with the list of titles
    return render_template_string('''
<h1>List of HTML Files</h1>
<ul>
{% for file_name, title in titles %}
<li><a href="/{{ file_name }}">{{ title }}</a></li>
{% endfor %}
</ul>
''', titles=titles)

@app.route('/<file_name>')
def display_html_file(file_name):
    # Directory containing HTML files
    html_dir = 'html_files/'

    # Read the content of the requested HTML file
    with open(os.path.join(html_dir, file_name), 'r', encoding='utf-8') as file:
        content = file.read()

    # Return the content as a response
    return content

if __name__ == '__main__':
    app.run(debug=True)
    