#!/bin/bash
cd "$(dirname "$0")"
if [ -d ".venv" ]; then source .venv/bin/activate; fi
python train_model.py
streamlit run app.py
