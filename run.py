from app import create_app
from app.models.load_default_model import print_all_debug

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print_all_debug()
    app.run(debug=True)

    