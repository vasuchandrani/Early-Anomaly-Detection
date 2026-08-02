package org.example.backend.model;

public class AnomalyResult {
    private String userId;
    private String anomalyType;
    private Double anomalyScore;
    private Double ratioInflowOutflow;
    private Double emiToIncomeRatio;
    private Double ambDropPercentage;
    private Integer transactionCount;
    private String detectedAt;

    public AnomalyResult() {}

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

    public String getDetectedAt() { return detectedAt; }
    public void setDetectedAt(String detectedAt) { this.detectedAt = detectedAt; }
}