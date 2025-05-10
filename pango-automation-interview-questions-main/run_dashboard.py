from automation_framework.dashboard.app import app

if __name__ == '__main__':
    print("Starting Weather Data Analysis Dashboard...")
    print("Open your browser and navigate to http://127.0.0.1:8050/")
    app.run(debug=True) 