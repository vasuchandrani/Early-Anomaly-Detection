package org.example.backend.Controller;

import jakarta.validation.Valid;
import org.example.backend.model.WebHookPayload;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/webhook")
public class WebhookController {

    private static final Logger log = LoggerFactory.getLogger(WebhookController.class);
    private static final String TOPIC = "transactions";

    private final KafkaTemplate<String, WebHookPayload> kafkaTemplate;

    public WebhookController(KafkaTemplate<String, WebHookPayload> kafkaTemplate) {
        this.kafkaTemplate = kafkaTemplate;
    }

    @PostMapping("/aa-fetch")
    public ResponseEntity<Map<String, Object>> receiveWebhook(
            @Valid @RequestBody WebHookPayload payload) {

        log.info("Received webhook for userId={} with {} transactions",
                payload.getUserId(), payload.getTransactions().size());

        kafkaTemplate.send(TOPIC, payload.getUserId(), payload);

        log.info("Pushed to Kafka topic '{}' for userId={}", TOPIC, payload.getUserId());

        return ResponseEntity.ok(Map.of(
                "status", "queued",
                "userId", payload.getUserId(),
                "transactionCount", payload.getTransactions().size()
        ));
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of("status", "UP"));
    }
}