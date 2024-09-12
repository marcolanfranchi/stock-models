## stock-models

this repo will hold different ML models created for predicting prices of different stocks. I also plan to create a UI to visualize the models' performance against the actual stock data. 

### hosted project
[here](https://github.com/marcolanfranchi/stock-models)

### setup

clone the repo
```bash
git clone https://github.com/marcolanfranchi/stock-models.git
```
 navigate to root directory
```bash
cd stock-models
```

create a virtual environment for packages
```bash
python -m venv venv
```

activate the virtual environment
```bash
source venv/bin/activate
```

install required packages
```bash
pip install -r 'requirements.txt'
```

run the ui
```bash
streamlit run ui/app.py
```

