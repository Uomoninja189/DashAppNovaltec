from app import app
import callback


server = app.server  # questo è l'oggetto che Gunicorn vuole

if __name__ == "__main__":
    app.run(debug=True)
