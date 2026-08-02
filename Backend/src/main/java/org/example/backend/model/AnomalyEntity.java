package org.example.backend.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "anomalies")
public class AnomalyEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id")
    private String userId;

    @Column(name = "anomaly_type")
    private String anomalyType;

    @Column(name = "anomaly_score")
    private Double anomalyScore;

    @Column(name = "ratio_inflow_outflow")
    private Double ratioInflowOutflow;

    @Column(name = "emi_to_income_ratio")
    private Double emiToIncomeRatio;

    @Column(name = "amb_drop_percentage")
    private Double ambDropPercentage;

    @Column(name = "transaction_count")
    private Integer transactionCount;

    @Column(name = "detected_at")
    private LocalDateTime detectedAt;

    public AnomalyEntity() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getAnomalyType() { return anomalyType; }
    public void setAnomalyType(String anomalyType) { this.anomalyType = anomalyType; }

    public Double getAnomalyScore() { return anomalyScore; }
    public void setAnomalyScore(Double anomalyScore) { this.anomalyScore = anomalyScore; }

    public Double getRatioInflowOutflow() { return ratioInflowOutflow; }
    public void setRatioInflowOutflow(Double ratioInflowOutflow) { this.ratioInflowOutflow = ratioInflowOutflow; }

    public Double getEmiToIncomeRatio() { return emiToIncomeRatio; }
    public void setEmiToIncomeRatio(Double emiToIncomeRatio) { this.emiToIncomeRatio = emiToIncomeRatio; }

    public Double getAmbDropPercentage() { return ambDropPercentage; }
    public void setAmbDropPercentage(Double ambDropPercentage) { this.ambDropPercentage = ambDropPercentage; }

    public Integer getTransactionCount() { return transactionCount; }
    public void setTransactionCount(Integer transactionCount) { this.transactionCount = transactionCount; }

    public LocalDateTime getDetectedAt() { return detectedAt; }
    public void setDetectedAt(LocalDateTime detectedAt) { this.detectedAt = detectedAt; }
}