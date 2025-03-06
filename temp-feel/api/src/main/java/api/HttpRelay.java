
package api;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Map;

public class HttpRelay {
    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();
            
    private static final ObjectMapper JSON_MAPPER = new ObjectMapper();
    
    private final String baseUrl;
    
    public HttpRelay(String baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    public Map<String, Object> predict(String endpoint, Map<String, Object> data) throws IOException, InterruptedException {
        // Create the request body
        ObjectNode requestBody = JSON_MAPPER.createObjectNode();
        ArrayNode instances = requestBody.putArray("instances");
        ObjectNode instance = instances.addObject();
        
        // Add all data fields to the instance
        for (Map.Entry<String, Object> entry : data.entrySet()) {
            String key = entry.getKey();
            Object value = entry.getValue();
            
            if (value instanceof Integer) {
                instance.put(key, (Integer) value);
            } else if (value instanceof Double) {
                instance.put(key, (Double) value);
            } else if (value instanceof Boolean) {
                instance.put(key, (Boolean) value);
            } else {
                instance.put(key, String.valueOf(value));
            }
        }
        
        // Convert to JSON string
        String requestJson = JSON_MAPPER.writeValueAsString(requestBody);
        
        // Build HTTP request
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + endpoint))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestJson))
                .build();
        
        // Send request and get response
        HttpResponse<String> response = HTTP_CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
        
        // Check response status
        if (response.statusCode() != 200) {
            throw new IOException("API request failed with status code: " + response.statusCode() + 
                                 ", body: " + response.body());
        }
        
        // Parse response
        @SuppressWarnings("unchecked")
        Map<String, Object> result = JSON_MAPPER.readValue(response.body(), Map.class);
        return result;
    }
}