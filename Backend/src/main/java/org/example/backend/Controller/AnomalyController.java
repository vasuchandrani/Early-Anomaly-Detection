package org.example.backend.controller;

import org.example.backend.model.AnomalyEntity;
import org.example.backend.repository.AnomalyRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/anomalies")
public class AnomalyController {

    private final AnomalyRepository anomalyRepository;

    public AnomalyController(AnomalyRepository anomalyRepository) {
        this.anomalyRepository = anomalyRepository;
    }

    @GetMapping
    public ResponseEntity<List<AnomalyEntity>> getAllAnomalies() {
        return ResponseEntity.ok(anomalyRepository.findAll());
    }

    @GetMapping("/{userId}")
    public ResponseEntity<List<AnomalyEntity>> getByUser(@PathVariable String userId) {
        return ResponseEntity.ok(anomalyRepository.findByUserId(userId));
    }
}