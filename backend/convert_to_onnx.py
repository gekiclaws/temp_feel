import pickle
import os
import json
import onnx
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

    # Ensure the ONNX model is using IR version 9
    onnx_model = onnx.load_model_from_string(onx.SerializeToString())
    onnx_model.ir_version = 9  # Set IR version to 9
    onnx.checker.check_model(onnx_model)

    # Save ONNX model
    output_path = os.path.join(model_dir, 'model.onnx')
    with open(output_path, 'wb') as f:
        f.write(onnx_model.SerializeToString())

    print(f"Successfully converted {model_name} model to ONNX with IR version 9.")

if __name__ == '__main__':
    # Convert both models
    convert_model('feels')
    convert_model('clothing')
