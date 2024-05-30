# ml/predict.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from models import db, Inventory

def predict_inventory(user_id):
    items = Inventory.query.filter_by(user_id=user_id).all()
    if not items:
        return []

    data = pd.DataFrame([(item.item_name, item.quantity) for item in items], columns=['item_name', 'quantity'])

    # Simple prediction model
    model = LinearRegression()
    data['id'] = data.index
    model.fit(data[['id']], data['quantity'])

    predictions = model.predict(data[['id']])

    return [{'item_name': item.item_name, 'predicted_quantity': int(pred)} for item, pred in zip(items, predictions)]
