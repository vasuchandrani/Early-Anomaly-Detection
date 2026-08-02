package org.example.backend.consumer;

import org.example.backend.model.AnomalyEntity;
import org.example.backend.model.AnomalyResult;
import org.example.backend.Repository.AnomalyRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class AnomalyConsumer {

    private static final Logger log = LoggerFactory.getLogger(AnomalyConsumer.class);
    private final AnomalyRepository anomalyRepository;

    public AnomalyConsumer(AnomalyRepository anomalyRepository) {
        this.anomalyRepository = anomalyRepository;
    }

    @KafkaListener(topics = "anomalies", groupId = "java-anomaly-writer")
    public void consume(AnomalyResult result) {
        log.info("Received anomaly result for userId={} type={}",
                result.getUserId(), result.getAnomalyType());

        AnomalyEntity entity = new AnomalyEntity();
        entity.setUserId(result.getUserId());
        entity.setAnomalyType(result.getAnomalyType());
        entity.setAnomalyScore(result.getAnomalyScore());
        entity.setRatioInflowOutflow(result.getRatioInflowOutflow());
        entity.setEmiToIncomeRatio(result.getEmiToIncomeRatio());
        entity.setAmbDropPercentage(result.getAmbDropPercentage());
        entity.setTransactionCount(result.getTransactionCount());
        entity.setDetectedAt(LocalDateTime.now());

        anomalyRepository.save(entity);
        log.info("Anomaly saved to PostgreSQL for userId={}", result.getUserId());
    }
}