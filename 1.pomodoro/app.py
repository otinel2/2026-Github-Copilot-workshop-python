"""Application entry point for the Pomodoro web app."""

from pomodoro import create_app


app = create_app()


if __name__ == "__main__":
	app.run(debug=True)
