The Flask application should display a web page that includes the following elements:

1. A title, "Hello World"
2. A paragraph with some text.
3. An input field for users to enter their names.
4. A button labeled "Submit".
5. A heading element to display a personalized greeting once the user enters their name and clicks the submit button.

The server should be accessible at `localhost:5000`. You can use HTML templates or render functions directly in your Flask route.

Here's an example of how you might structure the Flask application:

```python
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def hello():
    greeting = "Hello World"
    text = "Welcome to our simple user interface."
    name = ""

    if request.method == 'POST':
        name = request.form['name']
        greeting = f"Hello {name}!"

    return render_template('index.html', greeting=greeting, text=text, name=name)

if __name__ == '__main__':
    app.run(debug=True)
```

Create an `index.html` file in a folder named `templates`. This HTML file will contain the structure of your web page. Make sure to use Jinja2 templating syntax in your HTML to render the variables passed from your Flask route.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Simple User Interface</title>
</head>
<body>
    <h1>{{ greeting }}</h1>
    <p>{{ text }}</p>
    <form method="post">
        <input type="text" name="name" placeholder="Enter your name">
        <button type="submit">Submit</button>
    </form>
    {% if name %}
        <h2>{{ greeting }} {{ name }}!</h2>
    {% endif %}
</body>
</html>
```

This solution provides a basic Flask server and an HTML template that meets the requirements specified in the question. The server runs on `localhost:5000` and displays a web page with the requested elements, including a personalized greeting based on user input.