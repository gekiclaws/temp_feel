package services;

import org.jpmml.evaluator.*;
import org.dmg.pmml.FieldName;
import org.dmg.pmml.PMML;

import java.io.File;
import java.io.FileInputStream;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class FeelsPredictor {
    private Evaluator evaluator;
    
    public FeelsPredictor(String pmmlFilePath) throws Exception {
        // Load the PMML model
        PMML pmml = org.jpmml.model.PMMLUtil.unmarshal(new FileInputStream(new File(pmmlFilePath)));
        
        // Create a model evaluator
        ModelEvaluatorFactory modelEvaluatorFactory = ModelEvaluatorFactory.newInstance();
        evaluator = modelEvaluatorFactory.newModelEvaluator(pmml);
    }
    
    public Map<String, Object> predict(double uprClo, double lwrClo, int temp, 
                                     int sun, int headwind, int snow, int rain, 
                                     int fatigued, int hr) {
        
        // Create input parameters
        Map<FieldName, FieldValue> arguments = new LinkedHashMap<>();
        arguments.put(FieldName.create("upr_clo"), FieldValueUtil.create(uprClo));
        arguments.put(FieldName.create("lwr_clo"), FieldValueUtil.create(lwrClo));
        arguments.put(FieldName.create("temp"), FieldValueUtil.create(temp));
        arguments.put(FieldName.create("sun"), FieldValueUtil.create(sun));
        arguments.put(FieldName.create("headwind"), FieldValueUtil.create(headwind));
        arguments.put(FieldName.create("snow"), FieldValueUtil.create(snow));
        arguments.put(FieldName.create("rain"), FieldValueUtil.create(rain));
        arguments.put(FieldName.create("fatigued"), FieldValueUtil.create(fatigued));
        arguments.put(FieldName.create("hr"), FieldValueUtil.create(hr));
        
        // Evaluate
        Map<FieldName, ?> results = evaluator.evaluate(arguments);
        
        // Process results
        Map<String, Object> resultMap = new HashMap<>();
        
        // Get the predicted value
        ProbabilityDistribution targetValue = (ProbabilityDistribution)results.get(evaluator.getTargetField());
        resultMap.put("prediction", targetValue.getResult());
        
        // Translate the predicted value
        String[] feelCategories = {"cold", "cool", "warm", "hot"};
        int predictionValue = Integer.parseInt(targetValue.getResult().toString());
        if (predictionValue >= 0 && predictionValue < feelCategories.length) {
            resultMap.put("category", feelCategories[predictionValue]);
        }
        
        // Get the probability distribution
        Map<String, Double> probabilities = new HashMap<>();
        for (int i = 0; i < feelCategories.length; i++) {
            Double probability = targetValue.getProbability(String.valueOf(i));
            if (probability != null) {
                probabilities.put(feelCategories[i], probability);
            }
        }
        resultMap.put("probabilities", probabilities);
        
        return resultMap;
    }
    
    // Example usage
    public static void main(String[] args) {
        try {
            FeelsPredictor predictor = new FeelsPredictor("model/random_forest_feels.pmml");
            Map<String, Object> result = predictor.predict(0.5, 0.5, -5, 1, 0, 0, 0, 0, 120);
            
            System.out.println("Prediction: " + result.get("prediction"));
            System.out.println("Category: " + result.get("category"));
            System.out.println("Probabilities: " + result.get("probabilities"));
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}