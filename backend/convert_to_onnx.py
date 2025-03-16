import pickle
import os
import json
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

def convert_model(model_name):
    # Load the original model
    model_dir = os.path.join('models', model_name)
    with open(os.path.join(model_dir, 'latest_version.txt'), 'r') as f:
        version = f.read().strip()
    
    with open(os.path.join(model_dir, f'model_{version}.pkl'), 'rb') as f:
        model = pickle.load(f)
    
    with open(os.path.join(model_dir, 'model_meta.json'), 'r') as f:
        metadata = json.load(f)
    
    # Get number of features
    n_features = len(metadata['feature_names'])
    
    # Convert to ONNX
    initial_type = [('float_input', FloatTensorType([None, n_features]))]
    onx = convert_sklearn(model, initial_types=initial_type)
    
    # Save ONNX model
    with open(os.path.join(model_dir, 'model.onnx'), 'wb') as f:
        f.write(onx.SerializeToString())

if __name__ == '__main__':
    # Convert both models
    convert_model('feels')
    convert_model('clothing') 